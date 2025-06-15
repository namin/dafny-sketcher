# Dafny Sketcher VFP (Verified Functional Programming)

VFP relies on the Dafny Sketcher CLI -- see [sketcher.py](sketcher.py).

VFP uses LLM services, importing one of `google.genai`, `openai`, `anthropic`, `ollama` -- see [llm.py](llm.py).

Currently, there are two solvers, one in [driver.py](driver.py) which also contain all the code surrounding a solver,
and [mcts.py](mcts.py which recapitulates the approach from [VerMCTS](https://github.com/namin/llm-verified-with-monte-carlo-tree-search),
but using more principled structured editing (and sketching!) instead of ad-hoc left-to-right editing.

The file [vermcts.json](vermcts.json) contains the raw prompts from VerMCTS in the format used by DafnySynth, part of [dafny-annotator](https://github.com/metareflection/dafny-annotator).
