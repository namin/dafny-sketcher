# Dafny Sketcher MCP

This Dafny Sketcher MCP builds on the Dafny Sketcher CLI, and exposes certain CLI functionality to MCP clients such as Claude and Cursor.

## Building

- `npm run build`

## Testing

- ` npx @modelcontextprotocol/inspector node build/index.js`

## MCP Client Configuration

Edit your MCP client configuration, e.g.,
`$HOME/Library/Application Support/Claude/claude_desktop_config.json`.

Below, replace `$DAFNY_SKETCHER_PATH` with the path to your dafny-sketcher repo.

```
{
  "mcpServers": {
    "dafny-sketcher": {
      "command": "node",
      "args": ["$DAFNY_SKETCHER_PATH/mcp/build/index.js"],
      "env": {
        "DAFNY_SKETCHER_CLI_DLL_PATH": "$DAFNY_SKETCHER_PATH/cli/bin/Release/net8.0/DafnySketcherCli.dll"
      }
    }
  }
}
```