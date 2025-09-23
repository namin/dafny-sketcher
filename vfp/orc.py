from dataclasses import dataclass
from typing import Optional

from montecarlo.node import Node
from montecarlo.montecarlo import MonteCarlo

from llm import default_generate as generate
import sketcher
import driver
import fine
import mcts_fine

import argparse
import driver
import sketcher


import argparse
import driver
import sketcher


def main_loop_simple(spec, max_attempts=50):
    """
    A simple loop that keeps trying to resolve TODOs from `spec`
    until either no TODOs remain or attempts run out.
    """

    p = spec
    attempts = 0

    while attempts < max_attempts:
        attempts += 1

        # Check if all todos are done
        todo = sketcher.sketch_next_todo(p)
        if todo is None:
            print("SOLUTION FOUND")
            return p

        done = sketcher.sketch_done(p)

        # Try to solve the todo
        xp = driver.dispatch_implementer(p, todo, done)

        if xp is None:
            print(f"Attempt {attempts}: Couldn't solve todo {todo}")

            if todo["type"] == "lemma":
                # Try induction sketch fallback
                x = sketcher.sketch_induction(
                    driver.insert_program_todo(todo, p, ""), todo["name"]
                )
                xp = driver.insert_program_todo(todo, p, x)

                if xp is not None:
                    p = xp
                    continue

            # If nothing worked, try again
            continue

        # If we got a new program, update state
        p = xp

    print("Gave up after max attempts")
    return None


def main(spec, max_attempts=50):
    solution = main_loop_simple(spec, max_attempts=max_attempts)
    print("FINAL SOLUTION:", solution)
    return solution


if __name__ == "__main__":
    import tests
    tests.run(main)





