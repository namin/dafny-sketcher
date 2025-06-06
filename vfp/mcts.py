from dataclasses import dataclass
from typing import Optional

from montecarlo.node import Node
from montecarlo.montecarlo import MonteCarlo

from llm import default_generate as generate
import sketcher
import driver

@dataclass
class State:
    program: str
    command: Optional[str]

def pick_edit_function(program, done_functions):
    prompt = f"You have to choose a function to re-implement among those already implemented. The current program is\n{program}\n\n."
    prompt += "Only write in one line\n// EDIT <function name>\n where <function name> is one of the following: " + ", ".join(done_functions) + f" to specify which function to re-implement. Be honest and choose to re-implement a buggy function instead of changing the spirit of the spec."
    r = generate(prompt)
    edit_function = driver.extract_edit_function(r, done_functions)
    return edit_function # may be None

def add_standard_node(node, p):
    child = Node(State(p, None))
    node.add_child(child)
    child.update_win_value(1)
    child.update_policy_value(1)

    child = Node(node.state)
    node.add_child(child)
    child.update_policy_value(0.2)

def child_finder(node, montecarlo):
    p = node.state.program
    todo = sketcher.sketch_next_todo(p)
    done = sketcher.sketch_done(p)
    done_functions = [u['name'] for u in done if u['type'] == 'function'] if done else []
    command = node.state.command
    if command is None:
        if todo is None:
            montecarlo.solution = p
            return
        child = Node(State(p, "next"))
        node.add_child(child)
        child.update_win_value(1)
        child.update_policy_value(1)
        if done_functions:
            child = Node(State(p, "edit"))
            node.add_child(child)
            child.update_policy_value(0.3)
    elif command == 'next':
        xp = driver.dispatch_implementer(p, todo, done)
        if xp is None:
            print("Didn't solve todo")
            node.update_win_value(-1)
        else:
            add_standard_node(node, xp)
    elif command == 'edit':
        n = len(done_functions)
        assert n>=1
        if n>1:
            edit_function = pick_edit_function(p, done_functions)
            if edit_function is None:
                edit_function = done_functions[-1] # arbitrary
        else:
            edit_function = done_functions[0]
        print('edit function', edit_function)
        xp = driver.llm_implementer(p, [u for u in done if u['name'] == edit_function][0], hint=f"You chose to re-implement {edit_function} instead of implementing {todo['name']}.")
        if xp is None:
            print("Didn't solve edit")
            # No need to penalize
            #node.update_win_value(-1)
        else:
            add_standard_node(node, xp)

def main(spec, expansion_count = 20):
    montecarlo = MonteCarlo(Node(State(spec, None)))
    montecarlo.child_finder = child_finder

    montecarlo.simulate(expansion_count)

    print("CHOSEN SOLUTION")
    print(montecarlo.solution)

if __name__ == "__main__":
    import tests
    tests.run(main)
    #import bench_solve
    #bench_solve.main(main)
