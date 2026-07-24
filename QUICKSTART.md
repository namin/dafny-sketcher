# Quick Start: Scaffolding Paradox Artefact

This guide explains how to set up the environment needed to reproduce the
experiments whose logs live in [`vfp/logs_paradox/`](vfp/logs_paradox/). For the
mapping between individual log files and the commands that produced them, see
[`vfp/logs_paradox/README.md`](vfp/logs_paradox/README.md).

## 1. What the artefact does

The experiments compare LLM-driven Dafny proof repair starting from two seeds:

- an **empty** lemma body, and
- a **skeleton** seed (the top-level case / if structure with empty branches,
  extracted from the known solution).

The repair loop runs the Dafny Sketcher CLI to check errors and an LLM to fill
in proofs. Everything is orchestrated from the `vfp/` directory.

## 2. Prerequisites

You need three things in place: the Dafny toolchain, the Dafny Sketcher CLI,
and the Python environment.

### 2a. Build Dafny and the Sketcher CLI

From the repository root, the simplest path is:

```
./compile.sh
```

This builds the (forked) Dafny language implementation and the Sketcher CLI
(`cli/bin/Release/net8.0/DafnySketcherCli.dll`). See the
[root README](README.md) for the full dev setup, and the
[CLI README](cli/README.md) for building only the CLI:

```
cd cli
dotnet build DafnySketcherCli.csproj -c Release
```

### 2b. Make `dafny` and the Sketcher CLI available

- The benchmark scripts invoke `dafny` (`dafny verify`, `dafny resolve`)
  directly, so the built `dafny` binary must be on your `PATH`.
- The Sketcher CLI is located via `DAFNY_SKETCHER_CLI_DLL_PATH`, which defaults
  to `../cli/bin/Release/net8.0/DafnySketcherCli.dll` (relative to `vfp/`). Set
  it explicitly if your build lives elsewhere:

```
export DAFNY_SKETCHER_CLI_DLL_PATH=/abs/path/to/cli/bin/Release/net8.0/DafnySketcherCli.dll
```

### 2c. Python environment

The scripts use `joblib` for caching plus one LLM client library
(`anthropic`, `google.genai`, `openai`, or `ollama`) depending on the model you
target. Install the ones you need, e.g.:

```
pip install joblib anthropic google-genai openai ollama
```

See [`vfp/llm.py`](vfp/llm.py) (search for `os.environ`) and
[`vfp/README.md`](vfp/README.md) for the full list of supported providers and
options.

## 3. Configure the LLM

Pick a provider by exporting its API key, and optionally its model. The
experiments in this directory used Gemini, Claude Sonnet, and Claude Opus.
Examples:

```
# Anthropic (Claude)
export ANTHROPIC_API_KEY=your_key

# Google (Gemini)
export GEMINI_API_KEY=your_key
export GEMINI_MODEL=gemini-2.5-flash   # optional; this is the default
```

If no key is set, Ollama is assumed to be available locally. The
process-supervision script takes the model explicitly via `--model`
(e.g. `--model anthropic/claude-opus-4-6`).

Optional caching (recommended for reruns):

```
export CACHE_LLM=1     # cache LLM calls per provider/model/prompt
export CACHE_DAFNY=1   # cache Dafny Sketcher CLI calls
```

## 4. Data

The DafnyBench subset used by the `_dafnybench` runs lives in
[`vfp/DafnyBench/`](vfp/DafnyBench/). The default (non-DafnyBench) runs use the
solution files under `vfp/bench/*_solution.dfy`.

Note: three lemmas (`NthAppendA`, `NthRev`, `NthXtr`) come from a DafnyBench
file that does not resolve and cannot be repaired by this workflow; they appear
in some earlier logs but are excluded later.

## 5. Run the tool (whole-proof repair)

For a quick start, a single-file smoke test is enough to confirm the artefact
runs end to end. Run it from the `vfp/` directory after the setup above:

```
python bench_paradox.py --file <one DafnyBench file>
```

This runs the 3x whole-proof repair loop on that file, comparing the empty seed
and the skeleton seed. You should see, per lemma, the extracted skeleton
followed by `[empty]` / `[skeleton]` repair progress and a final summary of
solved rates.

To run the full DafnyBench subset (this can take **over an hour** depending on
your machine and LLM latency), drop the `--file` flag and use the glob pattern:

```
python bench_paradox.py --glob-pattern "DafnyBench/*.dfy"
```

Corresponding logs from our runs: `log_gemini_paradox.txt`,
`paradox_sonnet46_dafnybench_new.txt`, `paradox_opus46_dafnybench_new.txt`
(all in [`vfp/logs_paradox/`](vfp/logs_paradox/)).

## 6. Reproduce the full results

The other experiments (process supervision, case repair, on-track / no-sketcher
variants, and the top-k analysis) along with the exact commands and the log
file each one produced are documented in
[`vfp/logs_paradox/README.md`](vfp/logs_paradox/README.md).
