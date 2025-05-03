import { McpServer, ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

import { writeFile } from 'fs/promises';

async function writeFileContent(filePath: string, content: string) {
  try {
    await writeFile(filePath, content, 'utf8');  // Overwrites by default
    return true;
  } catch (err) {
    return false;
  }
}

// Create an MCP server
const server = new McpServer({
  name: "Dafny Sketcher",
  version: "1.0.0"
});

async function dafnySketcher(fileContent: string, args: string) {
    const filePath = 'tmp.dfy';
    const ok = await writeFileContent(filePath, fileContent);
    return String(ok);
};

server.tool("sketch-induction",
  { fileContent: z.string(), methodName: z.string() },
  async ({ fileContent, methodName }) => ({
    content: [{ type: "text", text: await dafnySketcher(fileContent, "--sketch induction --method " + methodName)}]
  })
);

// Start receiving messages on stdin and sending messages on stdout
const transport = new StdioServerTransport();
await server.connect(transport);