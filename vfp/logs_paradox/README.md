# Logs

- `paradox_` were run with `python bench_paradox.py`
- `_dafnybench` were run with `--glob-pattern "DafnyBench/*.dfy"`
- `_ontrack` ot `_on_track` were run with `--on-track`
- `no_sketchers` were run with `export USE_SKETCHERS=false`
- repair loop baseline is run with `python bench_feedback.py`

## Process supervision logs

- `process_` were run with [`bench_paradox_process.py`](../bench_paradox_process.py) `--process-only`
- The explanation prompt sees only the empty-branch skeleton, not the correct proof body

| Log file | Model | Command |
|----------|-------|---------|
| `process_opus46_dafnybench.json` | Opus 4.6 | `python bench_paradox_process.py --model anthropic/claude-opus-4-6 --process-only --glob-pattern 'DafnyBench/*.dfy'` |
| `process_sonnet46_dafnybench.json` | Sonnet 4.6 | `python bench_paradox_process.py --model anthropic/claude-sonnet-4-6 --process-only --glob-pattern 'DafnyBench/*.dfy'` |
