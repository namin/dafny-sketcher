"""
Benchmark script comparing repair from empty vs skeleton starting points.

For each lemma whose solution has a top-level case/if structure:
  1. Run 3 LLM repair iterations starting from an empty body
  2. Run 3 LLM repair iterations starting from the skeleton
     (just the top-level if/case analysis with empty branches,
      extracted from the known solution)

Skips lemmas whose solution does not have a case/if shape.
"""

import re
from llm import default_generate as generate
import driver
import sketcher
from fine import format_errors
from driver import prompt_begin_dafny, extract_dafny_program


# ---------------------------------------------------------------------------
# Skeleton extraction
# ---------------------------------------------------------------------------

def extract_skeleton(sketch: str) -> str | None:
    """
    Extract the top-level case/if structure from an induction sketch,
    replacing branch bodies with empty content.

    Returns the skeleton text (suitable for insertion as a lemma body),
    or None if the sketch has no recognisable case/if structure.
    """
    lines = sketch.splitlines()

    # Try match/case first
    skeleton_lines = _skeleton_match_cases(lines)
    if skeleton_lines is not None:
        return '\n'.join(skeleton_lines)

    # Try if/else
    skeleton_lines = _skeleton_if_else(lines)
    if skeleton_lines is not None:
        return '\n'.join(skeleton_lines)

    return None


def _skeleton_match_cases(lines: list[str]) -> list[str] | None:
    """Build skeleton for match/case branches."""
    # Find the match line and case lines at the top level
    match_line = None
    case_starts = []
    depth = 0

    for i, line in enumerate(lines):
        stripped = line.strip()
        if match_line is None and stripped.startswith('match '):
            match_line = i
        if re.match(r'case\s+', stripped) and '=>' in stripped:
            if depth == 0:
                case_starts.append(i)
        for ch in line:
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1

    if not case_starts:
        return None

    result = []
    # Include any lines before the first case (like the match line)
    start = match_line if match_line is not None else 0
    for i in range(start, case_starts[0]):
        result.append(lines[i])

    for idx, cs in enumerate(case_starts):
        header = lines[cs].rstrip()
        # If the header already contains a '{', strip everything after it
        # and rebuild as empty-bodied case
        brace_pos = header.find('{')
        if brace_pos != -1:
            header = header[:brace_pos].rstrip()
        result.append(header + ' {')
        result.append('}')

    return result


def _skeleton_if_else(lines: list[str]) -> list[str] | None:
    """Build skeleton for if/else branches."""
    # Find the top-level if and else lines
    branch_starts = []
    if_depth = None
    depth = 0

    for i, line in enumerate(lines):
        stripped = line.strip()
        if if_depth is None:
            if stripped.startswith('if ') and '{' in stripped:
                if_depth = depth
                branch_starts.append(i)
        else:
            if depth == if_depth + 1 and re.match(r'\}\s*else\b', stripped):
                branch_starts.append(i)
        for ch in line:
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1

    if len(branch_starts) < 2:
        return None

    result = []
    for idx, bs in enumerate(branch_starts):
        header = lines[bs].rstrip()
        if idx == 0:
            # "if cond {" → keep up to the opening brace
            brace_pos = header.find('{')
            if brace_pos != -1:
                result.append(header[:brace_pos + 1])
            else:
                result.append(header + ' {')
        else:
            # "} else {" or "} else if cond {"
            # Rebuild: close previous, open new
            stripped = lines[bs].strip()
            result.append('  ' + stripped)
        result.append('')  # empty body line

    # Close the final branch
    result.append('}')
    return result


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

def prompt_lemma_implementer(program: str, name: str, e: list[str]) -> str:
    return f'You are implementing a lemma in a Dafny program that is specified but not fully implemented. The current program is\n{program}\n\nThe lemma to implement is {name}. {prompt_begin_dafny("lemma")}\nThe errors in the work-in-progress lemma are:\n{format_errors(e)}'


# ---------------------------------------------------------------------------
# Repair loop (shared between empty and skeleton modes)
# ---------------------------------------------------------------------------

def repair_loop(lemma, init_p, start_body: str, name: str, n_iterations: int = 3):
    """
    Run *n_iterations* of LLM repair starting from *start_body*.

    Returns ``(iteration, proof)`` on success (iteration 0-based),
    or ``(None, last_attempt)`` on failure.
    """
    p = driver.insert_program_todo(lemma, init_p, start_body)
    e = sketcher._list_errors_for_method_core(p, name)
    if not e:
        return (-1, start_body)  # starting point already verifies

    last_x = start_body
    for i in range(n_iterations):
        prompt = prompt_lemma_implementer(p, name, e)
        r = generate(prompt)
        x = extract_dafny_program(r)
        if x is None:
            continue
        last_x = x
        p = driver.insert_program_todo(lemma, init_p, x)
        e = sketcher._list_errors_for_method_core(p, name)
        if not e:
            return (i, x)

    return (None, last_x)


# ---------------------------------------------------------------------------
# Main benchmark entry point
# ---------------------------------------------------------------------------

def lemma1(lemma, p, stats):
    init_p = p
    name = lemma['name']
    print('lemma', name)

    # Extract the skeleton from the solution body
    lines = init_p.splitlines()
    body_text = '\n'.join(lines[lemma['insertLine']:lemma['endLine']-1])
    skeleton = extract_skeleton(body_text)
    if skeleton is None:
        print("  solution has no case/if structure, skipping")
        stats[name] = {'empty': None, 'skeleton': None, 'skipped': True}
        return

    print(f"  skeleton:\n{skeleton}")

    # Check empty proof first
    xp = driver.insert_program_todo(lemma, init_p, "")
    e = sketcher.list_errors_for_method(xp, name)
    if not e:
        print("  empty proof works (trivial)")
        stats[name] = {'empty': -1, 'skeleton': -1, 'skipped': False}
        return

    # --- Mode A: repair from empty ---
    print("  [empty] starting repair loop...")
    empty_iter, empty_proof = repair_loop(lemma, init_p, "", name)
    if empty_iter is not None:
        print(f"  [empty] solved at iteration {empty_iter}")
    else:
        print("  [empty] failed")

    # --- Mode B: repair from skeleton ---
    print("  [skeleton] starting repair loop...")
    skel_iter, skel_proof = repair_loop(lemma, init_p, skeleton, name)
    if skel_iter is not None:
        print(f"  [skeleton] solved at iteration {skel_iter}")
    else:
        print("  [skeleton] failed")

    stats[name] = {
        'empty': empty_iter,
        'skeleton': skel_iter,
        'skipped': False,
    }
    if empty_iter is not None:
        stats['proof_empty_' + name] = empty_proof
    if skel_iter is not None:
        stats['proof_skeleton_' + name] = skel_proof


# ---------------------------------------------------------------------------
# Stats reporting
# ---------------------------------------------------------------------------

def print_summary_stats(stats):
    entries = {k: v for k, v in stats.items() if isinstance(v, dict)}
    total = len(entries)
    skipped = len([v for v in entries.values() if v.get('skipped')])
    considered = total - skipped

    empty_solved = len([v for v in entries.values()
                        if not v.get('skipped') and v['empty'] is not None])
    skel_solved = len([v for v in entries.values()
                       if not v.get('skipped') and v['skeleton'] is not None])

    both_solved = len([v for v in entries.values()
                       if not v.get('skipped')
                       and v['empty'] is not None and v['skeleton'] is not None])
    only_empty = len([v for v in entries.values()
                      if not v.get('skipped')
                      and v['empty'] is not None and v['skeleton'] is None])
    only_skel = len([v for v in entries.values()
                     if not v.get('skipped')
                     and v['empty'] is None and v['skeleton'] is not None])
    neither = len([v for v in entries.values()
                   if not v.get('skipped')
                   and v['empty'] is None and v['skeleton'] is None])

    print(f'\ntotal lemmas: {total}')
    print(f'skipped (no case/if structure): {skipped}')
    print(f'considered: {considered}')
    print(f'  empty solved:    {empty_solved}')
    print(f'  skeleton solved: {skel_solved}')
    print(f'  both solved:     {both_solved}')
    print(f'  only empty:      {only_empty}')
    print(f'  only skeleton:   {only_skel}')
    print(f'  neither:         {neither}')

    # Compare iteration counts where both solved
    skel_faster = 0
    empty_faster = 0
    same_speed = 0
    for v in entries.values():
        if v.get('skipped') or v['empty'] is None or v['skeleton'] is None:
            continue
        if v['skeleton'] < v['empty']:
            skel_faster += 1
        elif v['empty'] < v['skeleton']:
            empty_faster += 1
        else:
            same_speed += 1
    if both_solved > 0:
        print(f'\n  among {both_solved} solved by both:')
        print(f'    skeleton faster: {skel_faster}')
        print(f'    empty faster:    {empty_faster}')
        print(f'    same iterations: {same_speed}')


def print_stats(stats):
    print('\nFINISHED RUNNING THE BENCH')
    print_summary_stats(stats)

    entries = {k: v for k, v in stats.items() if isinstance(v, dict)}
    print('\n--- per-lemma results ---')
    for name, v in sorted(entries.items()):
        if v.get('skipped'):
            continue
        print(f'  {name}: empty={v["empty"]}  skeleton={v["skeleton"]}')

    print_summary_stats(stats)


if __name__ == "__main__":
    import bench_driver
    bench_driver.run(lemma1, print_stats)
