# Dafny Sketcher VFP (Verified Functional Programming)

VFP relies on the Dafny Sketcher CLI -- see [sketcher.py](sketcher.py).

VFP uses LLM services, importing one of `google.genai`, `openai`, `anthropic`, `ollama` -- see [llm.py](llm.py).

Currently, there are three solvers:
- [driver.py](driver.py) which also contain all the code surrounding a solver
- [mcts.py](mcts.py) which recapitulates the approach from [VerMCTS](https://github.com/namin/llm-verified-with-monte-carlo-tree-search) but using more principled structured editing (and sketching!) instead of ad-hoc left-to-right editing
- [fine.py](fine.py) which features finer-grained edits, for example, to fill in each case in inductive sketch as separate edits.

The file [vermcts.json](vermcts.json) contains the raw prompts from VerMCTS in the format used by DafnySynth, part of [dafny-annotator](https://github.com/metareflection/dafny-annotator).
The [bench](bench) directory contains starting points (as `_spec` or as `_buggy`) and solutions (as `_solution`).
These problems are already well within reach of Claude Code, so we should only consider the first step as a catch up.
