"""DafnySketcher tool hook for Henri.

Usage:
    henri --hook /path/to/dafny-sketcher/vfp/henri.py

Adds dafny_sketcher tool for proof sketching assistance.
"""

import os
import subprocess
import tempfile
from pathlib import Path

from henri.tools.base import Tool

# Path to the CLI DLL
CLI_DLL = os.environ.get(
    'DAFNY_SKETCHER_CLI_DLL_PATH',
    str(Path(__file__).parent.parent / 'cli' / 'bin' / 'Release' / 'net8.0' / 'DafnySketcherCli.dll')
)


class DafnySketcherTool(Tool):
    """Run dafny-sketcher CLI for proof assistance."""

    name = "dafny_sketcher"
    description = """Run dafny-sketcher to assist with Dafny proofs. Available sketch types:
  - errors: Show verification errors in the file
  - errors_warnings: Show errors and warnings
  - todo: List unimplemented functions/lemmas (JSON)
  - done: List implemented units (JSON)
  - todo_lemmas: List lemmas with errors (JSON)
  - induction_search: Generate induction proof sketch for a method (requires --method)
  - counterexamples: Find counterexamples for a method (requires --method)
  - proof_lines: List proof lines in file or method (JSON)"""

    parameters = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path to the .dfy file",
            },
            "sketch": {
                "type": "string",
                "description": "Sketch type: errors, errors_warnings, todo, done, todo_lemmas, induction_search, counterexamples, proof_lines",
            },
            "method": {
                "type": "string",
                "description": "Method name (required for induction_search, counterexamples)",
            },
        },
        "required": ["path", "sketch"],
    }
    requires_permission = True

    def execute(self, path: str, sketch: str, method: str = None) -> str:
        try:
            # Build command
            cmd = ["dotnet", CLI_DLL, "--file", path, "--sketch", sketch]
            if method:
                cmd.extend(["--method", method])

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
            )
            output = result.stdout
            if result.stderr:
                output += f"\n{result.stderr}"
            return output or "(no output)"
        except FileNotFoundError:
            return f"[error: dotnet or CLI not found. Ensure dotnet is installed and CLI is built at {CLI_DLL}]"
        except subprocess.TimeoutExpired:
            return "[error: dafny-sketcher timed out after 120 seconds]"
        except Exception as e:
            return f"[error: {e}]"


# Tools to add
TOOLS = [DafnySketcherTool()]

# Make dafny_sketcher path-based (per-path "always")
PATH_BASED = {"dafny_sketcher"}

# Auto-allow dafny_sketcher within cwd
AUTO_ALLOW_CWD = {"dafny_sketcher"}
