# Quick Start: Scaffolding Paradox Artefact

This guide explains how to set up the environment needed to reproduce the
experiments whose logs live in [`vfp/logs_paradox/`](vfp/logs_paradox/). For the
mapping between individual log files and the commands that produced them, see
[`vfp/logs_paradox/README.md`](vfp/logs_paradox/README.md).

## Quick start with Docker (recommended)

A prebuilt image bundles everything needed for this artefact: the forked Dafny
toolchain (with the z3 solver), the Dafny Sketcher CLI, and the Python
environment for the benchmark scripts. This is the fastest way to get running
and avoids building Dafny from source. If you prefer to build the toolchain
yourself, skip to [section 2](#2-prerequisites).

The image is multi-architecture: it runs natively on both Intel/AMD (`amd64`)
and Apple Silicon / ARM (`arm64`) hosts.

### 1. Pull the image

```
docker pull akravc/dafny-sketcher:latest
```

### 2. Run it, passing your LLM API key at runtime

```
# Anthropic (Claude)
docker run --rm -it -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY akravc/dafny-sketcher

# or Google (Gemini)
docker run --rm -it -e GEMINI_API_KEY=$GEMINI_API_KEY akravc/dafny-sketcher
```

You land in `/app/vfp` with `dafny`, `dafny-sketcher-cli`, and `python` already
on the `PATH` and configured (`DAFNY_SKETCHER_CLI_DLL_PATH` is set, and
`CACHE_LLM` / `CACHE_DAFNY` caching is enabled).

### 3. Smoke test

From the container prompt (see [section 5](#5-run-the-tool-whole-proof-repair)
for details):

```
python bench_paradox.py --file DafnyBench/AssertivePrograming_tmp_tmpwf43uz0e_DivMode_Unary.dfy
```

When the command finishes running, you will see the message "FINISHED RUNNING THE BENCH" 
and the printed solve count summary for this run (4 lemmas considered, 4 solved by both 
approaches).

### Optional: keep caches/results on the host

Mount a host directory so the joblib caches (and any outputs) survive between
runs:

```
docker run --rm -it \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  -v "$PWD/cache:/app/vfp/cache" \
  akravc/dafny-sketcher
```

### Building the image from source instead of pulling

```
docker build -t dafny-sketcher .          # native to your machine
# or target a specific architecture:
docker buildx build --platform linux/arm64 --load -t dafny-sketcher .
```

## 1. What the artefact does

The experiments compare LLM-driven Dafny proof repair starting from two seeds:

- an **empty** lemma body, and
- a **skeleton** seed (the top-level case / if structure with empty branches,
  extracted from the known solution).

The repair loop runs the Dafny Sketcher CLI to check errors and an LLM to fill
in proofs. Everything is orchestrated from the `vfp/` directory.

## 2. Building from Source

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
python bench_paradox.py --file DafnyBench/AssertivePrograming_tmp_tmpwf43uz0e_DivMode_Unary.dfy
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
