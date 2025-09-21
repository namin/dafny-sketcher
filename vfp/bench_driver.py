import glob
import os

def main(main1, print_stats):
    stats = {} 
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
    parser.add_argument('--file', type=str, help='Path to Dafny file to process')
    
    args = parser.parse_args()
    
    if args.file:
        stats = {}
        # run on a single file
        f = args.file
        main1(f, stats)
        print_stats(stats)
    else:
        main(main1, print_stats)
        
