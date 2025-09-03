import os
import json
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional

# Environment variables
CLI_DLL = os.environ.get('DAFNY_SKETCHER_CLI_DLL_PATH', '../cli/bin/Release/net8.0/DafnySketcherCli.dll')


def write_content_to_temp_file(content: str) -> Optional[str]:
    """Write content to a temporary .dfy file and return the file path."""
    try:
        # Create a temporary file with .dfy extension
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dfy', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(content)
            return temp_file.name
    except Exception:
        return None


def dafny_sketcher(file_input: str, args: List[str]) -> str:
    """
    Run Dafny Sketcher CLI tool on the given content.
    
    Args:
        file_input: String content of the Dafny file
        args: Additional arguments to pass to the CLI tool
    
    Returns:
        Output from the CLI tool or error message
    """
    # Always treat input as content and write to temp file
    file_path = write_content_to_temp_file(file_input)
    if not file_path:
        return "Error writing temporary file"
    
    try:
        # Prepare the command
        cmd = ['dotnet', CLI_DLL, '--file', file_path] + args
        
        # Run the command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout
        )
        
        if result.returncode != 0:
            if result.stderr:
                return f"Error from Dafny Sketcher: {result.stderr}"
            else:
                return f"Error running Dafny Sketcher: Process exited with code {result.returncode}"
        
        return result.stdout
        
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


def show_errors(file_input: str) -> Optional[str]:
    """
    Show errors in the Dafny file.
    
    Args:
        file_input: String content of the Dafny file
    
    Returns:
        Error information or "OK" if no errors
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
