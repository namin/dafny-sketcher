from dataclasses import dataclass
from typing import Optional

from montecarlo.node import Node
from montecarlo.montecarlo import MonteCarlo

from llm import default_generate as generate
import sketcher
import driver
import fine

def add_standard_node(node, p):
    child = Node(p)
    node.add_child(child)
    child.update_win_value(1)
    child.update_policy_value(1)

    child = Node(node.state)
    node.add_child(child)
    child.update_policy_value(0.2)

#Called by MCTs to find new children. With in this, we add/take away todos. 
#If it fails, then we take the node out. If it succeeds then it will loop back. 
def child_finder(node, montecarlo):
    p = node.state
    todo_lemmas = sketcher.sketch_todo_lemmas(p)
    if todo_lemmas:
        xp = fine.fine_implementer(p, todo_lemmas[0])
        if xp is None:
            print("Didn't solve todo")
            node.update_win_value(-1)
        else:
            add_standard_node(node, xp)
        return
    todo = sketcher.sketch_next_todo(p)
    if todo is None:
        montecarlo.solution = p
        return
    done = sketcher.sketch_done(p)
    xp = driver.dispatch_implementer(p, todo, done)
    if xp is None:
        print("Didn't solve todo")
        if todo['type'] == 'lemma':
            # can we enter fine mode with sketch?
            # for now, let's try a symbolic inductive sketch
            # we could also ask the LLM for a sketch, but we need a good way to evaluate it
            x = sketcher.sketch_induction(driver.insert_program_todo(todo, p, ""), todo['name'])
            xp = xp = driver.insert_program_todo(todo, p, x)
            if xp:
                add_standard_node(node, xp)
                return
        node.update_win_value(-1)
    else:
        add_standard_node(node, xp)

def main(spec, expansion_count = 20):
    montecarlo = MonteCarlo(Node(spec))
    montecarlo.child_finder = child_finder

    montecarlo.simulate(expansion_count)

    print("CHOSEN SOLUTION")
    print(montecarlo.solution)
    return montecarlo.solution

if __name__ == "__main__":
    import tests
    tests.run(main)
    #import bench_solve
    #bench_solve.main(main)
