import asyncio
import shutil
import re
from typing import List

from agents import Agent, Runner, trace
from agents.mcp import MCPServer, MCPServerStdio

from agents import ItemHelpers, RunResult
from mcp.types import CallToolResult
from pydantic import BaseModel

from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel, set_tracing_disabled

import os

BASE_URL = os.getenv("OPENAI_BASE_URL") or "http://localhost:11434/v1"
API_KEY = os.getenv("OPENAI_API_KEY") or "ollama"
MODEL_NAME = os.getenv("OPENAI_MODEL_NAME") or "qwen3:14b"
client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)
set_tracing_disabled(disabled=True)
model = OpenAIChatCompletionsModel(model=MODEL_NAME, openai_client=client)

class Suggestion(BaseModel):
    code: str
    errors: str

query = "Writes a datatype for arithmetic expressions comprising constants, variables, and binary additions. Then write an evaluator taking an expression and an environment (a function that takes a variable name and returns a number) and returning the number resulting from evaluation. Then write an optimizer taking an expression and returning an expression with all additions by 0 removed. Then prove that the optimizer preserves the semantics as defined by the evaluation function."

SUGGESTION_PROMPT = (
    "/nothink "
    "You are a helpful assistant that develops Dafny code. "
    "Only output the Dafny code."
)

def extract_code(output: str) -> str:
    # Remove anything between <think> </think> tags
    output = re.sub(r'<think>.*?</think>', '', output, flags=re.DOTALL)
    # Extract all code blocks from the output
    pattern = r'```(?:dafny)?\n(.*?)\n```'
    code_blocks = re.findall(pattern, output, re.DOTALL | re.IGNORECASE)
    if code_blocks:
        return '\n\n'.join(code_blocks)
    return output

def extract_response_text(response: CallToolResult) -> str:
    return response.content[0].text

async def suggestion_from_result(mcp_server: MCPServer, output: str) -> Suggestion:
    output = output
    print("Output")
    print(output)
    print("-" * 80)
    code = extract_code(output)
    print("Code")
    print(code)
    print("-" * 80)
    errors = extract_response_text(await mcp_server.call_tool("show-errors", {'fileInput': code}))
    print("Errors")
    print(errors)
    return Suggestion(code=code, errors=errors)

async def make_suggestion(mcp_server: MCPServer, query: str):
    suggestion_agent = Agent(
        name="SuggestionAgent",
        instructions=SUGGESTION_PROMPT,
        model=model
    )
    print(f"Running: {query}")
    result = await Runner.run(suggestion_agent, query, max_turns=1)
    return await suggestion_from_result(mcp_server, result.final_output)

async def pick_from_suggestions(mcp_server: MCPServer, query: str, suggestions: List[Suggestion]):
    pick_agent = Agent(
        name="PickAgent",
        instructions=(
            "You have the following errors for different implementation of a Dafny program. "
            "Based on the errors, pick the number of the best suggestion. "
            "Often, if the errors happen later in the program, then that is a sign that the earlier parts are correct."
        ),
        output_type=int,
        model=model
    )
    prompt = ""
    for i, suggestion in enumerate(suggestions):
        prompt += f"### Errors for Suggestion {i}:\n" + suggestion.errors + "\n"
    result = await Runner.run(pick_agent, prompt, max_turns=1)
    return suggestions[result.final_output_as(int)]

async def repair_suggestion(mcp_server: MCPServer, query: str, suggestion: Suggestion):
    repair_agent = Agent(
        name="RepairAgent",
        instructions=(
            SUGGESTION_PROMPT + "\n"
            "You are given a suggested program and its errors. Repair the errors as needed. "
            "Use the show-errors tool to check your work. "
            "Use the sketch-induction tool to find a suggestion for a lemma proof sketch. "
            "For both of these tools, use the entire code of the program as the fileInput parameter. "
            "For the sketch-induction tool, use the name of the lemma as the methodName parameter. "
        ),
        mcp_servers=[mcp_server],
        model=model
    )
    prompt = "Query: " + query + "\n"
    prompt += "## Suggestion:\n" + suggestion.code + "\n"
    prompt += "### Errors:\n" + suggestion.errors + "\n"
    result = Runner.run_streamed(repair_agent, prompt, max_turns=10)
    print("=== Run starting ===")
    async for event in result.stream_events():
        # We'll ignore the raw responses event deltas
        if event.type == "raw_response_event":
            continue
        # When the agent updates, print that
        elif event.type == "agent_updated_stream_event":
            print(f"Agent updated: {event.new_agent.name}")
            continue
        # When items are generated, print them
        elif event.type == "run_item_stream_event":
            if event.item.type == "tool_call_item":
                print(f"-- Tool {event.item.raw_item.name} was called with arguments: {event.item.raw_item.arguments}")
            elif event.item.type == "tool_call_output_item":
                print(f"-- Tool output: {event.item.output}")
            elif event.item.type == "message_output_item":
                print(f"-- Message output:\n {ItemHelpers.text_message_output(event.item)}")
            else:
                pass  # Ignore other event types
    print("=== Run complete ===")
    return await suggestion_from_result(mcp_server, result.final_output)

async def run(mcp_server: MCPServer):
    suggestions = [await make_suggestion(mcp_server, query) for i in range(3)]
    picked_suggestion = await pick_from_suggestions(mcp_server, query, suggestions)
    suggestion = await repair_suggestion(mcp_server, query, picked_suggestion)
    print("Final code")
    print(suggestion.code)
    print("Final errors")
    print(suggestion.errors)

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