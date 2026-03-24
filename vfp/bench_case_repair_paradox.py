"""
Benchmark script comparing empty-vs-skeleton seeds with case repair.

For each lemma whose solution has a top-level case/if shape:
  1. Run repair pipeline from empty seed
  2. Run the same pipeline from skeleton seed

Repair pipeline per seed:
  1. Seed feasibility check
  2. One whole-proof repair attempt
  3. Case-by-case repair
  4. Final whole-proof repair loop

Also provides available lemma signatures as context to the LLM.
"""

import re
import subprocess
import time
from llm import default_generate as _base_generate
import driver
import sketcher
import os
import sys
from fine import format_errors
from driver import prompt_begin_dafny, extract_dafny_program
from bench_paradox import extract_skeleton
from dafnybench_lemma_tracking import PARADOX_LEMMAS


# ---------------------------------------------------------------------------
# LLM call with transient-error retry
# ---------------------------------------------------------------------------

_RETRY_DELAYS = [1, 5, 10]
_CURRENT_LEMMA_STATS = None
_CURRENT_LEMMA_KEY = None


def _is_transient_llm_error(exc: Exception) -> bool:
    """Return True for transient LLM/API failures worth retrying."""
    msg = str(exc).lower()
    transient_markers = (
        '429',
        'resource_exhausted',
        'RESOURCE_EXHAUSTED',
        'server disconnected without sending a response',
        'connection reset',
        'connection aborted',
        'timed out',
        'timeout',
        'temporarily unavailable',
        'service unavailable',
        'bad gateway',
        'remote protocol error',
    )
    return any(marker in msg for marker in transient_markers)


def _set_current_lemma_stats(stats: dict, lemma_key: str) -> None:
    """Set per-lemma context so generate() can attribute LLM calls."""
    global _CURRENT_LEMMA_STATS, _CURRENT_LEMMA_KEY
    _CURRENT_LEMMA_STATS = stats
    _CURRENT_LEMMA_KEY = lemma_key


def _clear_current_lemma_stats() -> None:
    """Clear per-lemma LLM-call attribution context."""
    global _CURRENT_LEMMA_STATS, _CURRENT_LEMMA_KEY
    _CURRENT_LEMMA_STATS = None
    _CURRENT_LEMMA_KEY = None


def _record_llm_call() -> None:
    """Increment LLM call counter for the current lemma."""
    if _CURRENT_LEMMA_STATS is None or _CURRENT_LEMMA_KEY is None:
        return
    calls = _CURRENT_LEMMA_STATS.setdefault('llm_calls_per_lemma', {})
    calls[_CURRENT_LEMMA_KEY] = calls.get(_CURRENT_LEMMA_KEY, 0) + 1


def generate(*args, **kwargs):
    """Wrapper around base LLM generate with retries for transient API errors."""
    attempts = len(_RETRY_DELAYS) + 1
    for attempt in range(1, attempts + 1):
        try:
            result = _base_generate(*args, **kwargs)
            _record_llm_call()
            return result
        except Exception as e:
            if not _is_transient_llm_error(e):
                raise
            if attempt >= attempts:
                print('LLM transient error persisted after retries; skipping this generation attempt.')
                return ''
            delay = _RETRY_DELAYS[attempt - 1]
            print(
                f'LLM transient error (attempt {attempt}/{attempts}): {e}. '
                f'Retrying in {delay}s...'
            )
            time.sleep(delay)


# ---------------------------------------------------------------------------
# Sketch helpers
# ---------------------------------------------------------------------------

def _unique_stats_key(name: str, stats: dict) -> str:
    """Return a unique key derived from *name* that is not already in *stats*.

    When two lemmas from different files share the same name the second (and
    subsequent) occurrences get keys ``name__2``, ``name__3``, … so that no
    result is silently overwritten.
    """
    if name not in stats:
        return name
    i = 2
    while f'{name}__{i}' in stats:
        i += 1
    return f'{name}__{i}'


# ---------------------------------------------------------------------------
# Syntax validation
# ---------------------------------------------------------------------------

def check_dafny_syntax(program_text: str) -> list[str]:
    """Run ``dafny resolve`` and return error lines (empty list if syntactically valid)."""
    file_path = sketcher.write_content_to_temp_file(program_text)
    if not file_path:
        return []
    try:
        result = subprocess.run(
            ['dafny', 'resolve', file_path],
            capture_output=True, text=True, timeout=15,
        )
        output = (result.stdout or '') + (result.stderr or '')
        return [ln for ln in output.splitlines() if 'Error' in ln]
    except Exception:
        return []
    finally:
        try:
            os.unlink(file_path)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Helpers: lemma signatures, body/case parsing, replacement
# ---------------------------------------------------------------------------

def extract_lemma_signatures(program: str) -> str:
    """Return a formatted string of every lemma signature in *program*."""
    lines = program.splitlines()
    sigs: list[str] = []
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped.startswith('lemma ') or stripped.startswith('lemma{'):
            sig_lines = [lines[i].rstrip()]
            j = i + 1
            while j < len(lines):
                ns = lines[j].strip()
                if ns.startswith(('requires', 'ensures', 'decreases')):
                    sig_lines.append(lines[j].rstrip())
                    j += 1
                else:
                    break
            sigs.append('\n'.join(sig_lines))
            i = j
        else:
            i += 1
    return '\n'.join(sigs) if sigs else '(none)'


def find_top_level_cases(body_text: str, body_open_line: int) -> list[dict]:
    """
    Parse top-level proof branches inside a lemma body.

    Handles two flavours:
      * **match/case** – ``case X => { … }``
      * **if/else**    – ``if cond { … } else { … }``

    *body_open_line* is the **1-based** line of the opening ``{``.

    Each returned dict contains:
      * ``header``       – the stripped branch header
      * ``text``         – full text of the branch (header + body)
      * ``start`` / ``end`` – 1-based program line range (inclusive)
      * ``sketch_start`` / ``sketch_end`` – 0-based line indices in *body_text*
    """
    cases = _find_match_cases(body_text, body_open_line)
    if cases:
        print(f"  ## DEBUG: found {len(cases)} match/case branch(es)")
        return cases
    branches = _find_if_else_branches(body_text, body_open_line)
    if branches:
        print(f"  ## DEBUG: found {len(branches)} if/else branch(es)")
    return branches


def _find_match_cases(body_text: str, body_open_line: int) -> list[dict]:
    """Find ``case … =>`` branches (braced or unbraced match)."""
    lines = body_text.splitlines()
    depth = 0
    case_depth = None
    case_starts: list[int] = []

    for i, line in enumerate(lines):
        stripped = line.strip()
        if re.match(r'case\s+', stripped) and '=>' in stripped:
            if case_depth is None:
                case_depth = depth
            if depth == case_depth:
                case_starts.append(i)
        for ch in line:
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1

    if not case_starts:
        return []

    cases = []
    for idx, start in enumerate(case_starts):
        end = case_starts[idx + 1] - 1 if idx + 1 < len(case_starts) else len(lines) - 1
        while end > start and not lines[end].strip():
            end -= 1
        cases.append({
            'header': lines[start].strip(),
            'text': '\n'.join(lines[start : end + 1]),
            'start': body_open_line + 1 + start,
            'end': body_open_line + 1 + end,
            'sketch_start': start,
            'sketch_end': end,
        })
    return cases


def _find_if_else_branches(body_text: str, body_open_line: int) -> list[dict]:
    """
    Find ``if / else if / else`` branches.

    For a body like::

        if cond {        ← branch 0  (lines 0-2, includes ``} else {``)
          body1;
        } else {         ← branch 1  (lines 2-4)
          body2;
        }

    Adjacent branches *overlap* on the ``} else …`` transition line so that
    each branch is self-contained text the LLM can read and reproduce.
    """
    lines = body_text.splitlines()
    branch_starts: list[int] = []
    if_depth = None

    depth = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if if_depth is None:
            if stripped.startswith('if ') and '{' in stripped:
                if_depth = depth
                branch_starts.append(i)
        else:
            if depth == if_depth + 1 and re.match(r'\}\s*else\b', stripped):
                branch_starts.append(i)
        for ch in line:
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1

    if len(branch_starts) < 2:
        return []

    # Find the closing line of the whole if/else chain
    depth = if_depth
    chain_end = len(lines) - 1
    for i in range(branch_starts[0], len(lines)):
        for ch in lines[i]:
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
        if i > branch_starts[0] and depth == if_depth:
            chain_end = i
            break

    branches = []
    for idx, start in enumerate(branch_starts):
        # Each branch runs up to (and including) the next transition line,
        # so adjacent branches share the ``} else {`` boundary.
        if idx + 1 < len(branch_starts):
            end = branch_starts[idx + 1]
        else:
            end = chain_end
        while end > start and not lines[end].strip():
            end -= 1
        branches.append({
            'header': lines[start].strip(),
            'text': '\n'.join(lines[start : end + 1]),
            'start': body_open_line + 1 + start,
            'end': body_open_line + 1 + end,
            'sketch_start': start,
            'sketch_end': end,
        })
    return branches


def errors_in_range(errors, start_line, end_line):
    """Filter errors whose line falls within [start_line, end_line] (1-based)."""
    return [(l, c, m, s) for (l, c, m, s) in errors if start_line <= l <= end_line]


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

def prompt_case_repair(program: str, name: str, case_text: str,
                       errors: list, lemma_sigs: str) -> str:
    return f"""You are fixing a specific branch in an inductive proof of lemma {name} in a Dafny program.

Program:
{program}

Available lemma signatures in the file (you may call any of these as helper lemmas):
{lemma_sigs}

The specific proof branch that needs fixing is:
{case_text}

The errors in this branch are:
{format_errors(errors)}

Please provide the full fixed body of lemma {name} (without the outer braces), with this branch corrected and all other branches left intact.
{prompt_begin_dafny("lemma")}"""


def prompt_statement_repair(program: str, name: str, case_text: str,
                            stmt: str, errors: list, lemma_sigs: str) -> str:
    return f"""You are fixing a specific failing statement in an inductive proof of lemma {name} in a Dafny program.

Program:
{program}

Available lemma signatures in the file (you may call any of these as helper lemmas):
{lemma_sigs}

The proof branch containing the error is:
{case_text}

The specific statement that is failing:
{stmt}

The errors at this statement:
{format_errors(errors)}

Please provide the full fixed body of lemma {name} (without the outer braces), with the failing statement corrected and all other branches left intact.
{prompt_begin_dafny("lemma")}"""


def prompt_lemma_implementer(program: str, name: str, e: list, lemma_sigs: str) -> str:
    return f"""You are implementing a lemma in a Dafny program that is specified but not fully implemented. The current program is
{program}

Available lemma signatures in the file (you may call any of these as helper lemmas):
{lemma_sigs}

The lemma to implement is {name}. {prompt_begin_dafny("lemma")}
The errors in the work-in-progress lemma are:
{format_errors(e)}"""


# ---------------------------------------------------------------------------
# Case-level and statement-level repair
# ---------------------------------------------------------------------------

def try_fix_case(p, lemma, init_p, current_sketch, name, case, case_errors, lemma_sigs,
                 syntax_feedback=''):
    """One LLM attempt to fix the entire *case*. Returns updated sketch or ``None``."""
    note = (f"Your previous generation attempt had syntax errors:\n{syntax_feedback}\n\n"
            if syntax_feedback else '')
    prompt = note + prompt_case_repair(p, name, case['text'], case_errors, lemma_sigs)
    r = generate(prompt)
    candidate_sketch = extract_dafny_program(r)
    if candidate_sketch is None:
        return None

    candidate_p = driver.insert_program_todo(lemma, init_p, candidate_sketch)
    candidate_errors = sketcher._list_errors_for_method_core(candidate_p, name)
    if not candidate_errors:
        return candidate_sketch

    # Accept if errors *within this case* decreased or stayed the same
    new_cases = find_top_level_cases(candidate_sketch, lemma['insertLine'])
    for nc in new_cases:
        if nc['header'] == case['header']:
            new_ce = errors_in_range(candidate_errors, nc['start'], nc['end'])
            if len(new_ce) <= len(case_errors):
                return candidate_sketch
            break
    return None


def try_fix_statements(p, lemma, init_p, current_sketch, name, case, case_errors, lemma_sigs,
                       syntax_feedback=''):
    """
    Iteratively fix individual failing statements inside *case*.

    For each error line, ask the LLM to repair that statement (outputting the
    full lemma body).  Accept any change that doesn't increase total errors.
    Returns updated sketch or ``None``.
    """
    working_sketch = current_sketch

    for _attempt in range(2):
        wp = driver.insert_program_todo(lemma, init_p, working_sketch)
        all_errors = sketcher._list_errors_for_method_core(wp, name)
        if not all_errors:
            return working_sketch

        cases = find_top_level_cases(working_sketch, lemma['insertLine'])
        target = next((c for c in cases if c['header'] == case['header']), None)
        if target is None:
            return None

        ce = errors_in_range(all_errors, target['start'], target['end'])
        if not ce:
            return working_sketch

        err = ce[0]
        err_line = err[0]
        wp_lines = wp.splitlines()
        stmt = wp_lines[err_line - 1].strip() if 0 < err_line <= len(wp_lines) else ''
        line_errors = [e for e in ce if e[0] == err_line]

        note = (f"Your previous generation attempt had syntax errors:\n{syntax_feedback}\n\n"
                if syntax_feedback else '')
        syntax_feedback = ''
        prompt = note + prompt_statement_repair(wp, name, target['text'], stmt, line_errors, lemma_sigs)
        r = generate(prompt)
        candidate = extract_dafny_program(r)
        if candidate is None:
            continue

        cp = driver.insert_program_todo(lemma, init_p, candidate)
        new_errors = sketcher._list_errors_for_method_core(cp, name)

        if not new_errors:
            return candidate
        if len(new_errors) <= len(all_errors):
            working_sketch = candidate

    fp = driver.insert_program_todo(lemma, init_p, working_sketch)
    fe = sketcher._list_errors_for_method_core(fp, name)
    if not fe:
        return working_sketch
    if working_sketch != current_sketch:
        return working_sketch
    return None


# ---------------------------------------------------------------------------
# Top-level case-by-case repair driver
# ---------------------------------------------------------------------------

def case_repair(lemma, init_p, sketch, name, lemma_sigs):
    """
    Try to repair the induction sketch case-by-case.

    Returns the repaired sketch text, or ``None`` on failure.
    """
    current_sketch = sketch
    syntax_feedback = ''

    for _iteration in range(2):
        # Case-repair stage 1: evaluate current sketch and collect verifier errors.
        p = driver.insert_program_todo(lemma, init_p, current_sketch)
        e = sketcher._list_errors_for_method_core(p, name)
        if not e:
            return current_sketch

        # Case-repair stage 2: parse top-level branches to localize fixes.
        body_text = current_sketch
        body_open = lemma['insertLine']
        cases = find_top_level_cases(body_text, body_open)
        if not cases:
            print('  No cases found in sketch')
            return None

        failing = None
        for case in cases:
            ce = errors_in_range(e, case['start'], case['end'])
            if ce:
                failing = (case, ce)
                break

        if failing is None:
            print('  Errors not inside any case – cannot repair case-by-case')
            return None

        # Case-repair stage 3: attempt full-branch repair for the first failing case.
        case, case_errors = failing
        print(f"  Case `{case['header']}`: {len(case_errors)} error(s)")

        fixed = try_fix_case(p, lemma, init_p, current_sketch, name,
                             case, case_errors, lemma_sigs, syntax_feedback)
        syntax_feedback = ''
        if fixed is not None:
            syntax_errs = check_dafny_syntax(driver.insert_program_todo(lemma, init_p, fixed))
            if syntax_errs:
                syntax_feedback = '\n'.join(syntax_errs)
                print('  -> syntax error in case fix, rejecting:')
                print('\n'.join(f'     {ln}' for ln in syntax_errs))
                continue
            current_sketch = fixed
            print('  -> case-level fix applied')
            continue

        # Case-repair stage 4: if branch-level fix fails, repair failing statements.
        fixed = try_fix_statements(p, lemma, init_p, current_sketch, name,
                                   case, case_errors, lemma_sigs, syntax_feedback)
        syntax_feedback = ''
        if fixed is not None:
            syntax_errs = check_dafny_syntax(driver.insert_program_todo(lemma, init_p, fixed))
            if syntax_errs:
                syntax_feedback = '\n'.join(syntax_errs)
                print('  -> syntax error in statement fix, rejecting:')
                print('\n'.join(f'     {ln}' for ln in syntax_errs))
                continue
            current_sketch = fixed
            print('  -> statement-level fix applied')
            continue

        print(f"  -> could not fix case `{case['header']}`")
        return None

    # Case-repair stage 5: final verification gate before returning success.
    p = driver.insert_program_todo(lemma, init_p, current_sketch)
    e = sketcher._list_errors_for_method_core(p, name)
    return current_sketch if not e else None


def whole_proof_repair_phase(lemma, init_p, p, e, name, lemma_sigs,
                             seed_label: str, num_iters: int, phase_label: str):
    """Run up to ``num_iters`` whole-proof LLM repair attempts."""
    syntax_feedback = ''
    last_candidate = None
    for _ in range(num_iters):
        note = (f"Your previous generation attempt had syntax errors:\n{syntax_feedback}\n\n"
                if syntax_feedback else '')
        syntax_feedback = ''
        prompt = note + prompt_lemma_implementer(p, name, e, lemma_sigs)
        r = generate(prompt)
        x = extract_dafny_program(r)
        if x is None:
            continue
        last_candidate = x
        candidate_p = driver.insert_program_todo(lemma, init_p, x)
        syntax_errs = check_dafny_syntax(candidate_p)
        if syntax_errs:
            syntax_feedback = '\n'.join(syntax_errs)
            print(f'  [{seed_label}] -> syntax error in candidate ({phase_label}), not accepting')
            continue
        p = candidate_p
        e = sketcher._list_errors_for_method_core(p, name)
        if not e:
            return True, x, last_candidate, p, e
    return False, '', last_candidate, p, e


# ---------------------------------------------------------------------------
# Per-seed repair runner
# ---------------------------------------------------------------------------

def _run_repair_pipeline_for_seed(lemma, init_p, name, lemma_sigs, seed_body: str,
                                  seed_label: str, stats: dict, stats_key: str) -> dict:
    """
    Run the full repair pipeline for one seed mode.

    Returns a dict with fields including:
      solved, status, iteration, proof, failed_proof, llm_calls
    """
    mode_stats_key = f'{stats_key}::{seed_label}'
    _set_current_lemma_stats(stats, mode_stats_key)

    result = {
        'seed': seed_label,
        'solved': False,
        'status': 'unsolved',
        'iteration': None,
        'proof': None,
        'failed_proof': None,
        'llm_calls': 0,
    }

    # Seed feasibility check
    p = driver.insert_program_todo(lemma, init_p, seed_body)
    e = sketcher.list_errors_for_method(p, name)
    if not e:
        print(f'  [{seed_label}] empty proof works')
        result['solved'] = True
        result['status'] = f'{seed_label}_seed'
        result['proof'] = seed_body
    else:
        # After seed feasibility, run one broad whole-proof repair attempt.
        print(f'  [{seed_label}] Attempting whole-proof LLM repair first...')
        solved, proof, last_candidate, p, e = whole_proof_repair_phase(
            lemma, init_p, p, e, name, lemma_sigs,
            seed_label=seed_label, num_iters=1, phase_label='whole-proof (post-seed)',
        )
        if solved:
            print(f'  [{seed_label}] initial whole-proof repair works')
            result['solved'] = True
            result['status'] = 'whole_proof_loop'
            result['proof'] = proof
        else:
            result['failed_proof'] = last_candidate

        # Then try narrow case-by-case repair (when there is branch structure).
        if not result['solved'] and seed_body.strip():
            print(f'  [{seed_label}] Immediate whole-proof repair did not verify; attempting case-by-case repair...')
            case_result = case_repair(lemma, init_p, seed_body, name, lemma_sigs)
            if case_result is not None:
                print(f'  [{seed_label}] case-by-case repair works')
                result['solved'] = True
                result['status'] = 'case_repair'
                result['proof'] = case_result

        # End with a shorter whole-proof repair fallback loop (2 iterations).
        if not result['solved']:
            print(f'  [{seed_label}] Case-by-case repair did not verify; attempting final whole-proof repair...')
            solved, proof, last_candidate, p, e = whole_proof_repair_phase(
                lemma, init_p, p, e, name, lemma_sigs,
                seed_label=seed_label, num_iters=2, phase_label='whole-proof (final)',
            )
            if solved:
                print(f'  [{seed_label}] final whole-proof repair works')
                result['solved'] = True
                result['status'] = 'whole_proof_loop'
                result['proof'] = proof
            else:
                print(f'  [{seed_label}] all failed :(')
                result['failed_proof'] = last_candidate

    mode_calls = stats.get('llm_calls_per_lemma', {}).get(mode_stats_key, 0)
    result['llm_calls'] = mode_calls
    if result['solved']:
        result['iteration'] = mode_calls
    return result


# ---------------------------------------------------------------------------
# Main benchmark entry point
# ---------------------------------------------------------------------------

def lemma1(lemma, p, stats):
    # Stage 0: initialize per-lemma context and bookkeeping.
    # Count lemmas as soon as we start processing them so totals remain accurate
    # even if execution exits early before per-lemma stats are fully populated.
    stats['total_lemmas_seen'] = stats.get('total_lemmas_seen', 0) + 1
    init_p = p
    name = lemma['name']
    print('lemma', name)

    # Deduplicate stats keys when the same lemma name appears in multiple files.
    stats_key = _unique_stats_key(name, stats)
    if stats_key != name:
        print(f'  Duplicate lemma name {name!r} – using stats key {stats_key!r}')
    lemma_names = stats.setdefault('lemma_names', [])
    if stats_key not in lemma_names:
        lemma_names.append(stats_key)

    try:
        lemma_sigs = extract_lemma_signatures(init_p)

        # Build skeleton from known solution body. Skip if not case/if-shaped.
        lines = init_p.splitlines()
        body_text = '\n'.join(lines[lemma['insertLine']:lemma['endLine'] - 1])
        skeleton = extract_skeleton(body_text)
        if skeleton is None:
            print("  solution has no case/if structure, skipping")
            stats[stats_key] = {'empty': None, 'skeleton': None, 'skipped': True}
            return

        print("  [empty] running repair pipeline...")
        empty_result = _run_repair_pipeline_for_seed(
            lemma, init_p, name, lemma_sigs, '', 'empty', stats, stats_key
        )

        print("  [skeleton] running repair pipeline...")
        skeleton_result = _run_repair_pipeline_for_seed(
            lemma, init_p, name, lemma_sigs, skeleton, 'skeleton', stats, stats_key
        )

        stats[stats_key] = {
            'empty': empty_result,
            'skeleton': skeleton_result,
            'skipped': False,
        }
        stats['solve_path_empty_' + stats_key] = empty_result['status']
        stats['solve_path_skeleton_' + stats_key] = skeleton_result['status']
        stats['llm_calls_empty_' + stats_key] = empty_result['llm_calls']
        stats['llm_calls_skeleton_' + stats_key] = skeleton_result['llm_calls']
        if empty_result.get('proof') is not None:
            stats['proof_empty_' + stats_key] = empty_result['proof']
        if skeleton_result.get('proof') is not None:
            stats['proof_skeleton_' + stats_key] = skeleton_result['proof']
        if empty_result.get('failed_proof') is not None:
            stats['failed_proof_empty_' + stats_key] = empty_result['failed_proof']
        if skeleton_result.get('failed_proof') is not None:
            stats['failed_proof_skeleton_' + stats_key] = skeleton_result['failed_proof']
    finally:
        _clear_current_lemma_stats()


# ---------------------------------------------------------------------------
# Stats reporting
# ---------------------------------------------------------------------------

def print_summary_stats(stats):
    entries = {
        k: v for k, v in stats.items()
        if isinstance(v, dict) and 'empty' in v and 'skeleton' in v
    }
    total = len(entries)
    skipped = len([v for v in entries.values() if v.get('skipped')])
    considered = total - skipped

    empty_solved = len([
        v for v in entries.values()
        if not v.get('skipped') and v['empty'] and v['empty'].get('solved')
    ])
    skeleton_solved = len([
        v for v in entries.values()
        if not v.get('skipped') and v['skeleton'] and v['skeleton'].get('solved')
    ])

    both_solved = len([
        v for v in entries.values()
        if not v.get('skipped')
        and v['empty'] and v['empty'].get('solved')
        and v['skeleton'] and v['skeleton'].get('solved')
    ])
    only_empty = len([
        v for v in entries.values()
        if not v.get('skipped')
        and v['empty'] and v['empty'].get('solved')
        and not (v['skeleton'] and v['skeleton'].get('solved'))
    ])
    only_skeleton = len([
        v for v in entries.values()
        if not v.get('skipped')
        and v['skeleton'] and v['skeleton'].get('solved')
        and not (v['empty'] and v['empty'].get('solved'))
    ])
    neither = len([
        v for v in entries.values()
        if not v.get('skipped')
        and not (v['empty'] and v['empty'].get('solved'))
        and not (v['skeleton'] and v['skeleton'].get('solved'))
    ])

    print('total lemmas:', total)
    print('skipped (no case/if structure):', skipped)
    print('considered:', considered)
    print('  empty solved:', empty_solved)
    print('  skeleton solved:', skeleton_solved)
    print('  both solved:', both_solved)
    print('  only empty:', only_empty)
    print('  only skeleton:', only_skeleton)
    print('  neither:', neither)

    skeleton_faster = 0
    empty_faster = 0
    same_iter = 0
    for v in entries.values():
        if v.get('skipped'):
            continue
        ev = v['empty']
        sv = v['skeleton']
        if not (ev and sv and ev.get('solved') and sv.get('solved')):
            continue
        ei = ev.get('iteration')
        si = sv.get('iteration')
        if ei is None or si is None:
            continue
        if si < ei:
            skeleton_faster += 1
        elif ei < si:
            empty_faster += 1
        else:
            same_iter += 1
    if both_solved > 0:
        print('  among solved-by-both:')
        print('    skeleton faster:', skeleton_faster)
        print('    empty faster:', empty_faster)
        print('    same iterations:', same_iter)


def print_stats(stats):
    print('FINISHED RUNNING THE BENCH')
    print_summary_stats(stats)
    print('--- per-lemma ---')
    entries = {
        k: v for k, v in stats.items()
        if isinstance(v, dict) and 'empty' in v and 'skeleton' in v
    }
    for name, v in sorted(entries.items()):
        if v.get('skipped'):
            print(f'  {name}: skipped')
            continue
        e = v['empty']
        s = v['skeleton']
        print(
            f"  {name}: "
            f"empty=({e['status']}, iter={e['iteration']}, calls={e['llm_calls']})  "
            f"skeleton=({s['status']}, iter={s['iteration']}, calls={s['llm_calls']})"
        )
    print_summary_stats(stats)


if __name__ == '__main__':
    import bench_driver
    paradox_only = False
    if '--paradox-only' in sys.argv:
        paradox_only = True
        sys.argv = [arg for arg in sys.argv if arg != '--paradox-only']

    if paradox_only:
        print('Running with paradox-only lemma filter')
        bench_driver.run(lemma1, print_stats, only_lemmas=PARADOX_LEMMAS)
    else:
        bench_driver.run(lemma1, print_stats)
