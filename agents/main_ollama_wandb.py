import asyncio
import shutil

from agents import Agent, Runner, trace
from agents.mcp import MCPServer, MCPServerStdio

from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel, set_tracing_disabled

import os

BASE_URL = os.getenv("OPENAI_BASE_URL") or "http://localhost:11434/v1"
API_KEY = os.getenv("OPENAI_API_KEY") or "ollama"
MODEL_NAME = os.getenv("OPENAI_MODEL_NAME") or "qwen3:14b"

import weave
from weave.integrations.openai_agents.openai_agents import WeaveTracingProcessor
from agents import set_trace_processors
weave.init("openai-agents")
set_trace_processors([WeaveTracingProcessor()])

client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)
set_tracing_disabled(disabled=True)

async def run(mcp_server: MCPServer):
    agent = Agent(
        model=OpenAIChatCompletionsModel(model=MODEL_NAME, openai_client=client),
        name="Assistant",
        instructions=f"""/nothink
        Create Dafny programs with functional code and verified properties through lemma.
        Use the dafny-sketcher MCP to help with proof automation, like inductive sketches, and also to verify your suggestions.
        The fileInput parameter to the Dafny Sketcher MCP tools should be your entire code so far.
        The sketch-induction tool takes an additional methodName parameter for the name of the method in your fileInpt code whose proof will be sketched.
        Only return code that verifies using the dafny-sketcher MCP show-errors tool.
        Use the MCP show-errors tool after each definition.
        Always provide the entire code so far to the Dafny Sketcher MCP.""",
        mcp_servers=[mcp_server],
    )

    message = "Writes a datatype for arithmetic expressions comprising constants, variables, and binary additions. Then write an evaluator taking an expression and an environment (a function that takes a variable name and returns a number) and returning the number resulting from evaluation. Then write an optimizer taking an expression and returning an expression with all additions by 0 removed. Then prove that the optimizer preserves the semantics as defined by the evaluation function."
    print("\n" + "-" * 40)
    print(f"Running: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)

async def main():
    async with MCPServerStdio(
        cache_tools_list=True,
        params={"command": "node", "args": ["../mcp/build/index.js"]},
    ) as server:
        with trace(workflow_name="Dafny Sketcher"):
            await run(server)


if __name__ == "__main__":
    if not shutil.which("node"):
        raise RuntimeError("node is not installed")

    asyncio.run(main())
