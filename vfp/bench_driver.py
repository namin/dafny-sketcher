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
    import sys
    if len(sys.argv) < 2:
        main(main1, print_stats)
    else:
        stats = {}
        # just run main1 on a single file
        f = sys.argv[1]
        main1(f, stats)
        print_stats(stats)
