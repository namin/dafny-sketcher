import glob
import os

import driver
import sketcher
import tests


import llm_repair  # wrapper around llm.py

import glob
import os

import driver
import sketcher
import tests
import llm_repair  # contains generate_proof()

'''
to do
add better library orgonization so as to not reuse xode

'''


def try_llm_generate(program, lemma):
    """Call LLM to generate a full proof from scratch."""
    generated = llm_repair.generate_proof(program, lemma)
    xp = driver.insert_program_todo(lemma, program, generated)
    e = sketcher.show_errors(xp)
    if e is None:
        return True, None, generated
    else:
        return False, e, generated


def main1(f, stats):
    """Run LLM proof generation on all lemmas in one file."""
    program = tests.read_file(f)
    lemmas = [x for x in sketcher.sketch_done(program) if x['type'] == 'lemma']

    for lemma in lemmas:
        name = lemma['name']
        print(f"lemma {name}")

        ok, errs, proof = try_llm_generate(program, lemma)
        if ok:
            print(":) :) :) LLM generation works")
            stats[name] = {"status": "success", "proof": proof}
        else:
            print(":( :( :( LLM generation failed")
            stats[name] = {"status": "error", "errors": errs, "proof": proof}




def loop_on_lemmas(main1):
    stats = {}

    solution_files = sorted(glob.glob("bench/*_solution.dfy"))
    # skip uppercase files
    solution_files = [f for f in solution_files if os.path.basename(f)[0].islower()]

    print(f"Found {len(solution_files)} solution files")
    for f in solution_files:
        print(f"\n=== File: {f} ===")
        main1(f, stats)


def print_results(stats):



def main():
    stats = {}

    solution_files = sorted(glob.glob("bench/*_solution.dfy"))
    # skip uppercase files
    solution_files = [f for f in solution_files if os.path.basename(f)[0].islower()]

    print(f"Found {len(solution_files)} solution files")
    for f in solution_files:
        print(f"\n=== File: {f} ===")
        main1(f, stats)

    # Summary
    total_ok = sum(1 for v in stats.values() if v["status"] == "success")
    total_err = sum(1 for v in stats.values() if v["status"] == "error")

    print("\n=== Summary ===")
    print("total lemmas:", len(stats))
    print("successful proofs:", total_ok)
    print("failed proofs:", total_err)

    # Print failing cases
    for name, result in stats.items():
        if result["status"] == "error":
            print(f"\nLemma {name} failed:")
            print("Generated proof:")
            print(result["proof"])
            print("Errors:")
            print(result["errors"])


if __name__ == "__main__":
    main()
