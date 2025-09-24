import glob
import os
import tests
import sketcher

def main(lemma1, print_stats, solution_files=None, lemma_names=None):
    stats = {}
    if not solution_files:
        solution_files = sorted(glob.glob("bench/*_solution.dfy"))
        solution_files = [f for f in solution_files if os.path.basename(f)[0].islower()]
    print(len(solution_files))
    print(solution_files)
    for f in solution_files:
        main1(lemma1, f, stats, lemma_names=lemma_names)
    print_stats(stats)

def main1(lemma1, f, stats, lemma_names=None):
    print('---------- Looking at file: ', f, '--------------')
    p = tests.read_file(f)
    if False:
        e = sketcher.show_errors(p)
        if e is not None:
            print('ERRORS')
            print(e)
    done = sketcher.sketch_done(p)
    lemmas = [x for x in done if x['type'] == 'lemma']
    for lemma in lemmas:
        if not lemma_names or lemma['name'] in lemma_names:
            lemma1(lemma, p, stats)

def run(lemma1, print_stats):
    import argparse
    
    parser = argparse.ArgumentParser(description='Run the bench suite')
    parser.add_argument('--file', type=str, action='append', help='Path to Dafny file to process (can be used multiple times)')
    parser.add_argument('--lemma', type=str, action='append', help='Name of lemma to process (can be used multiple times)')
    
    args = parser.parse_args()
    
    main(lemma1, print_stats, args.file, args.lemma)

