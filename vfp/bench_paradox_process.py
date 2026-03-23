"""
Benchmark testing the "process supervision" hypothesis for the scaffolding paradox.

Hypothesis: giving the LLM the correct sketch (outcome) doesn't help, but
simulating the *thinking process* that would generate the sketch might help.

For each lemma with a case/if structure:
  1. Mode A: repair from empty (baseline)
  2. Mode B: repair from skeleton (original paradox)
  3. Mode C: ask LLM to explain WHY this sketch is correct (process),
             then repair with that explanation in context

This tests whether process > outcome for Dafny proof generation.

Usage:
    # Run all three modes (A, B, C) with Opus 4.6:
    python bench_paradox_process.py --model anthropic/claude-opus-4-6 \\
        --glob-pattern 'DafnyBench/*.dfy'

    # Run only Mode C (process supervision):
    python bench_paradox_process.py --model anthropic/claude-opus-4-6 \\
        --process-only --glob-pattern 'DafnyBench/*.dfy'

    # Limit LLM calls: 2 = 1 explanation + 1 repair attempt:
    python bench_paradox_process.py --model anthropic/claude-opus-4-6 \\
        --process-only --max-llm-calls 2 --glob-pattern 'DafnyBench/*.dfy'
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import bench_driver
import driver
import sketcher
from fine import format_errors
from driver import extract_dafny_program
from bench_paradox import extract_skeleton, prompt_lemma_implementer

_repo_root = Path(__file__).resolve().parent.parent


def make_generate(model: str, temperature: float = 0.0) -> Callable[..., str]:
    """Build a litellm-based generate function for the given model."""
    import litellm

    def generate(prompt, max_tokens=4000, temperature=temperature, model=model):
        print(f"[LLM] Querying {model} ...", flush=True)
        resp = litellm.completion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
            timeout=600,
        )
        result = resp.choices[0].message.content
        print(f"[LLM] Response received", flush=True)
        return result

    return generate


# ---------------------------------------------------------------------------
# Process supervision: ask LLM to explain the skeleton
# ---------------------------------------------------------------------------

PROCESS_PROMPT = """You are a Dafny proof expert. A lemma needs to be proved, and someone has
proposed the following proof skeleton (just the case structure with empty branches):

Program:
{program}

Lemma to prove: {name}

The skeleton (case structure with empty branches) is:
{skeleton}

Please explain step by step:
1. WHY this particular case analysis is the right approach for this lemma
2. What property or structure of the data/function definitions makes this case split necessary
3. For each branch, what the key proof obligation is and what technique (induction, helper lemma call, assertion, etc.) would discharge it
4. Any invariants or key insights that connect the preconditions to the postconditions through this case structure

Be specific about the Dafny functions and predicates involved. This explanation will be used to guide a proof search."""


def repair_loop(
    lemma: dict,
    init_p: str,
    start_body: str,
    name: str,
    generate: Callable[..., str],
    n_iterations: int = 3,
    prompt_prefix: str = "",
) -> tuple[int | None, str]:
    """Run n_iterations of LLM repair starting from start_body.

    If prompt_prefix is non-empty, it is prepended to each repair prompt
    (used for process supervision mode).

    Returns (iteration, proof) on success, (-1, start_body) if start_body
    already verifies, or (None, last_attempt) on failure.
    """
    p = driver.insert_program_todo(lemma, init_p, start_body)
    e = sketcher.list_errors_for_method(p, name)
    if not e:
        return (-1, start_body)

    last_x = start_body
    for i in range(n_iterations):
        base_prompt = prompt_lemma_implementer(p, name, e)
        prompt = prompt_prefix + base_prompt if prompt_prefix else base_prompt
        r = generate(prompt)
        x = extract_dafny_program(r)
        if x is None:
            continue
        last_x = x
        p = driver.insert_program_todo(lemma, init_p, x)
        e = sketcher.list_errors_for_method(p, name)
        if not e:
            return (i, x)

    return (None, last_x)


# ---------------------------------------------------------------------------
# Main benchmark entry point
# ---------------------------------------------------------------------------

def lemma1(lemma: dict, p: str, stats: dict) -> None:
    init_p = p
    name = lemma['name']

    print('lemma', name)

    # Extract the skeleton from the solution body
    lines = init_p.splitlines()
    body_text = '\n'.join(lines[lemma['insertLine']:lemma['endLine']-1])
    skeleton = extract_skeleton(body_text)
    if skeleton is None:
        print("  solution has no case/if structure, skipping")
        stats[name] = {'empty': None, 'skeleton': None, 'process': None, 'skipped': True}
        return

    print(f"  skeleton:\n{skeleton}")

    # Check empty proof first
    xp = driver.insert_program_todo(lemma, init_p, "")
    e = sketcher.list_errors_for_method(xp, name)
    if not e:
        print("  empty proof works (trivial)")
        stats[name] = {'empty': -1, 'skeleton': -1, 'process': -1, 'skipped': False}
        return

    generate = _generate
    n_iter = _n_iterations

    # --- Mode A & B: empty and skeleton repair ---
    if not _process_only:
        print("  [empty] starting repair loop...")
        empty_iter, empty_proof = repair_loop(lemma, init_p, "", name, generate, n_iter)
        print(f"  [empty] {'solved at iteration ' + str(empty_iter) if empty_iter is not None else 'failed'}")

        print("  [skeleton] starting repair loop...")
        skel_iter, skel_proof = repair_loop(lemma, init_p, skeleton, name, generate, n_iter)
        print(f"  [skeleton] {'solved at iteration ' + str(skel_iter) if skel_iter is not None else 'failed'}")
    else:
        empty_iter = skel_iter = None
        empty_proof = skel_proof = ""

    # --- Mode C: process explanation + repair ---
    print("  [process] generating explanation...")
    explanation = ""
    explanation_error = None
    try:
        explanation = generate(
            PROCESS_PROMPT.format(program=init_p, name=name, skeleton=skeleton),
            max_tokens=4000,
        )
        print(f"  [process] explanation generated ({len(explanation)} chars)")
    except Exception as ex:
        explanation_error = str(ex)
        print(f"  [process] explanation failed: {ex}")

    if explanation:
        n_repair = (_max_llm_calls - 1) if _max_llm_calls else n_iter
        prefix = f"""Before attempting the proof, here is an analysis of the proof strategy that should work for this lemma:

{explanation}

Now, using this analysis to guide your proof:

"""
        print(f"  [process] starting repair loop (max {n_repair} repairs)...")
        proc_iter, proc_proof = repair_loop(
            lemma, init_p, "", name, generate, n_repair, prompt_prefix=prefix)
        print(f"  [process] {'solved at iteration ' + str(proc_iter) if proc_iter is not None else 'failed'}")
    else:
        proc_iter, proc_proof = None, ""

    entry = {
        'empty': empty_iter,
        'skeleton': skel_iter,
        'process': proc_iter,
        'skipped': False,
    }
    if explanation_error:
        entry['process_error'] = explanation_error
    if empty_iter is not None:
        entry['proof_empty'] = empty_proof
    if skel_iter is not None:
        entry['proof_skeleton'] = skel_proof
    if proc_iter is not None:
        entry['proof_process'] = proc_proof
    if explanation:
        entry['explanation'] = explanation

    stats[name] = entry
    save_run_state(stats)


# ---------------------------------------------------------------------------
# Stats reporting
# ---------------------------------------------------------------------------

def print_summary_stats(stats: dict) -> None:
    entries = {k: v for k, v in stats.items() if isinstance(v, dict)}
    total = len(entries)
    skipped = considered = 0
    empty_solved = skel_solved = proc_solved = neither_es = 0
    proc_only_vs_skel = skel_only_vs_proc = both_ps = 0
    proc_fewer = skel_fewer = same = 0
    proc_only_vs_empty = 0

    for v in entries.values():
        if v.get('skipped'):
            skipped += 1
            continue
        considered += 1
        e, s, p = v.get('empty'), v.get('skeleton'), v.get('process')
        if e is not None: empty_solved += 1
        if s is not None: skel_solved += 1
        if p is not None: proc_solved += 1
        if e is None and s is None: neither_es += 1
        if p is not None and s is None: proc_only_vs_skel += 1
        elif s is not None and p is None: skel_only_vs_proc += 1
        elif p is not None and s is not None:
            both_ps += 1
            if p < s: proc_fewer += 1
            elif s < p: skel_fewer += 1
            else: same += 1
        if p is not None and e is None: proc_only_vs_empty += 1

    print(f'\ntotal lemmas: {total}')
    print(f'skipped (no case/if structure): {skipped}')
    print(f'considered: {considered}')
    print(f'  empty solved:    {empty_solved}')
    print(f'  skeleton solved: {skel_solved}')
    print(f'  process solved:  {proc_solved}')
    print(f'  neither (empty/skel): {neither_es}')

    # NOTE: when --process-only is used, skeleton=None for all non-trivial
    # lemmas, so "process-only solved" counts all process successes.
    print(f'\n  === Process vs Skeleton ===')
    print(f'  process-only solved: {proc_only_vs_skel}')
    print(f'  skeleton-only solved: {skel_only_vs_proc}')
    if both_ps > 0:
        # NOTE: process iteration 0 costs 2 LLM calls (explain + 1 repair)
        # while skeleton iteration 0 costs 1. This compares proof-attempt
        # count, not total LLM cost.
        print(f'  both solved: {both_ps}')
        print(f'    process fewer iterations: {proc_fewer}')
        print(f'    skeleton fewer iterations: {skel_fewer}')
        print(f'    same iterations: {same}')

    print(f'\n  === Process vs Empty ===')
    print(f'  process-only solved: {proc_only_vs_empty}')


def save_run_state(stats: dict) -> None:
    payload = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "config": {
            "llm_model": _model_name,
            "n_iterations": _n_iterations,
            "max_llm_calls": _max_llm_calls,
            "process_only": _process_only,
        },
        "stats": stats,
    }
    try:
        with open(_out_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=True)
    except Exception as e:
        print(f"failed to save: {e}")


def print_stats(stats: dict) -> None:
    print('\nFINISHED RUNNING THE BENCH')
    print_summary_stats(stats)

    entries = {k: v for k, v in stats.items() if isinstance(v, dict)}
    print('\n--- per-lemma results ---')
    for name, v in sorted(entries.items()):
        if v.get('skipped'):
            continue
        err = f"  error={v['process_error'][:50]}" if v.get('process_error') else ""
        print(f'  {name}: empty={v.get("empty")}  skeleton={v.get("skeleton")}  process={v.get("process")}{err}')

    print_summary_stats(stats)
    save_run_state(stats)


# Module-level state, set in __main__.
_generate: Callable[..., str]
_model_name: str | None = None
_n_iterations: int = 3
_max_llm_calls: int | None = None
_process_only: bool = False
_out_path: str = str(_repo_root / "vfp" / "bench_paradox_process_latest.json")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(_repo_root / ".env")
    load_dotenv(_repo_root / "vfp" / ".env")

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--model', type=str, default=None,
                        help='litellm model (e.g. anthropic/claude-opus-4-6)')
    parser.add_argument('--out', type=str, default=_out_path)
    parser.add_argument('--iterations', type=int, default=3)
    parser.add_argument('--process-only', action='store_true',
                        help='Only run Mode C (process), skip A and B')
    parser.add_argument('--max-llm-calls', type=int, default=None,
                        help='Max LLM calls per lemma for process mode '
                             '(e.g. 2=explain+1repair, 3=explain+2repairs)')
    args, remaining = parser.parse_known_args()

    _model_name = args.model
    _n_iterations = args.iterations
    _max_llm_calls = args.max_llm_calls
    _process_only = args.process_only
    _out_path = args.out

    if args.model:
        _generate = make_generate(args.model)
    else:
        from llm import default_generate
        _generate = default_generate

    sys.argv = [sys.argv[0]] + remaining
    bench_driver.run(lemma1, print_stats)
