"""
Benchmark using POETRY (dafny-poetry) on the VFP benchmark suite.

This uses the same lemma parameters as bench_track.py but calls the POETRY API
instead of using individual LLM calls.
"""

import driver
import os
import pathlib
import tempfile
from dafny_poetry.api import verify_dafny

USE_SKETCHERS = os.environ.get('USE_SKETCHERS', 'true').lower() != 'false'

def lemma1(lemma, p, stats):
    """
    Run POETRY on a single lemma.

    This follows the same interface as bench_track.py's lemma1 function:
    - lemma: dict with lemma metadata (name, insertLine, etc.)
    - p: the full program source as a string
    - stats: dict to accumulate results
    """
    init_p = p  # the offsets for insertion are based on original program
    name = lemma['name']
    print('lemma', name)

    # Create a version of the program with empty lemma body
    x = ""  # empty body
    xp = driver.insert_program_todo(lemma, init_p, x)

    # Create temporary directory for POETRY output
    with tempfile.TemporaryDirectory(prefix=f"poetry_{name}_") as tmpdir:
        out_dir = pathlib.Path(tmpdir)

        try:
            # Run POETRY on the program
            result = verify_dafny(
                xp,
                max_depth=3,
                use_sketcher=USE_SKETCHERS,
                use_llm=True,
                llm_tries=2,
                timeout=300,  # 5 minutes per lemma
                verbose=True,
                out_dir=out_dir
            )

            if result.error:
                print(f"  Error: {result.error}")
                stats[name] = 0
                stats['failed_proof_' + name] = result.error
                return

            if result.success and result.final_admits == 0:
                print(f"  ✓ POETRY solved it! (admits: {result.initial_admits} → 0)")
                # Read the final proof
                final_source = result.final_path.read_text()
                stats[name] = 5  # New category for POETRY success
                stats['proof_poetry_' + name] = final_source
            elif result.final_admits < result.initial_admits:
                print(f"  ~ Partial progress (admits: {result.initial_admits} → {result.final_admits})")
                stats[name] = 6  # Partial progress
                final_source = result.final_path.read_text()
                stats['partial_poetry_' + name] = final_source
            else:
                print(f"  ✗ No progress (admits: {result.initial_admits})")
                stats[name] = 0

        except Exception as e:
            print(f"  Exception: {e}")
            import traceback
            traceback.print_exc()
            stats[name] = 0
            stats['failed_proof_' + name] = str(e)


def print_summary_stats(stats):
    """Print summary statistics matching bench_track.py format."""
    poetry_solved = len([v for v in stats.values() if isinstance(v, int) and v == 5])
    poetry_partial = len([v for v in stats.values() if isinstance(v, int) and v == 6])
    unsolved = len([v for v in stats.values() if isinstance(v, int) and v == 0])

    print('total for POETRY solved (0 admits):', poetry_solved)
    print('total for POETRY partial progress:', poetry_partial)
    print('total for unsolved:', unsolved)


def print_stats(stats):
    """Print final statistics."""
    print('FINISHED RUNNING THE BENCH (POETRY)')
    print(stats)
    print_summary_stats(stats)
    print('lemmas')
    for k, v in stats.items():
        if not isinstance(v, int):
            print(k)
            print(v[:200] if isinstance(v, str) and len(v) > 200 else v)
    print_summary_stats(stats)


if __name__ == "__main__":
    import bench_driver
    bench_driver.run(lemma1, print_stats)
