import os
from typing import List

SYSTEM_PROMPT = "You are a Dafny expert." # for Anthropic only

AWS_BEARER_TOKEN_BEDROCK = os.environ.get('AWS_BEARER_TOKEN_BEDROCK')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
OLLAMA_API_KEY = os.environ.get('OLLAMA_API_KEY')
MLX_API_KEY = os.environ.get('MLX_API_KEY')
PROJECT_ID = os.environ.get('PROJECT_ID') or os.environ.get('GOOGLE_CLOUD_PROJECT')
CACHE_LLM = os.environ.get('CACHE_LLM')
DEBUG_LLM = os.environ.get('DEBUG_LLM')
LLM_PROVIDER = os.environ.get('LLM_PROVIDER')
GEMINI_MODEL = os.environ.get('GEMINI_MODEL', "gemini-2.5-flash")
TEMPERATURE = float(os.environ.get('TEMPERATURE', 1.0))

def debug(msg: str):
    if DEBUG_LLM:
        print(f"DEBUG: {msg}")

def dummy_generate(pkg, extra=""):
    # def generate(*args):
    #     raise ValueError(f"Need to install pip package '{pkg}'"+extra)
    # return generate
    raise ValueError(f"Need to install pip package '{pkg}'"+extra)

models = {}
generators = {}

def generate(prompt, max_tokens=1000, temperature=TEMPERATURE, model=None):
    debug(f"Prompt:\n{prompt}")
    return None
generators[None] = generate

if AWS_BEARER_TOKEN_BEDROCK:
    generate = None
    try:
        from anthropic import AnthropicBedrock
    except ModuleNotFoundError:
        generate = dummy_generate('anthropic[bedrock]')
    if generate is None:
        model = os.environ.get('ANTHROPIC_AWS_MODEL')
        if not model:
            claude_model = os.environ.get('CLAUDE_MODEL', 'sonnet3')
            if claude_model == 'opus':
                model = 'us.anthropic.claude-opus-4-1-20250805-v1:0'
            elif claude_model == 'sonnet3':
                model = 'anthropic.claude-3-sonnet-20240229-v1:0'
            elif claude_model == 'sonnet45':
                model = 'global.anthropic.claude-sonnet-4-5-20250929-v1:0'
            elif claude_model == 'sonnet4':
                model = 'global.anthropic.claude-sonnet-4-20250514-v1:0'
            else:
                raise ValueError(f"Invalid Claude model: {claude_model}")
        aws_region = os.environ.get('AWS_REGION', 'us-east-1')
        def generate(prompt, max_tokens=1000, temperature=TEMPERATURE, model=model):
            debug(f"Prompt:\n{prompt}")
            print(f"Sending request to Anthropic AWS (model={model}, max_tokens={max_tokens}, temp={temperature})")

            client = AnthropicBedrock()

            message = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=SYSTEM_PROMPT,
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
            print("Received response from Anthropic AWS")
            print(f"Response:\n{message}")
            return message.content[0].text
        models['claude_aws'] = model
    generators['claude_aws'] = generate

if PROJECT_ID:
    generate = None
    try:
        from anthropic import AnthropicVertex
    except ModuleNotFoundError:
        generate = dummy_generate('anthropic[vertex]')
    if generate is None:
        model = os.environ.get('ANTHROPIC_MODEL', 'claude-sonnet-4-5')
        def generate(prompt, max_tokens=1000, temperature=TEMPERATURE, model=model):
            debug(f"Prompt:\n{prompt}")
            print(f"Sending request to Anthropic Vertex (model={model}, max_tokens={max_tokens}, temp={temperature})")

            client = AnthropicVertex(region="us-east5", project_id=PROJECT_ID)

            message = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=SYSTEM_PROMPT,
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
            print("Received response from Anthropic Vertex")
            print(f"Response:\n{message}")
            return message.content[0].text
        models['claude_vertex'] = model
    generators['claude_vertex'] = generate

    generate = None
    try:
        from google import genai
    except ModuleNotFoundError:
        generate = dummy_generate('google-genai')

    if generate is None:
        def generate(prompt, max_tokens=1000, temperature=TEMPERATURE, model=GEMINI_MODEL):
            print(f"Sending request to Gemini Vertex (model={model}, max_tokens={max_tokens}, temp={temperature})")

            client = genai.Client(vertexai=True, project=PROJECT_ID, location="us-central1")
            response = client.models.generate_content(
                model=model, contents=prompt
            )
            text = response.text
            print("Received response from Google Gemini")
            print(f"Response:\n{text}")
            return text
        models['gemini_vertex'] = GEMINI_MODEL
    generators['gemini_vertex'] = generate

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
        def generate(prompt, max_tokens=1000, temperature=TEMPERATURE, model="gpt-4o"):
            debug(f"Prompt:\n{prompt}")
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
        models['openai'] = model
    generators['openai'] = generate

if ANTHROPIC_API_KEY:
    generate = None
    try:
        import anthropic
    except ModuleNotFoundError:
        generate = dummy_generate('anthropic')
    if generate is None:
        def generate(prompt, max_tokens=1000, temperature=TEMPERATURE, model="claude-3-7-sonnet-20250219"):
            debug(f"Prompt:\n{prompt}")
            debug(f"Sending request to Anthropic (model={model}, max_tokens={max_tokens}, temp={temperature})")

            client = anthropic.Anthropic()

            message = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=SYSTEM_PROMPT,
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
        models['claude'] = model
    generators['claude'] = generate

if GEMINI_API_KEY:
    generate = None
    try:
        from google import genai
    except ModuleNotFoundError:
        generate = dummy_generate('google-genai')
    if generate is None:
        def generate(prompt, max_tokens=1000, temperature=TEMPERATURE, model=GEMINI_MODEL):
            debug(f"Prompt:\n{prompt}")
            debug(f"Sending request to Google Gemini (model={model}, max_tokens={max_tokens}, temp={temperature})")
            
            client = genai.Client(api_key=GEMINI_API_KEY)

            response = client.models.generate_content(
                model=model, contents=prompt
            )
            text = response.text
            debug("Received response from Google Gemini")
            debug(f"Response:\n{text}")
            return text
        models['gemini'] = GEMINI_MODEL
    generators['gemini'] = generate

if OLLAMA_API_KEY:
    generate = None
    try:
        import ollama
    except ModuleNotFoundError:
        generate = dummy_generate('ollama', extra=", or package 'anthropic' while setting ANTHROPIC_API_KEY")
    if generate is None:
        model = os.environ.get('OLLAMA_MODEL', 'gemma3:27b')
        def generate(prompt, max_tokens=1000, temperature=TEMPERATURE, model=model):
            debug(f"Prompt:\n{prompt}")
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
        models['ollama'] = model
    generators['ollama'] = generate

if MLX_API_KEY and (len(generators) < 2 or LLM_PROVIDER == 'mlx'):
    generate = None
    try:
        from mlx_lm import load
        from mlx_lm import generate as mlx_generate
    except ModuleNotFoundError:
        generate = dummy_generate('mlx-lm')
    if generate is None:
        model_name = os.environ.get('MLX_MODEL', 'mlx-community/Qwen2.5-14B-Instruct-4bit')
        model, tokenizer = load(model_name)
        def generate(prompt, max_tokens=1000, temperature=TEMPERATURE, model=model):

            debug(f"Prompt:\n{prompt}")
            debug(f"Sending request to MLX (model={model_name}, max_tokens={max_tokens}, temp={temperature})")

            try:
                response = mlx_generate(model, tokenizer, prompt=prompt)
                debug("Received response from MLX")
                debug(f"Response:\n{response}")
                return response
            except Exception as e:
                debug(f"Error generating response: {e}")
                return None
        models['mlx'] = model_name
    generators['mlx'] = generate

def multiline_input():
    print("Enter your input (end with an empty line):")
    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)
    return "\n".join(lines)

if LLM_PROVIDER=='user':
    def generate(prompt, max_tokens=1000, temperature=TEMPERATURE, model=None):
        print(f"Prompt:\n{prompt}")
        return multiline_input()
    generators['user'] = generate

def pick_generate():
    if LLM_PROVIDER:
        return LLM_PROVIDER, generators[LLM_PROVIDER]
    gs = [(key, generators[key]) for key in generators.keys() if key is not None]
    if gs:
        return gs[0]
    raise ValueError("No generators available")

default_provider, default_generate = pick_generate()

if CACHE_LLM:
    try:
        from joblib import Memory
        
        cache_dir = os.environ.get('CACHE_LLM_DIR', './cache')
        os.makedirs(cache_dir, exist_ok=True)
        
        memory = Memory(cache_dir, verbose=0)
        
        @memory.cache
        def cached_generate_with_config(provider, default_model, prompt, **kwargs):
            generator = generators[provider]
            # Filter out None values to let generator use its own defaults
            filtered_kwargs = {k: v for k, v in kwargs.items() if v is not None}
            return generator(prompt, **filtered_kwargs)

        original_generate = default_generate
        default_model = models[default_provider]
        def cached_default_generate(prompt, **kwargs):
            return cached_generate_with_config(default_provider, default_model, prompt, **kwargs)
        default_generate = cached_default_generate
        
        debug(f"LLM caching enabled with cache directory: {cache_dir}")
        
    except ImportError:
        print("joblib not available, caching disabled")
        pass

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

if __name__ == '__main__':
    print('available providers:', list(generators.keys()))
    print('picked provider:', default_provider)
    print('default model:', models[default_provider])
    import sys
    if len(sys.argv) > 1:
        print(default_generate('Who are you?'))
