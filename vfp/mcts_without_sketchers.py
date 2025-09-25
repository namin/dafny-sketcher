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

def child_finder(node, montecarlo):
    p = node.state
    todo_lemmas = sketcher.sketch_todo_lemmas(p)
    if todo_lemmas:
        todo = todo_lemmas[0]
    else:
        todo = sketcher.sketch_next_todo(p)
    if todo is None:
        montecarlo.solution = p
        return
    done = sketcher.sketch_done(p)
    xp = driver.llm_implementer(p, todo, done=done)
    if xp is None:
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
