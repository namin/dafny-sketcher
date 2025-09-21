import glob
import os

def main(main1, print_stats, solution_files=None):
    stats = {}
    if not solution_files:
        solution_files = sorted(glob.glob("bench/*_solution.dfy"))
        solution_files = [f for f in solution_files if os.path.basename(f)[0].islower()]
    print(len(solution_files))
    print(solution_files)
    for f in solution_files:
        main1(f, stats)
    print_stats(stats)


def run(main1, print_stats):
    import argparse
    
    parser = argparse.ArgumentParser(description='Run the bench suite')
    parser.add_argument('--file', type=str, action='append', help='Path to Dafny file to process (can be used multiple times)')
    
    args = parser.parse_args()
    
    main(main1, print_stats, args.file)

