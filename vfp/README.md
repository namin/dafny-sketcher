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
