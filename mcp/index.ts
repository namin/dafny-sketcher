import { McpServer, ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

import { exec } from 'child_process';
import { writeFile } from 'fs/promises';
import { join } from 'path';
import { tmpdir } from 'os';

const cli_dll = process.env.DAFNY_SKETCHER_CLI_DLL_PATH || "../cli//bin/Release/net8.0/DafnySketcherCli.dll ";

async function writeFileContent(content: string) {
  try {
    const tempDir = tmpdir();
    const filePath = join(tempDir, 'tmp.dfy');
    await writeFile(filePath, content, 'utf8');
    return filePath;
  } catch (err) {
    return null;
  }
}

// Create an MCP server
const server = new McpServer({
  name: "Dafny Sketcher",
  version: "1.0.0"
});

async function dafnySketcher(fileContent: string, args: string): Promise<string> {
    var filePath = await writeFileContent(fileContent);
    if (!filePath) {
        return "Error writing file";
    }
    
    return new Promise<string>((resolve, reject) => {
        exec('dotnet '+cli_dll+" --file "+filePath+" "+args, (error, stdout, stderr) => {
            if (error) {
                resolve("Error running Dafny Sketcher: "+error.message);
                return;
            }
            if (stderr) {
                resolve("Error from Dafny Sketcher: "+stderr);
                return;
            }
            resolve(stdout);
        });
    });
};

server.tool("show-errors",
    { fileContent: z.string() },
    async ({ fileContent }) => {
      const result = await dafnySketcher(fileContent, "--sketch errors");
      return {
        content: [{ type: "text", text: result || "OK" }]
      };
    }
  );

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