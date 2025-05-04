import asyncio
import shutil
import json

from agents import trace, set_tracing_disabled
from agents.mcp import MCPServer, MCPServerStdio

set_tracing_disabled(disabled=True)

async def run(mcp_server: MCPServer):
    while True:
        tool_name = input("Tool name: ")
        tool_arguments_input = input("Enter JSON or path to JSON file: ")
        tool_arguments_str = tool_arguments_input
        try:
            with open(tool_arguments_input, 'r') as f:
                tool_arguments_str = f.read()
        except Exception as e:
            pass
        try:
            tool_arguments = json.loads(tool_arguments_str)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON format - {e}")
            continue
        for key, value in tool_arguments.items():
            print("Key: ", key)
            print("Value: ", value)
        result = await mcp_server.call_tool(tool_name, tool_arguments)
        print(result)

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