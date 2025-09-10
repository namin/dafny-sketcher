import glob
import os

import driver
import sketcher
import tests

def main1(f, stats):
    print('---------- Looking at file: ', f, '--------------')
    p = tests.read_file(f)
    if False:
        e = sketcher.show_errors(p)
        if e is not None:
            stats[f] = e
        else:
            stats[f] = "OK"
    done = sketcher.sketch_done(p)
    lemmas = [x for x in done if x['type'] == 'lemma']
    for lemma in lemmas:
        name = lemma['name']
        print('lemma', name)
        xp = driver.insert_program_todo(lemma, p, "")
        e = sketcher.show_errors(xp)
        if e is None:
            print("empty proof works")
            stats[name] = -1
            continue
        ix = sketcher.sketch_induction(xp, name)
        ip = driver.insert_program_todo(lemma, p, ix)
        e = sketcher.show_errors(ip)
        if e is None:
            print("inductive proof sketch works")
            stats[name] = 0
        else:
            print("inductive proof failed")
            stats[name] = 1 #stats[name] = ix

def main():
    stats = {}
    
    solution_files = sorted(glob.glob("bench/*_solution.dfy"))
    solution_files = [f for f in solution_files if os.path.basename(f)[0].islower()]
    print(len(solution_files))
    print(solution_files)
    for f in solution_files:
        main1(f, stats)
    print('FINISHED FOR LOOP')
    print(stats)
    print('total for empty proof works:', len([v for v in stats.values() if isinstance(v, int) and v == -1]))
    print('total for inductive proof sketch works:', len([v for v in stats.values() if isinstance(v, int) and v == 0]))
    print('total for errors:', len([v for v in stats.values() if not isinstance(v, int)]))
    print('lemmas with errors:')
    for k, v in stats.items():
        if not isinstance(v, int):
            print(k)
            print(v)

if __name__ == "__main__":
    main()