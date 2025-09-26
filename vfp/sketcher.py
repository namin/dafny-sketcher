import os
import json
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional
from joblib import Memory

# Environment variables
CLI_DLL = os.environ.get('DAFNY_SKETCHER_CLI_DLL_PATH', '../cli/bin/Release/net8.0/DafnySketcherCli.dll')
CACHE_DAFNY = os.environ.get('CACHE_DAFNY', '').lower() in ('true', '1', 'yes', 'on')
CACHE_DIR = Path('cache/dafny_sketcher')

# Initialize joblib memory cache
memory = Memory(location=str(CACHE_DIR), verbose=0) if CACHE_DAFNY else None


def write_content_to_temp_file(content: str) -> Optional[str]:
    """Write content to a temporary .dfy file and return the file path."""
    try:
        # Create a temporary file with .dfy extension
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dfy', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(content)
            return temp_file.name
    except Exception:
        return None

def show_errors_for_method(file_input: str, method_name: str) -> Optional[str]:
    file_path = write_content_to_temp_file(file_input)
    if not file_path:
        return "Error writing temporary file"
    
    try:
        # Run dafny verify with filter-symbol
        cmd = ['dafny', 'verify', file_path]
        if method_name:
            cmd = cmd + ['--filter-symbol', method_name]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout
        )
        
        # Combine stdout and stderr for complete output
        output = ""
        if result.stdout:
            output += result.stdout
        if result.stderr:
            if output:
                output += "\n"
            output += result.stderr
        
        return output if output else None

    except subprocess.TimeoutExpired:
        return "Error: Dafny verify timed out"
    except Exception as e:
        return f"Error running Dafny verify: {str(e)}"
    finally:
        # Clean up temp file
        try:
            if file_path:
                Path(file_path).unlink()
        except Exception:
            pass  # Ignore cleanup errors


def list_errors_for_method(file_input: str, method_name: Optional[str]) -> List[tuple[int, int, str, str]]:
    errors = show_errors_for_method(file_input, method_name)
    if errors is None:
        return []
    
    result = []
    lines = errors.splitlines()
    
    for i, line in enumerate(lines):
        # Parse lines like: /path/to/file.dfy(493,46): Error: message
        if '.dfy(' in line and '): Error:' in line:
            try:
                # Extract the part between .dfy( and ):
                pos_start = line.find('.dfy(') + 5
                pos_end = line.find('):', pos_start)
                if pos_start > 4 and pos_end > pos_start:
                    coords = line[pos_start:pos_end]
                    if ',' in coords:
                        parts = coords.split(',')
                        line_num = int(parts[0])
                        col_num = int(parts[1])
                        # Extract error message after ): Error:
                        error_start = line.find('): Error:') + 9
                        error_msg = line[error_start:].strip()
                        
                        # Look for the code snippet in the following lines
                        code_snippet = ""
                        # The pattern is usually: error line, then "|", then line number, then "|", then code
                        for j in range(i + 1, min(i + 5, len(lines))):
                            next_line = lines[j]
                            # Look for lines that contain the line number followed by |
                            if f"{line_num} |" in next_line:
                                # Extract everything after "line_num |"
                                snippet_start = next_line.find(f"{line_num} |") + len(f"{line_num} |")
                                code_snippet = next_line[snippet_start:].strip()
                                break
                        err = (line_num, col_num, error_msg, code_snippet)
                        if err not in result:
                            result.append(err)
            except (ValueError, IndexError):
                # Skip lines that don't parse correctly
                continue
    
    return result

def _run_dafny_sketcher_core(file_input: str, args: tuple) -> str:
    """
    Core function that runs Dafny Sketcher CLI tool. 
    This is the function that gets cached by joblib.
    
    Args:
        file_input: String content of the Dafny file
        args: Tuple of arguments to pass to the CLI tool (tuple for hashability)
    
    Returns:
        Output from the CLI tool or error message
    """
    # Always treat input as content and write to temp file
    file_path = write_content_to_temp_file(file_input)
    if not file_path:
        return "Error writing temporary file"
    
    try:
        # Prepare the command
        cmd = ['dotnet', CLI_DLL, '--file', file_path] + list(args)
        
        # Run the command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout
        )
        
        # Combine stdout and stderr for complete output
        output = ""
        if result.stdout:
            output += result.stdout
        if result.stderr:
            if output:
                output += "\n"
            output += result.stderr
        
        if result.returncode != 0:
            if output:
                return f"Error from Dafny Sketcher: {output}"
            else:
                return f"Error running Dafny Sketcher: Process exited with code {result.returncode}"
        
        return output
        
    except subprocess.TimeoutExpired:
        return "Error: Dafny Sketcher timed out"
    except Exception as e:
        return f"Error running Dafny Sketcher: {str(e)}"
    finally:
        # Clean up temp file
        try:
            if file_path:
                Path(file_path).unlink()
        except Exception:
            pass  # Ignore cleanup errors


# Create cached version if caching is enabled
_cached_run_dafny_sketcher_core = memory.cache(_run_dafny_sketcher_core) if memory else None


def dafny_sketcher(file_input: str, args: List[str]) -> str:
    """
    Run Dafny Sketcher CLI tool on the given content.
    
    Args:
        file_input: String content of the Dafny file
        args: Additional arguments to pass to the CLI tool
    
    Returns:
        Output from the CLI tool or error message
    """
    # Convert args to tuple for hashability (required by joblib)
    args_tuple = tuple(args)
    
    # Use cached version if caching is enabled, otherwise use direct version
    if _cached_run_dafny_sketcher_core:
        return _cached_run_dafny_sketcher_core(file_input, args_tuple)
    else:
        return _run_dafny_sketcher_core(file_input, args_tuple)


def show_errors(file_input: str) -> Optional[str]:
    """
    Show errors in the Dafny file.
    
    Args:
        file_input: String content of the Dafny file
    
    Returns:
        Error information or None if no errors
    """
    result = dafny_sketcher(file_input, ['--sketch', 'errors_warnings'])
    return result or None


def sketch_induction(file_input: str, method_name: Optional[str] = None) -> str:
    """
    Sketch induction for a specific method.
    
    Args:
        file_input: String content of the Dafny file
        method_name: Name of the method to sketch induction for
    
    Returns:
        Induction sketch or error message
    """
    if not method_name:
        return "Error: missing parameter for method name"
    
    result = dafny_sketcher(file_input, ['--sketch', 'induction_search', '--method', method_name])
    
    if result and "// Error: No method resolved." in result:
        return "Error: No method resolved. Either the method name could not be found or there is a parse error early on. Use show_errors for details on errors."
    
    return result

def sketch_todo_lemmas(file_input: str) -> list[object]:
    """
    List lemma todos for a specific file.
    
    Args:
        file_input: String content of the Dafny file
    
    Returns:
        TODOs as JSON
    """
    result = dafny_sketcher(file_input, ['--sketch', 'todo_lemmas'])
    print(result)
    return json.loads(result) if result else []

def sketch_todo(file_input: str) -> list[object]:
    """
    List todos for a specific file.
    
    Args:
        file_input: String content of the Dafny file
    
    Returns:
        TODOs as JSON
    """
    result = dafny_sketcher(file_input, ['--sketch', 'todo'])
    return json.loads(result) if result else []

def sketch_next_todo(file_input: str) -> Optional[str]:
    """
    List next todo for a specific file.

    Args:
        file_input: String content of the Dafny file
    
    Returns:
        Next TODO as JSON or None
    """
    todos = sketch_todo(file_input)
    if not todos:
        return None
    return todos[0]

def sketch_done(file_input: str) -> list[object]:
    """
    List implemented units for a specific file.
    
    Args:
        file_input: String content of the Dafny file
    
    Returns:
        Units as JSON
    """
    result = dafny_sketcher(file_input, ['--sketch', 'done'])
    return json.loads(result) if result else None

def sketch_counterexamples(file_input: str, method_name: Optional[str] = None) -> List[str]:
    """
    Find some counterexamples for a specific method.

    Args:
        file_input: String content of the Dafny file
        method_name: Name of the method to sketch induction for
    
    Returns:
        A list of counterexamples, each a boolean condition on the parameters.
    """
    if not method_name:
        return "Error: missing parameter for method name"

    result = dafny_sketcher(file_input, ['--sketch', 'counterexamples', '--method', method_name])

    return [x for x in result.split('\n') if x]


if __name__ == "__main__":
    import tests
    if True:
        p = tests.read_file('bench/stlc_fine.dfy')
        print("SHOW ERRORS FOR METHOD")
        print(show_errors_for_method(p, "preservation"))
        print("LIST ERRORS FOR METHOD")
        print(list_errors_for_method(p, "preservation"))
        print("SHOW ERRORS")
        print(show_errors(p))
        print("SHOW ERRORS FOR SOLUTION")
        print(show_errors(tests.read_file('bench/bst_solution.dfy')))
        print("LIST ERRORS FOR TEST FILE")
        print(list_errors_for_method(tests.read_file('test.dfy'), "reverse_involutes"))

    if False:
        print('StlcDemo')
        print(sketch_todo_lemmas(tests.read_file('examples/StlcDemo.dfy')))
        print('OptBuggy')
        print(sketch_todo_lemmas(tests.read_file('examples/OptBuggy.dfy')))

    if False:
        print(sketch_todo(tests.nat_module))
        print(sketch_todo_lemmas(tests.nat_module_empty_lemma_body))
        print(sketch_done(tests.nat_module))
        print(show_errors(tests.nat_module_empty_lemma_body))
        print(sketch_induction(tests.nat_module_empty_lemma_body, "add_comm"))

    if False:
        print(sketch_todo("""
        function foo()
        lemma {:axiom} bar()
        lemma {:axiom} baz()
        """))
        print(sketch_next_todo("""
        function foo()
        lemma {:axiom} bar()
        lemma {:axiom} baz()
        """))
        print(sketch_next_todo("""
    datatype Expr =
    | Const(value: int)
    | Var(name: string)
    | Add(left: Expr, right: Expr)

    type Environment = string -> int

    function eval(e: Expr, env: Environment): int

    function optimize(e: Expr): Expr

    lemma {:axiom} optimizePreservesSemantics(e: Expr, env: Environment)
    ensures eval(optimize(e), env) == eval(e, env)
    """))

        print(sketch_next_todo("""
    datatype Expr =
    | Const(value: int)
    | Var(name: string)
    | Add(left: Expr, right: Expr)

    type Environment = string -> int

    function eval(e: Expr, env: Environment): int { 0 }

    function optimize(e: Expr): Expr { e }

    lemma {:axiom} optimizePreservesSemantics(e: Expr, env: Environment)
    ensures eval(optimize(e), env) == eval(e, env)
    """))

    if False:
        program_with_bugs = """datatype Expr =
    | Const(value: int)
    | Var(name: string)
    | Add(left: Expr, right: Expr)

    predicate {:spec} optimal(e: Expr)
    {
    match e
    case Add(Const(0), _) => false
    case Add(_, Const(0)) => false
    case Add(e1, e2) => optimal(e1) && optimal(e2)
    case _ => true
    }

    function optimize(e: Expr): Expr
    {
    match e
    case Add(Const(0), e2) => optimize(e2)
    case Add(e1, Const(0)) => optimize(e1)
    case Add(e1, e2) => Add(optimize(e1), optimize(e2))
    case _ => e
    }

    lemma optimizeOptimal(e: Expr)
    ensures optimal(optimize(e))
    {
    }
    """
        print(sketch_counterexamples(program_with_bugs, "optimizeOptimal"))
