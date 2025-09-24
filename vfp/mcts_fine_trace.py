import llm
old_default_generate = llm.default_generate
llm_calls = []
failed_llm_calls_per_parent = {}
def generate(prompt, **kwargs):
    print(f"!!! LLM call !!!")
    result = old_default_generate(prompt, **kwargs)
    llm_calls.append((prompt, result))
    return result
llm.default_generate = generate

from dataclasses import dataclass
from typing import List, Tuple

from montecarlo.node import Node
from montecarlo.montecarlo import MonteCarlo

import sketcher
import driver
import fine

import os
INDUCTIVE_SKETCH = os.environ.get('INDUCTIVE_SKETCH', 'true').lower() != 'false'

@dataclass
class State:
    program: str
    llm_calls: List[Tuple[str, str]]

def add_standard_node(node, p):
    global llm_calls
    child = Node(State(p, llm_calls))
    llm_calls = []
    node.add_child(child)
    child.update_win_value(1)
    child.update_policy_value(1)

    child = Node(node.state)
    node.add_child(child)
    child.update_policy_value(0.2)

def child_finder(node, montecarlo):
    global llm_calls
    p = node.state.program
    todo_lemmas = sketcher.sketch_todo_lemmas(p)
    if todo_lemmas:
        xp = fine.fine_implementer(p, todo_lemmas[0])
        if xp is None:
            print("Didn't solve todo")
            failed_llm_calls_per_parent[node] = llm_calls + failed_llm_calls_per_parent.get(node, [])
            llm_calls = []
            node.update_win_value(-1)
        else:
            add_standard_node(node, xp)
        return
    todo = sketcher.sketch_next_todo(p)
    if todo is None:
        montecarlo.solution_node = node
        montecarlo.solution = p
        return
    done = sketcher.sketch_done(p)
    xp = driver.dispatch_implementer(p, todo, done)
    if xp is None:
        print("Didn't solve todo")
        failed_llm_calls_per_parent[node] = llm_calls + failed_llm_calls_per_parent.get(node, [])
        llm_calls = []
        if INDUCTIVE_SKETCH and todo['type'] == 'lemma':
            # can we enter fine mode with sketch?
            # for now, let's try a symbolic inductive sketch
            # we could also ask the LLM for a sketch, but we need a good way to evaluate it
            x = sketcher.sketch_induction(driver.insert_program_todo(todo, p, ""), todo['name'])
            xp = driver.insert_program_todo(todo, p, x)
            if xp:
                errors = sketcher.list_errors_for_method(xp, todo['name'])
                if fine.proper_only(errors):
                    add_standard_node(node, xp)
                    return
            llm_calls = []
        node.update_win_value(-1)
    else:
        add_standard_node(node, xp)

def trace_solution(node):
    trace = []
    winning = []
    failure_learning = []
    while node is not None:
        winning = node.state.llm_calls + winning
        trace = [node.state.program] + trace
        for p, rf in failed_llm_calls_per_parent.get(node.parent, []):
            for p2, rw in node.state.llm_calls:
                if p2 == p:
                    failure_learning.append((p, rf, rw))
        node = node.parent
    print('WINNING CALLS')
    for p, r in winning:
        print('PROMPT')
        print(p)
        print('RESPONSE')
        print(r)
    print('FAILURE LEARNING')
    for p, rf, r in failure_learning:
        print('PROMPT')
        print(p)
        print('FAILURE RESPONSE')
        print(rf)
        print('SUCCESS RESPONSE')
        print(r)
    return trace

def main(spec, expansion_count = 20):
    global llm_calls
    global failed_llm_calls_per_parent
    llm_calls = []
    failed_llm_calls_per_parent = {}

    montecarlo = MonteCarlo(Node(State(spec, [])))
    montecarlo.child_finder = child_finder
    montecarlo.solution_node = None

    montecarlo.simulate(expansion_count)

    print("CHOSEN SOLUTION")
    print(montecarlo.solution)

    if montecarlo.solution_node is not None:
        print("TRACE")
        trace = trace_solution(montecarlo.solution_node)
        print(trace)
    
    return montecarlo.solution

if __name__ == "__main__":
    import tests
    tests.run(main)
    #import bench_solve
    #bench_solve.main(main)
