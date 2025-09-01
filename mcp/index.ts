import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { execFile } from 'child_process';
import { writeFile, unlink } from 'fs/promises';
import { join, isAbsolute, resolve, normalize } from 'path';
import { tmpdir } from 'os';
import { existsSync } from 'fs';

const cli_dll = process.env.DAFNY_SKETCHER_CLI_DLL_PATH || "../cli//bin/Release/net8.0/DafnySketcherCli.dll ";
const workingDir = process.env.DAFNY_SKETCHER_WORKING_DIR || null;

// Create an MCP server
const server = new McpServer({
  name: "Dafny Sketcher",
  version: "1.0.0"
});

async function writeContentToTempFile(content: string): Promise<string | null> {
  try {
    const tempDir = tmpdir();
    const filePath = join(tempDir, `tmp.dfy`);
    await writeFile(filePath, content, 'utf8');
    return filePath;
  } catch (err) {
    return null;
  }
}

// Function to resolve a path against the working directory
function resolveFilePath(relativePath: string): string | null {
  if (!workingDir) {
    // If working directory isn't set, don't try to resolve files
    return null;
  }
  
  // Prevent path traversal attacks by normalizing and ensuring the path remains within workingDir
  const normalized = normalize(relativePath);
  
  // Reject absolute paths or paths with ../ that might escape the working dir
  if (isAbsolute(normalized) || normalized.startsWith('..')) {
    return null;
  }
  
  const absolutePath = resolve(workingDir, normalized);
  
  // Ensure the resolved path is still within the working directory
  if (!absolutePath.startsWith(workingDir)) {
    return null;
  }
  
  return absolutePath;
}

async function dafnySketcher(fileInput: string, args: any[]): Promise<string> {
    let filePath: string | null = null;
    let isTemp = false;
    
    // If working directory is set, try to resolve the file path
    if (workingDir) {
        const resolvedPath = resolveFilePath(fileInput);
        if (resolvedPath && existsSync(resolvedPath)) {
          filePath = resolvedPath;
        } else {
          return "Error resolving file path";
        }
    }
    
    // If not a valid file path or file doesn't exist, treat as content
    if (!filePath) {
        filePath = await writeContentToTempFile(fileInput);
        isTemp = true;
        if (!filePath) {
            return "Error writing temporary file";
        }
    }
    
    return new Promise<string>((resolve, reject) => {
        execFile('dotnet', [cli_dll, "--file", filePath].concat(args), (error, stdout, stderr) => {
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
      const result = await dafnySketcher(fileInput, ["--sketch", "errors"]);
      return {
        content: [{ type: "text", text: result || "OK" }]
      };
    }
  );

server.tool("sketch-induction",
  // TODO: we only make methodName optional because OpenAI makes calls missing this parameter.
  { fileInput: z.string(), methodName: z.string().optional() },
  async ({ fileInput, methodName }) => {
    let result = !methodName ? "Error: missing parameter methodName" : await dafnySketcher(fileInput, ["--sketch", "induction_search", "--method", methodName]);
    if (result.includes("// Error: No method resolved.")) {
      result = "Error: No method resolved. Either the method name could not be found or there is a parse error early on. Use show-errors tool for details on errors.";
    }
    return {
      content: [{ type: "text", text: result }]
    };
  }
);

server.tool("sketch-counterexamples",
  // TODO: we only make methodName optional because OpenAI makes calls missing this parameter.
  { fileInput: z.string(), methodName: z.string().optional() },
  async ({ fileInput, methodName }) => {
    let result = !methodName ? "Error: missing parameter methodName" : await dafnySketcher(fileInput, ["--sketch", "counterexamples", "--method", methodName]);
    return {
      content: [{ type: "text", text: result }]
    };
  }
);

server.tool("sketch-assertions",
  { fileInput: z.string(), line: z.number().optional() },
  async ({ fileInput, line }) => {
    let result = line === undefined || line < 0 ? "Error: missing parameter line number" : await dafnySketcher(fileInput, ["--sketch", "assertions", "--line", line]);
    return {
      content: [{ type: "text", text: result }]
    };
  }
);

// Start receiving messages on stdin and sending messages on stdout
const transport = new StdioServerTransport();
await server.connect(transport);