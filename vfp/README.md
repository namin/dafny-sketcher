# Dafny Sketcher VFP (Verified Functional Programming)

VFP relies on the Dafny Sketcher CLI -- see [sketcher.py](sketcher.py).

VFP uses LLM services, importing one of `google.genai`, `openai`, `anthropic`, `ollama` -- see [llm.py](llm.py). Search for `os.environ` to see what you can set.

Caching is available through `joblib`. Options include:
- `CACHE_LLM` to cache LLM calls, per distinct provider/model/prompt.
- `CACHE_DAFNY` to cache Dafny Sketcher CLI calls.

Some solvers here:
- [driver.py](driver.py) which also contain all the code surrounding a solver
- [mcts.py](mcts.py) which recapitulates the approach from [VerMCTS](https://github.com/namin/llm-verified-with-monte-carlo-tree-search) but using more principled structured editing (and sketching!) instead of ad-hoc left-to-right editing
- [fine.py](fine.py) which features finer-grained edits, for example, to fill in each case in inductive sketch as separate edits.
- The `bench_` files also show some solvers and orchestration loops.

The file [vermcts.json](vermcts.json) contains the raw prompts from VerMCTS in the format used by DafnySynth, part of [dafny-annotator](https://github.com/metareflection/dafny-annotator).
The [bench](bench) directory contains starting points (as `_spec` or as `_buggy`) and solutions (as `_solution`).
These problems are already well within reach of Claude Code, so we should only consider the first step as a catch up.

Additional projects:
- [dafny-tasker](https://github.com/metareflection/dafny-tasker): create annotation tasks for training [dafny-annotator](https://github.com/metareflection/dafny-tasker); supersedes [gendata.py](gendata.py)
- [dafny-admitter](https://github.com/metareflection/dafny-admitter): make failure points explicit
- [dafny-poetry](https://github.com/metareflection/dafny-poetry): orchestrate proving recursively
- [henri](https://github.com/metareflection/henri): agent CLI with explicit control via tools, permissions, and hooks

## Instructions to run `bench_poetry`

### in one shell, run the dafny-annotator oracle
- Choose the LLM configuration as follows:
```
export MLX_API_KEY=mlx
export MLX_MODEL=metareflection/dafny-annotator-vfp-4B
```
Run `python llm.py --test` as a sanity check.
- Run the annotation server: `uvicorn annotator_server:app --host 127.0.0.1 --port 8000 --log-level debug`.
### in another shell
- Choose an LLM configuration from [llm.py](llm.py). For example:
```
export OLLAMA_API_KEY=ollama
export OLLAMA_MODEL=gemma3:12b
```
- Probably `export USE_LLM=false` to just try with the inductive sketcher and oracle but without additional LLMs.
- `export DAFNY_ANNOTATOR_SERVER=http://localhost:8000` matching your first shell.
- Try a small run: `python bench_poetry.py --lemma flattenCorrect --lemma Insert_New_Min --lemma ReverseLength --lemma HeapHeightBound`.
  This should score 2/4 for solving `flattenCorrect` and `ReverseLength`.
