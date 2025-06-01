import os
from typing import List

ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
OLLAMA_API_KEY = os.environ.get('OLLAMA_API_KEY')

DEBUG_LLM = os.environ.get('DEBUG_LLM')

def debug(msg: str):
    if DEBUG_LLM:
        print(f"DEBUG: {msg}")

def dummy_generate(pkg, extra=""):
    # def generate(*args):
    #     raise ValueError(f"Need to install pip package '{pkg}'"+extra)
    # return generate
    raise ValueError(f"Need to install pip package '{pkg}'"+extra)

generators = {}

def generate(prompt, max_tokens=1000, temperature=1.0, model=None):
    debug(f"Prompt:\n{prompt}")
    return None
generators[None] = generate

if OPENAI_API_KEY:
    generate = None
    try:
        import openai
    except ModuleNotFoundError:
        generate = dummy_generate('openai')
    if generate is None:
        OPENAI_BASE_URL = os.environ.get('OPENAI_BASE_URL')
        if OPENAI_BASE_URL:
            openai.base_url = OPENAI_BASE_URL
        def generate(prompt, max_tokens=1000, temperature=1.0, model="gpt-4o"):
            debug(f"Sending request to OpenAI (model={model}, max_tokens={max_tokens}, temp={temperature})")

            completion = openai.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
            )
            response = completion.choices[0].message.content
            debug("Received response from OpenAI")
            debug(f"Response:\n{response}")
            return response
    generators['openai'] = generate

if ANTHROPIC_API_KEY:
    generate = None
    try:
        import anthropic
    except ModuleNotFoundError:
        generate = dummy_generate('anthropic')
    if generate is None:
        def generate(prompt, max_tokens=1000, temperature=1.0, model="claude-3-7-sonnet-20250219"):
            debug(f"Sending request to Anthropic (model={model}, max_tokens={max_tokens}, temp={temperature})")

            client = anthropic.Anthropic()

            message = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system="You are a Dafny expert.",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            )
            debug("Received response from Anthropic")
            debug(f"Response:\n{message}")
            return message.content[0].text

    generators['claude'] = generate

if GEMINI_API_KEY:
    generate = None
    try:
        from google import genai
    except ModuleNotFoundError:
        generate = dummy_generate('google-genai')
    if generate is None:
        def generate(prompt, max_tokens=1000, temperature=1.0, model="gemini-2.5-flash-preview-04-17"):
            debug(f"Sending request to Google Gemini (model={model}, max_tokens={max_tokens}, temp={temperature})")
            
            client = genai.Client(api_key=GEMINI_API_KEY)

            response = client.models.generate_content(
                model='gemini-2.0-flash', contents=prompt
            )
            text = response.text
            debug("Received response from Google Gemini")
            debug(f"Response:\n{text}")
            return text

    generators['gemini'] = generate

if OLLAMA_API_KEY:
    generate = None
    try:
        import ollama
    except ModuleNotFoundError:
        generate = dummy_generate('ollama', extra=", or package 'anthropic' while setting ANTHROPIC_API_KEY")
    if generate is None:
        model = os.environ.get('OLLAMA_MODEL', 'gemma3:27b-it-qat')
        def generate(prompt, max_tokens=1000, temperature=1.0, model=model):
            debug(f"Sending request to Ollama (model={model}, max_tokens={max_tokens}, temp={temperature})")

            try:
                response = ollama.generate(
                    model=model, prompt=prompt,
                    options={
                        'max_tokens': max_tokens,
                        'temperature': temperature
                    }
                )
                debug("Received response from Ollama")
                debug(f"Response:\n{response['response']}")
                return response['response']
            except Exception as e:
                debug(f"Error generating response: {e}")
                return None

    generators['ollama'] = generate

def pick_generate():
    gs = [generators[key]for key in generators.keys() if key is not None]
    if gs:
        return gs[0]
    raise ValueError("No generators available")

default_generate = pick_generate()


def extract_code_blocks(response: str) -> List[str]:
    """Extract code blocks from LLM response, removing markdown and explanations."""
    if not response:
        return []
    if "```" in response:
        lines = response.split("```")[1:]
        lines = [lines[i] for i in range(0, len(lines)) if i % 2 == 0]
        lines = ["\n".join(line.split('\n')[1:]) if '\n' in line else line for line in lines]
        blocks = lines
    #elif "`" in response:
    #    lines = response.split("`")[1:]
    #    lines = [lines[i] for i in range(0, len(lines)) if i % 2 == 0]
    #    lines = ["\n".join(line) if '\n' in line else line for line in lines]
    #    blocks = lines
    else:
        code = response.strip()
        blocks = [code]
    return blocks

def extract_dafny_program(text: str) -> str:
    blocks = extract_code_blocks(text)
    return blocks[0] if blocks else None

if __name__ == '__main__':
    print(generators.keys())
