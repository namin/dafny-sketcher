from dataclasses import dataclass
from typing import Optional
import pathlib
import tempfile

from montecarlo.node import Node
from montecarlo.montecarlo import MonteCarlo

from llm import default_generate as generate
import driver
import sketcher
from fine import format_errors
from driver import prompt_begin_dafny, extract_dafny_program
from bench_feedback import prompt_lemma_implementer
from dafny_poetry.dafny_io import run_dafny_admitter, count_admits, collect_first_admit_context, replace_method_body
from dafny_poetry import poetry_recursive
from dafny_poetry.poetry_recursive import expand_node, PoetryConfig
from dafny_poetry.proof_tree import ProofNode
from dafny_poetry.utils import extract_method_body_text
import os

# Override STRUCTURE_DELTA_MAX for more permissive admit growth in MCTS exploration
poetry_recursive.STRUCTURE_DELTA_MAX = 4

USE_SKETCHERS = os.environ.get('USE_SKETCHERS', 'true').lower() != 'false'
USE_LLM = os.environ.get('USE_LLM', 'false').lower() != 'false'
SERVER = os.environ.get('DAFNY_ANNOTATOR_SERVER')
SKETCH_SERVER = os.environ.get('SKETCH_DAFNY_ANNOTATOR_SERVER')
if SERVER is not None:
    print('CONFIG: using oracle')
    import annotator
    oracle = annotator.annotate
else:
    print('CONFIG: NOT using oracle')
    oracle = None
if SKETCH_SERVER is not None:
    print('CONFIG: using sketch oracle')
    import annotator
    sketch_oracle = annotator.sketch
else:
    print('CONFIG: NOT using sketch oracle')
    sketch_oracle = None

@dataclass
class State:
    initial_program: str
    lemma: object
    body: str
    admits: int = 0  # Track number of admits
    file_path: Optional[pathlib.Path] = None  # For admitter workflow

def add_standard_node(node, body, admits):
    child = Node(State(node.state.initial_program, node.state.lemma, body, admits))
    node.add_child(child)
    # Reward based on admit reduction
    admit_reduction = node.state.admits - admits
    reward = 1 + (admit_reduction * 0.5)  # Bonus for reducing admits
    child.update_win_value(reward)
    child.update_policy_value(1)

    child = Node(node.state)
    node.add_child(child)
    child.update_policy_value(0.2)

def child_finder(node, montecarlo):
    init_p = node.state.initial_program
    lemma = node.state.lemma
    name = lemma['name']
    x = node.state.body
    p = driver.insert_program_todo(lemma, init_p, x)
    
    print(f"[child_finder] Exploring node with {node.state.admits} admits")
    
    # Create temporary directory for poetry processing
    with tempfile.TemporaryDirectory(prefix=f"mcts_{name}_") as tmpdir:
        out_dir = pathlib.Path(tmpdir)
        
        # Write current program to file
        prog_file = out_dir / "current.dfy"
        prog_file.write_text(p, encoding="utf-8")
        
        # Run admitter to get initial patched version with admits
        try:
            patched_path = run_dafny_admitter(prog_file, mode="admit", timeout=30)
            admits_count = count_admits(patched_path)
            
            # If solved (0 admits), extract body from patched file
            if admits_count == 0:
                print(f"[child_finder] *** Found state with 0 admits after admitter! ***")
                patched_text = patched_path.read_text(encoding="utf-8")
                solved_body = extract_method_body_text(patched_text, name)
                if solved_body:
                    print(f"[child_finder] *** Setting montecarlo.solution (from patched state) ***")
                    print(f"Solution body: {solved_body[:100]}...")
                    montecarlo.solution = solved_body
                    return
                # If extraction failed, continue with expansion
                print(f"[child_finder] Warning: admits=0 but couldn't extract body, continuing...")
            
            # Create ProofNode for poetry's expand_node
            proof_node = ProofNode(
                file_path=patched_path,
                admits=admits_count,
                parent=None,
                score=0.0,
                depth=0
            )
            
            # Create PoetryConfig from environment settings
            config = PoetryConfig(
                max_depth=1,  # Single expansion
                max_branches=3,  # Limit candidates
                max_iterations=1,
                use_sketcher=USE_SKETCHERS,
                use_llm=USE_LLM,
                llm_tries=1,
                out_dir=out_dir,
                verbose=True,  # Enable verbose to see what's happening
                oracle=oracle,
                sketch_oracle=sketch_oracle,
                local_timeout=60,  # 60 second timeout per expansion
                global_timeout=90  # 90 second overall timeout
            )
            
            # Use poetry's expand_node to generate children with timeout
            print(f"[child_finder] Calling poetry's expand_node...")
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError("Poetry expand_node timed out")
            
            # Set a 90 second timeout for expand_node
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(90)
            
            try:
                children = expand_node(proof_node, config)
                signal.alarm(0)  # Cancel alarm
                print(f"[child_finder] Got {len(children)} children from poetry")
            except TimeoutError as e:
                signal.alarm(0)  # Cancel alarm
                print(f"[child_finder] expand_node timed out after 90s")
                node.update_win_value(-1)
                return
            
            if not children:
                # No candidates generated
                print(f"[child_finder] No children generated, marking as failed")
                node.update_win_value(-1)
                return
            
            # Process children: extract bodies and add to MCTS tree
            children_added = 0
            MAX_ADMIT_INCREASE = 10  # Allow admit increases for exploration (matches poetry's STRUCTURE_DELTA_MAX)
            
            for i, child_node in enumerate(children):
                print(f"[child_finder] Processing child {i+1}/{len(children)}: {child_node.admits} admits")
                
                # Check if complete solution (0 admits)
                if child_node.admits == 0:
                    print(f"[child_finder] *** Found child with 0 admits! ***")
                    # Extract body from the solved program
                    solved_text = child_node.file_path.read_text(encoding="utf-8")
                    solved_body = extract_method_body_text(solved_text, name)
                    if solved_body:
                        print(f"[child_finder] *** Setting montecarlo.solution (from child) ***")
                        print(f"Solution body: {solved_body[:100]}...")
                        montecarlo.solution = solved_body
                        return
                    # If extraction failed, log and skip
                    print(f"[child_finder] Warning: child has 0 admits but couldn't extract body")
                    continue
                
                # Accept children that don't increase admits too much (allow exploration)
                admit_delta = child_node.admits - node.state.admits
                if admit_delta <= MAX_ADMIT_INCREASE:
                    try:
                        child_text = child_node.file_path.read_text(encoding="utf-8")
                        child_body = extract_method_body_text(child_text, name)
                        if child_body:
                            if admit_delta <= 0:
                                print(f"[child_finder] Adding child (improvement): {node.state.admits} -> {child_node.admits} admits")
                            else:
                                print(f"[child_finder] Adding child (exploration): {node.state.admits} -> {child_node.admits} admits (+{admit_delta})")
                            add_standard_node(node, child_body, child_node.admits)
                            children_added += 1
                    except Exception as e:
                        # If extraction fails, skip this child
                        print(f"[child_finder] Warning: couldn't extract body from child: {e}")
                        pass
                else:
                    print(f"[child_finder] Skipping child (too many admits): {child_node.admits} admits (+{admit_delta})")
            
            print(f"[child_finder] Added {children_added} children to MCTS tree")
            
            # If we added children but none are better, mark as explored
            if children_added == 0:
                print(f"[child_finder] No progress made, marking as explored")
                node.update_win_value(-0.5)
                
        except Exception as e:
            # If admitter or expansion fails, mark as failure
            print(f"[child_finder] Exception: {e}")
            import traceback
            traceback.print_exc()
            node.update_win_value(-1)

def lemma1(lemma, init_p, stats, expansion_count = 7):
    name = lemma['name']
    print('lemma', name)
    x = ""
    xp = driver.insert_program_todo(lemma, init_p, x)
    e = sketcher.list_errors_for_method(xp, name)
    if not e:
        print("empty proof works")
        stats[name] = ""
        return x
    if USE_SKETCHERS:
        x = sketcher.sketch_induction(xp, name)
        xp = driver.insert_program_todo(lemma, init_p, x)
    else:
        print('Not using sketchers!')

    # Create initial verified sketch with admitter to get initial admit count
    with tempfile.NamedTemporaryFile(mode='w', suffix='.dfy', delete=False) as f:
        f.write(xp)
        seed_path = pathlib.Path(f.name)
    
    try:
        seed_patched = run_dafny_admitter(seed_path, mode="admit", timeout=30)
        initial_admits = count_admits(seed_patched)
        print(f"Initial admits: {initial_admits}")
    finally:
        seed_path.unlink(missing_ok=True)
        if seed_patched.exists():
            seed_patched.unlink(missing_ok=True)
    
    # If already solved, return early
    if initial_admits == 0:
        print("dafny-admitter solved it!")
        stats[name] = x
        return x
    
    # Initialize state with admit count
    initial_state = State(init_p, lemma, x, initial_admits)
    montecarlo = MonteCarlo(Node(initial_state))
    montecarlo.child_finder = child_finder

    print(f"Starting MCTS simulation with {expansion_count} expansions...")
    for i in range(expansion_count):
        print(f"\n=== MCTS Expansion {i+1}/{expansion_count} ===")
        montecarlo.simulate(1)
        if montecarlo.solution is not None:
            print(f"Solution found at expansion {i+1}!")
            break

    print("\n=== CHOSEN SOLUTION ===")
    print(montecarlo.solution)
    
    # Validate solution has 0 admits before accepting
    if montecarlo.solution is not None:
        xp_final = driver.insert_program_todo(lemma, init_p, montecarlo.solution)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dfy', delete=False) as f:
            f.write(xp_final)
            final_path = pathlib.Path(f.name)
        
        try:
            final_patched = run_dafny_admitter(final_path, mode="admit", timeout=30)
            final_admits = count_admits(final_patched)
            print(f"Solution validation: {final_admits} admits")
            
            if final_admits > 0:
                print(f"REJECTING: Solution has {final_admits} admits, marking as unsolved")
                stats[name] = None
                return None
            else:
                print(f"ACCEPTED: Solution has 0 admits!")
                stats[name] = montecarlo.solution
                return montecarlo.solution
        finally:
            final_path.unlink(missing_ok=True)
            if final_patched.exists():
                final_patched.unlink(missing_ok=True)
    else:
        print("No solution found")
        stats[name] = None
        return None

def print_stats(stats):
    print('FINISHED RUNNING THE BENCH')
    print(stats)
    print('total for empty proof works:', len([v for v in stats.values() if v == ""]))
    print('total for MCTS works:', len([v for v in stats.values() if v is not None and v != ""]))
    print('total for unsolved:', len([v for v in stats.values() if v is None]))

if __name__ == "__main__":
    import bench_driver
    bench_driver.run(lemma1, print_stats)
