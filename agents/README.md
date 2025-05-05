# Dafny Sketcher Agents

The agents rely on the Dafny Sketcher MCP.

## Setup

- Make sure the [MCP](../mcp) is built.
- In your Python environment, `pip install weave openai-agents`.
- Make sure the environment variable `OPENAI_API_KEY` is set.

## Run

- Run example with `python main.py`.
- The traces for the program are collected at https://platform.openai.com/traces.

- The `main_ollama_*` variants can be run with Ollama or another OpenAI-compatible server.
- Leave as is for Ollama running locally.
- To try them instead with the main OpenAI server, export the following environment variables:
  - `export OPENAI_BASE_URL=https://api.openai.com/v1`
  - `export OPENAI_MODEL_NAME=gpt-4o`
  - `export OPENAI_API_KEY=...`
