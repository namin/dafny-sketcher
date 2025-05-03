import { McpServer, ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

import { exec } from 'child_process';
import { writeFile } from 'fs/promises';

// TODO: Make this configurable
const cli_dll = "/Users/namin/code/cld/dafny-sketcher/cli//bin/Release/net8.0/DafnySketcherCli.dll ";

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

async function dafnySketcher(fileContent: string, args: string): Promise<string> {
    const filePath = 'tmp.dfy';
    var ok = await writeFileContent(filePath, fileContent);
    if (!ok) {
        return "Error writing file";
    }
    
    // Use Promise to handle the exec callback
    return new Promise<string>((resolve, reject) => {
        exec('dotnet '+cli_dll+" --file tmp.dfy "+args, (error, stdout, stderr) => {
            if (error) {
                resolve("Error running Dafny Sketcher");
                return;
            }
            if (stderr) {
                resolve("Error from Dafny Sketcher");
                return;
            }
            resolve(stdout);
        });
    });
};

server.tool("sketch-induction",
  { fileContent: z.string(), methodName: z.string() },
  async ({ fileContent, methodName }) => {
    const result = await dafnySketcher(fileContent, "--sketch induction --method " + methodName);
    return {
      content: [{ type: "text", text: result }]
    };
  }
);

// Start receiving messages on stdin and sending messages on stdout
const transport = new StdioServerTransport();
await server.connect(transport);