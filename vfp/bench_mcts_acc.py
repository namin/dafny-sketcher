from dataclasses import dataclass
from typing import Optional

from montecarlo.node import Node
from montecarlo.montecarlo import MonteCarlo

from llm import default_generate as generate
import driver
import sketcher
from fine import format_errors
from driver import prompt_begin_dafny, extract_dafny_program
from bench_feedback import prompt_lemma_implementer

import os
USE_SKETCHERS = os.environ.get('USE_SKETCHERS', 'true').lower() != 'false'

@dataclass
class State:
    initial_program: str
    lemma: object
    body: str

def add_standard_node(node, body):
    child = Node(State(node.state.initial_program, node.state.lemma, body))
    node.add_child(child)
    child.update_win_value(1)
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
    e = sketcher.list_errors_for_method(p, name)
    if not e:
        montecarlo.solution = x
        return
    prompt = prompt_lemma_implementer(p, name, e)
    r = generate(prompt)
    x = extract_dafny_program(r)
    if x is None:
        node.update_win_value(-1)
    else:
        # TODO: could still penalize more harshly based on errors
        add_standard_node(node, x)

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

    montecarlo = MonteCarlo(Node(State(init_p, lemma, x)))
    montecarlo.child_finder = child_finder

    montecarlo.simulate(expansion_count)

    print("CHOSEN SOLUTION")
    print(montecarlo.solution)
    stats[name] = montecarlo.solution
    return montecarlo.solution

def print_stats(stats):
    print('FINISHED RUNNING THE BENCH')
    print(stats)
    print('total for empty proof works:', len([v for v in stats.values() if v == ""]))
    print('total for MCTS works:', len([v for v in stats.values() if v is not None and v != ""]))
    print('total for unsolved:', len([v for v in stats.values() if v is None]))

if __name__ == "__main__":
    import bench_driver
    bench_driver.run(lemma1, print_stats)
