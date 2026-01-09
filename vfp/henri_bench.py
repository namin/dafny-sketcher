"""Henri benchmark for Dafny lemma proving.

Uses henri with hooks to solve Dafny lemmas, then validates:
1. The solution only adds lines (no modifications/deletions)
2. The solution verifies with Dafny

Usage:
    python henri_bench.py
    python henri_bench.py --file bench/binary_search_solution.dfy
    python henri_bench.py --file bench/reverse_solution.dfy --lemma reverseLength
    USE_SKETCHERS=true python henri_bench.py
    MAX_TURNS=10 python henri_bench.py

Environment variables:
    USE_SKETCHERS: Set to 'true' to include the dafny_sketcher hook
    MAX_TURNS: Maximum conversation turns for henri (default: 4)
    MODEL: Model ID to use (e.g., us.anthropic.claude-opus-4-5-20250929-v1:0)
    PROVIDER: LLM provider (e.g., bedrock, google, vertex, ollama)
    KEEP_TMP: Set to 'true' to keep temp files for debugging
"""

import os
import subprocess
import tempfile
import time
import difflib
from pathlib import Path

import driver
import sketcher


# Paths to henri hooks
HENRI_DIR = Path(__file__).parent.parent.parent / 'henri'
HOOKS_DIR = HENRI_DIR / 'hooks'
VFP_HENRI_HOOK = Path(__file__).parent / 'henri.py'

# Temp directory for henri working files
HENRI_TMP_DIR = Path(__file__).parent / 'henri_tmp'


def empty_lemma_body(lemma, program):
    """Create a version of the program with the lemma body emptied."""
    return driver.insert_program_todo(lemma, program, "")


def run_henri(problem_file_path, use_sketcher=False, timeout=300, max_turns=None, model=None, provider=None, keep_tmp=False):
    """
    Run henri as a subprocess to solve the Dafny verification problem.

    Args:
        problem_file_path: Absolute path to the .dfy file with empty lemma body
        use_sketcher: Whether to include the dafny_sketcher hook
        timeout: Timeout in seconds (default 300 = 5 minutes)
        max_turns: Maximum conversation turns for henri (default None = unlimited)
        model: Model ID to use (default None = henri's default)
        provider: LLM provider to use (default None = henri's default)
        keep_tmp: Whether to keep temp files (default False)

    Returns:
        tuple: (success: bool, henri_stats: dict | None, error: str | None, elapsed_time: float)
    """
    filename = Path(problem_file_path).name
    tools_hint = " You have access to dafny_sketcher for induction sketches." if use_sketcher else ""
    prompt = f"Make the file {filename} verify in Dafny. Only add lines; do not delete any line except whitespace. You have access to dafny_verify to check your work.{tools_hint} Verify your solution before finishing."

    # Build hooks list
    hooks = [
        str(HOOKS_DIR / 'dafny.py'),
        str(HOOKS_DIR / 'bench.py'),
    ]

    if use_sketcher:
        hooks.append(str(VFP_HENRI_HOOK))

    # Build command
    cmd = ['henri']
    for hook in hooks:
        cmd.extend(['--hook', hook])

    if max_turns is not None:
        cmd.extend(['--max-turns', str(max_turns)])

    if model is not None:
        cmd.extend(['--model', model])

    if provider is not None:
        cmd.extend(['--provider', provider])

    # Stats file has same base name as problem file but with .json extension
    stats_file = str(Path(problem_file_path).with_suffix('.json'))
    cmd.extend(['--stats-file', stats_file])

    start_time = time.time()
    try:
        # Don't capture output - let it stream to terminal
        result = subprocess.run(
            cmd,
            input=prompt,
            text=True,
            timeout=timeout,
            cwd=str(Path(problem_file_path).parent),
        )
        elapsed = time.time() - start_time

        # Read stats from file
        import json
        henri_stats = None
        try:
            with open(stats_file, 'r') as f:
                henri_stats = json.load(f)
        except:
            pass
        finally:
            if not keep_tmp:
                try:
                    os.unlink(stats_file)
                except:
                    pass

        return True, henri_stats, None, elapsed
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start_time
        return False, None, f"[timeout after {timeout} seconds]", elapsed
    except Exception as e:
        elapsed = time.time() - start_time
        return False, None, f"[error: {e}]", elapsed


def diff_check(original, modified):
    """
    Check that modified only adds lines to original.

    Allows:
    - Insertions (adding new lines)
    - Removing empty/whitespace-only lines

    Args:
        original: Original file content (with empty lemma body)
        modified: Modified file content (henri's output)

    Returns:
        tuple: (valid: bool, reason: str, additions: list[str])
    """
    orig_lines = original.splitlines(keepends=True)
    mod_lines = modified.splitlines(keepends=True)

    matcher = difflib.SequenceMatcher(None, orig_lines, mod_lines)

    additions = []
    bad_deletions = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            continue
        elif tag == 'insert':
            additions.extend(mod_lines[j1:j2])
        elif tag == 'delete':
            # Only flag deletions of non-empty lines
            for line in orig_lines[i1:i2]:
                if line.strip():
                    bad_deletions.append(line)
        elif tag == 'replace':
            # Check if deleted lines were just whitespace
            for line in orig_lines[i1:i2]:
                if line.strip():
                    bad_deletions.append(line)
            # Added lines are fine
            additions.extend(mod_lines[j1:j2])

    if bad_deletions:
        return False, f"Deleted {len(bad_deletions)} non-empty lines", additions

    return True, "Only additions", additions


def lemma1(lemma, program, stats):
    """
    Process a single lemma using henri.

    Args:
        lemma: Lemma dict from sketcher.sketch_done() with keys:
               name, type, status, startLine, insertLine, insertColumn, endLine, endColumn
        program: Full solution file content
        stats: Dictionary to accumulate results
    """
    name = lemma['name']
    print(f'lemma {name}')

    use_sketcher = os.environ.get('USE_SKETCHERS', 'false').lower() in ('true', '1', 'yes')
    max_turns = int(os.environ.get('MAX_TURNS', '4'))
    model = os.environ.get('MODEL')
    provider = os.environ.get('PROVIDER')
    keep_tmp = os.environ.get('KEEP_TMP', 'false').lower() in ('true', '1', 'yes')

    # Step 1: Create problem file (solution with empty lemma body)
    problem_content = empty_lemma_body(lemma, program)

    # Step 2: Ensure temp directory exists and write file there
    HENRI_TMP_DIR.mkdir(exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.dfy',
        delete=False,
        dir=HENRI_TMP_DIR,
        prefix=f'{name}_',
    ) as f:
        f.write(problem_content)
        problem_file = f.name

    try:
        # Step 3: Run henri
        print(f'  Running henri (USE_SKETCHERS={use_sketcher}, MAX_TURNS={max_turns}, MODEL={model}, PROVIDER={provider})...')
        success, henri_stats, error, elapsed = run_henri(problem_file, use_sketcher=use_sketcher, max_turns=max_turns, model=model, provider=provider, keep_tmp=keep_tmp)

        if not success:
            print(f'  :( henri failed: {error}')
            stats[name] = {
                'status': 'henri_error',
                'error': error,
                'elapsed': elapsed,
            }
            return

        turns = henri_stats.get('turns') if henri_stats else None
        print(f'  henri completed in {elapsed:.1f}s (turns={turns})')

        # Step 4: Read back the modified file
        try:
            with open(problem_file, 'r') as f:
                modified_content = f.read()
        except Exception as e:
            print(f'  :( could not read modified file: {e}')
            stats[name] = {
                'status': 'read_error',
                'error': str(e),
                'elapsed': elapsed,
            }
            return

        # Step 5: Diff check - ensure only additions
        diff_valid, diff_reason, additions = diff_check(problem_content, modified_content)

        if not diff_valid:
            print(f'  :( diff check failed: {diff_reason}')
            stats[name] = {
                'status': 'diff_invalid',
                'reason': diff_reason,
                'elapsed': elapsed,
                'henri_stats': henri_stats,
            }
            return

        # Step 6: Verification check
        errors = sketcher.list_errors_for_method(modified_content, name)

        if not errors:
            print(f'  :) solved {name}!')
            stats[name] = {
                'status': 'success',
                'elapsed': elapsed,
                'proof': modified_content,
                'additions': len(additions),
                'henri_stats': henri_stats,
            }
        else:
            print(f'  :( verification failed with {len(errors)} errors')
            stats[name] = {
                'status': 'verify_failed',
                'errors': errors,
                'elapsed': elapsed,
                'proof': modified_content,
                'henri_stats': henri_stats,
            }

    finally:
        # Cleanup temp file unless KEEP_TMP is set
        if keep_tmp:
            print(f'  temp file kept: {problem_file}')
        else:
            try:
                os.unlink(problem_file)
            except:
                pass


def print_stats(stats):
    """Print summary statistics."""
    print('\n' + '=' * 50)
    print('HENRI BENCH RESULTS')
    print('=' * 50)

    # Count by status
    status_counts = {}
    for name, result in stats.items():
        status = result.get('status', 'unknown')
        status_counts[status] = status_counts.get(status, 0) + 1

    print(f'\nTotal lemmas: {len(stats)}')
    print(f'  Success:       {status_counts.get("success", 0)}')
    print(f'  Henri error:   {status_counts.get("henri_error", 0)}')
    print(f'  Diff invalid:  {status_counts.get("diff_invalid", 0)}')
    print(f'  Verify failed: {status_counts.get("verify_failed", 0)}')

    # Print timing stats
    elapsed_times = [r['elapsed'] for r in stats.values() if 'elapsed' in r]
    if elapsed_times:
        print(f'\nTiming:')
        print(f'  Total:   {sum(elapsed_times):.1f}s')
        print(f'  Average: {sum(elapsed_times)/len(elapsed_times):.1f}s')
        print(f'  Max:     {max(elapsed_times):.1f}s')

    # Print turns stats
    turns_list = [r['henri_stats']['turns'] for r in stats.values()
                  if r.get('henri_stats') and r['henri_stats'].get('turns')]
    if turns_list:
        print(f'\nTurns:')
        print(f'  Total:   {sum(turns_list)}')
        print(f'  Average: {sum(turns_list)/len(turns_list):.1f}')
        print(f'  Max:     {max(turns_list)}')

    # List successes
    successes = [name for name, r in stats.items() if r.get('status') == 'success']
    if successes:
        print(f'\nSuccessful: {", ".join(successes)}')

    # List failures with details
    failures = [(name, r) for name, r in stats.items() if r.get('status') != 'success']
    if failures:
        print(f'\nFailures:')
        for name, result in failures:
            status = result.get('status', 'unknown')
            print(f'  {name}: {status}')
            if 'reason' in result:
                print(f'    Reason: {result["reason"]}')
            if 'errors' in result:
                errs = result['errors'][:2]  # First 2 errors
                for err in errs:
                    print(f'    Error: {err}')
                if len(result['errors']) > 2:
                    print(f'    ... and {len(result["errors"]) - 2} more errors')


if __name__ == "__main__":
    import bench_driver
    bench_driver.run(lemma1, print_stats)
