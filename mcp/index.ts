import { McpServer, ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

// Create an MCP server
const server = new McpServer({
  name: "Dafny Sketcher",
  version: "1.0.0"
});

const dafnySketcher = function(fileContent: string, args: string) {
    return "TODO";
};

server.tool("sketch-induction",
  { fileContent: z.string(), methodName: z.string() },
  async ({ fileContent, methodName }) => ({
    content: [{ type: "text", text: dafnySketcher(fileContent, "--sketch induction --method " + methodName)}]
  })
);

// Start receiving messages on stdin and sending messages on stdout
const transport = new StdioServerTransport();
await server.connect(transport);