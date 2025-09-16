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
    e = sketcher.show_errors(xp)
    if e is None:
        return True, None
    else:
        return False, e

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
        e = sketcher.show_errors(xp)
        if e is None:
            print("empty proof works")
            stats[name] = 0
            continue
        ix = sketcher.sketch_induction(xp, name)
        ip = driver.insert_program_todo(lemma, p, ix)
        e = sketcher.show_errors(ip)
        if e is None:
            print("inductive proof sketch works")
            stats[name] = 1
            continue

        # Strategy 3: inductive sketch + LLM repair
        ok, errs = try_llm_repair(xp, ix, lemma)
        if ok:
            print("inductive + LLM repair works")
            stats[name] = 2
            
        else:
            print("all failed :(")
            stats[name] = ix  # keep sketch that failed. 
            #Q: do we want to print the sketch or the LLM update? Or both?

def main():
    stats = {}
    
    solution_files = sorted(glob.glob("bench/*_solution.dfy"))
    solution_files = [f for f in solution_files if os.path.basename(f)[0].islower()]
    print(len(solution_files))
    print(solution_files)
    for f in solution_files:
        main1(f, stats)
    print(stats)
    print('total for empty proof works:', len([v for v in stats.values() if v == 0]))
    print('total for inductive proof sketch works:', len([v for v in stats.values() if v == 1]))
    print('total for inductive + LLM repair works:', len([v for v in stats.values() if v == 2]))
    print('total for errors:', len([v for v in stats.values() if not isinstance(v, int)]))

    for k, v in stats.items():
        if not isinstance(v, int):
            print(k)
            print(v)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        main()
    else:
        stats = {}
        # just run main1 on a single file
        f = sys.argv[1]
        main1(f, stats)
        
        for k, v in stats.items():
            if not isinstance(v, int):
                print(k)
                print(v)
        print(stats)

