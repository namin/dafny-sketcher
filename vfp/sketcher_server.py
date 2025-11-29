from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Optional
import json

from sketcher import dafny_sketcher, show_errors_for_method, list_errors_for_method

app = FastAPI(
    title="Dafny Sketcher API",
    description="FastAPI server wrapping the Dafny Sketcher CLI",
    version="1.0.0"
)


class SketchRequest(BaseModel):
    content: str                          # Dafny file content (required)
    sketch: str                           # Sketch type (required)
    method: Optional[str] = None          # Method name to target
    line: Optional[int] = None            # Single line number
    line_range: Optional[str] = None      # Line range "start-end"
    replace: bool = False                 # Apply sketch back into file
    prompt: Optional[str] = None          # Optional prompt for AI sketches


class SketchResponse(BaseModel):
    success: bool
    result: Any                           # String or JSON depending on sketch type
    error: Optional[str] = None


class ErrorItem(BaseModel):
    line: int
    column: int
    message: str
    snippet: str


class ErrorListResponse(BaseModel):
    success: bool
    errors: list[ErrorItem]
    error: Optional[str] = None


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/sketch", response_model=SketchResponse)
async def sketch(request: SketchRequest):
    """
    Run a Dafny Sketcher operation.

    Sketch types include:
    - errors, errors_warnings: Show errors/warnings
    - todo: List TODOs
    - done: List implemented units
    - todo_lemmas: List lemma TODOs
    - proof_lines: List proof lines
    - induction, induction_search: Sketch induction
    - shallow_induction, shallow_induction_search: Shallow induction
    - counterexamples: Find counterexamples
    - ai_whole: AI whole-program generation (requires prompt)
    """
    try:
        # Build CLI args
        args = []

        if request.method:
            args.extend(['--method', request.method])

        if request.line is not None:
            args.extend(['--line', str(request.line)])

        if request.line_range:
            args.extend(['--line-range', request.line_range])

        if request.replace:
            args.append('--replace')

        if request.prompt:
            args.extend(['--prompt', request.prompt])

        # Call the sketcher
        result = dafny_sketcher(request.content, ['--sketch', request.sketch] + args)

        # Check for errors in result
        if result.startswith("Error"):
            return SketchResponse(success=False, result=None, error=result)

        # Try to parse as JSON for structured sketch types
        if request.sketch in ('todo', 'done', 'todo_lemmas', 'proof_lines'):
            try:
                parsed = json.loads(result)
                return SketchResponse(success=True, result=parsed, error=None)
            except json.JSONDecodeError:
                pass

        return SketchResponse(success=True, result=result, error=None)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sketch/errors/method", response_model=SketchResponse)
async def sketch_errors_for_method(content: str, method_name: str):
    """Show raw error output for a specific method."""
    try:
        result = show_errors_for_method(content, method_name)
        return SketchResponse(success=True, result=result, error=None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sketch/errors/list", response_model=ErrorListResponse)
async def sketch_list_errors(content: str, method_name: Optional[str] = None):
    """List parsed errors for a method (or all methods if not specified)."""
    try:
        errors = list_errors_for_method(content, method_name)
        error_items = [
            ErrorItem(line=e[0], column=e[1], message=e[2], snippet=e[3])
            for e in errors
        ]
        return ErrorListResponse(success=True, errors=error_items, error=None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
