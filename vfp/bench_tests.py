import glob
import os

import driver
import sketcher
import tests


import llm_repair  # wrapper around llm.py

def try_llm_repair(program, sketch, lemma):
    """Call LLM to repair a failing inductive sketch."""
    repaired = llm_repair.repair(program, sketch, lemma['name'])
    xp = driver.insert_program_todo(lemma, program, repaired)  # use the real lemma dict
    e = sketcher.list_errors_for_method(xp, lemma['name'])
    if not e:
        return True, None, repaired
    else:
        return False, e, repaired

def main1(f, stats):
    p = tests.read_file(f)
    print('PROGRAM')
    print(p)
    if True:
        e = sketcher.show_errors(p)
        if e is not None:
            print('ERRORS')
            print(e)
    done = sketcher.sketch_done(p)
    lemmas = [x for x in done if x['type'] == 'lemma']
    for lemma in lemmas:
        name = lemma['name']
        print('lemma', name)
        xp = driver.insert_program_todo(lemma, p, "")
        e = sketcher.list_errors_for_method(xp, name)
        if not e:
            print("empty proof works")
            stats[name] = 0
            continue
        ix = sketcher.sketch_induction(xp, name)
        ip = driver.insert_program_todo(lemma, p, ix)
        e = sketcher.list_errors_for_method(ip, name)
        if not e:
            print("inductive proof sketch works")
            stats[name] = 1
            continue

        # Strategy 3: inductive sketch + LLM repair
        ok, errs, repaired = try_llm_repair(xp, ix, lemma)
        if ok:
            print("inductive + LLM repair works")
            stats[name] = 2
            
        else:
            print("all failed :(")
            stats[name] = (ix, repaired)

def print_stats(stats):
    print('STATS')
    print(stats)
    for k, v in stats.items():
        if not isinstance(v, int):
            print('--------------------------------')
            print('lemma')
            print(k)
            print('with sketch')
            print(v[0])
            print('with LLM repair')
            print(v[1])
    print('total for empty proof works:', len([v for v in stats.values() if v == 0]))
    print('total for inductive proof sketch works:', len([v for v in stats.values() if v == 1]))
    print('total for inductive + LLM repair works:', len([v for v in stats.values() if v == 2]))
    print('total for errors:', len([v for v in stats.values() if not isinstance(v, int)]))
    print({k:3 if not isinstance(v, int) else v for k,v in stats.items()})

def main():
    stats = {} 
    solution_files = sorted(glob.glob("bench/*_solution.dfy"))
    solution_files = [f for f in solution_files if os.path.basename(f)[0].islower()]
    print(len(solution_files))
    print(solution_files)
    for f in solution_files:
        main1(f, stats)
    print_stats(stats)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        main()
    else:
        stats = {}
        # just run main1 on a single file
        f = sys.argv[1]
        main1(f, stats)
        print_stats(stats)

