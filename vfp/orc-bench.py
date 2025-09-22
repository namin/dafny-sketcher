import os
import glob
import tests
import sketcher
import orc


def main(filenames=None):
    stats = {
        "total": 0,
        "solved": 0,
        "failed": 0,
        "files": {}
    }

    if not filenames:
        filenames = sorted(glob.glob("bench/*_solution.dfy"))
        filenames = [f for f in filenames if os.path.basename(f)[0].islower()]

    print(len(filenames))
    print(filenames)

    for f in filenames:
        print('---------- Looking at file: ', f, '--------------')
        p = tests.read_file(f)

        # Optionally check errors
        if False:
            e = sketcher.show_errors(p)
            if e is not None:
                print('ERRORS')
                print(e)

        stats["total"] += 1

        solution = orc.main(p)

        if solution is None:
            stats["failed"] += 1
            stats["files"][f] = "FAILED"
        else:
            stats["solved"] += 1
            stats["files"][f] = "SOLVED"

    print_stats(stats)


def print_stats(stats):
    print("\n===== BENCHMARK STATS =====")
    print(f"Total: {stats['total']}")
    print(f"Solved: {stats['solved']}")
    print(f"Failed: {stats['failed']}")
    print("\nPer-file results:")
    for f, result in stats["files"].items():
        print(f"  {os.path.basename(f)}: {result}")
    print("===========================\n")


def run():
    import argparse

    parser = argparse.ArgumentParser(description='Run the simple bench suite')
    parser.add_argument(
        '--file',
        type=str,
        action='append',
        help='Path to Dafny file to process (can be used multiple times)',
    )

    args = parser.parse_args()
    main(args.file)


if __name__ == "__main__":
    run()
