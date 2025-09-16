import llm
from typing import Dict

def repair(program: str, sketch: str, lemma_name: str, config=None) -> str:
    """
    Try to repair a failing inductive sketch using the chosen LLM.
    Returns a new sketch string (may still be invalid).
    """
    provider, gen = llm.pick_generate()
    prompt = f"""
You are a Dafny expert. A proof sketch for lemma `{lemma_name}` failed.
Here is the Dafny program context:

{program}

Here is the failing proof sketch:

{sketch}

Please provide a corrected Dafny proof body for lemma `{lemma_name}`.
Return only valid Dafny code for the body (no explanations).
"""
    response = gen(prompt)
    blocks = llm.extract_code_blocks(response)
    return blocks[0] if blocks else response


def generate_proof(program: str, lemma: Dict, config=None) -> str:
    """
    Ask the LLM to generate a proof from scratch for the given lemma.
    """
    provider, gen = llm.pick_generate()
    prompt = f"""
You are a Dafny expert. Here is a program:

{program}

Please complete the proof for lemma `{lemma['name']}` by providing a Dafny proof body.
Return only valid Dafny code for the body (no explanations)..
"""
    response = gen(prompt)
    blocks = llm.extract_code_blocks(response)
    return blocks[0] if blocks else response
