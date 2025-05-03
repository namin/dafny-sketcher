import { McpServer, ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

import { exec } from 'child_process';
import { writeFile } from 'fs/promises';
import { join } from 'path';
import { tmpdir } from 'os';
import { existsSync } from "fs";

const cli_dll = process.env.DAFNY_SKETCHER_CLI_DLL_PATH || "../cli//bin/Release/net8.0/DafnySketcherCli.dll ";

async function writeFileInput(fileInput: string): Promise<string | null> {
  if (existsSync(fileInput)) {
    return fileInput;
  }
  try {
    const tempDir = tmpdir();
    const filePath = join(tempDir, 'tmp.dfy');
    await writeFile(filePath, fileInput, 'utf8');
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

async function dafnySketcher(fileInput: string, args: string): Promise<string> {
    var filePath = await writeFileInput(fileInput);
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
    { fileInput: z.string() },
    async ({ fileInput }) => {
      const result = await dafnySketcher(fileInput, "--sketch errors");
      return {
        content: [{ type: "text", text: result || "OK" }]
      };
    }
  );

server.tool("sketch-induction",
  { fileInput: z.string(), methodName: z.string() },
  async ({ fileInput, methodName }) => {
    const result = await dafnySketcher(fileInput, "--sketch induction --method " + methodName);
    return {
      content: [{ type: "text", text: result }]
    };
  }
);

// Start receiving messages on stdin and sending messages on stdout
const transport = new StdioServerTransport();
await server.connect(transport);