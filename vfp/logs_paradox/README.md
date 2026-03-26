# Logs

- `paradox_` were run with `python bench_paradox.py`
- `_dafnybench` were run with `--glob-pattern "DafnyBench/*.dfy"`
- `_ontrack` ot `_on_track` were run with `--on-track`
- `no_sketchers` were run with `export USE_SKETCHERS=false`
- repair loop baseline is run with `python bench_feedback.py`


# Scaffolding Paradox Instructions

All commands should be run from the `vfp` directory.

Note that some of the logs consider the following lemmas for repair:

- NthAppendA
- NthRev
- NthXtr

These lemmas come from a DafnyBench file that does not resolve, and therefore they cannot be repaired using our workflow. We exclude these lemmas in later logs.

## Setting the model

See the [parent README](../README.md) for LLM configuration (API keys, model env vars, etc.).

## Whole-proof repair 

The command below runs the 3x whole-proof repair loop pipeline on the DafnyBench subset, comparing empty seed and skeleton seed. You must specify the model before running it.

```
python bench_paradox.py --glob-pattern "DafnyBench/*.dfy"
```

Our whole-proof repair logs are included here:
- [`log_gemini_paradox.txt`](../logs_paradox/log_gemini_paradox.txt) (Gemini)
- [`paradox_sonnet46_dafnybench_new.txt`](../logs_paradox/paradox_sonnet46_dafnybench_new.txt) (Claude Sonnet)
- [`paradox_opus46_dafnybench_new.txt`](../logs_paradox/paradox_opus46_dafnybench_new.txt) (Claude Opus)

## Process supervision logs

- `process_` were run with [`bench_paradox_process.py`](../bench_paradox_process.py) `--process-only`
- The explanation prompt sees only the empty-branch skeleton, not the correct proof body

| Log file | Model | Command |
|----------|-------|---------|
| `process_opus46_dafnybench.json` | Opus 4.6 | `python bench_paradox_process.py --model anthropic/claude-opus-4-6 --process-only --glob-pattern 'DafnyBench/*.dfy'` |
| `process_sonnet46_dafnybench.json` | Sonnet 4.6 | `python bench_paradox_process.py --model anthropic/claude-sonnet-4-6 --process-only --glob-pattern 'DafnyBench/*.dfy'` |


## Case repair

The command below runs the case repair pipeline on the DafnyBench subset, comparing empty seed and skeleton seed. You must specify the model before running it.

```
python bench_case_repair_paradox.py --glob-pattern "DafnyBench/*.dfy" --paradox-only
```

Our case repair log using Gemini 2.5 Flash Lite is available here: [`log_gemini_case_repair_paradox.txt`](../logs_paradox/log_gemini_case_repair_paradox.txt).

### Case repair top-k analysis

The top-k analysis restricts the statistics to the top k proofs with longest reference solutions, that cannot also be solved by an empty body.

Run this command to get top-k statistics (e.g., k = 30) for the case repair log [`log_gemini_case_repair_paradox.txt`](../logs_paradox/log_gemini_case_repair_paradox.txt) (default file path). The k parameter can be varied via the option `--top-k`.

```
python run_top_lemma_analysis.py --top-k 30
```

Similarly, the command below collects the solved rates from the [`log_gemini_paradox.txt`](../logs_paradox/log_gemini_paradox.txt) log.

```
python run_top_lemma_analysis.py --top-k 30 --log-file "logs_paradox/log_gemini_paradox.txt"
```