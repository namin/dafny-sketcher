# Dafny Sketcher Server

A FastAPI server wrapping the Dafny Sketcher CLI.

## Running the Server

```bash
# Using uvicorn directly
uvicorn sketcher_server:app --reload --port 8000

# Or run as script
python sketcher_server.py
```

The server runs on `http://localhost:8000` by default.

## API Documentation

Once running, interactive API docs are available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints

### Health Check

```
GET /health
```

Returns `{"status": "ok"}` if the server is running.

### Sketch

```
POST /sketch
```

Main endpoint that mirrors the CLI interface.

#### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `content` | string | Yes | Dafny file content |
| `sketch` | string | Yes | Sketch type (see below) |
| `method` | string | No | Method name to target |
| `line` | int | No | Single line number |
| `line_range` | string | No | Line range "start-end" |
| `replace` | bool | No | Apply sketch back into file (default: false) |
| `prompt` | string | No | Prompt for AI sketch types |

#### Sketch Types

| Type | Description |
|------|-------------|
| `errors` | Show errors in file |
| `errors_warnings` | Show errors and warnings |
| `todo` | List TODOs (functions/lemmas to implement) |
| `done` | List implemented units |
| `todo_lemmas` | List lemma TODOs |
| `proof_lines` | List proof lines |
| `induction` | Sketch induction proof |
| `induction_search` | Search for induction proof |
| `shallow_induction` | Shallow induction proof |
| `shallow_induction_search` | Search for shallow induction proof |
| `counterexamples` | Find counterexamples for a method |
| `ai_whole` | AI whole-program generation (requires `prompt`) |

#### Response

```json
{
  "success": true,
  "result": "...",
  "error": null
}
```

- `success`: Whether the operation succeeded
- `result`: String or JSON depending on sketch type
- `error`: Error message if `success` is false

## Examples

### Induction Search

```bash
curl -X POST http://localhost:8000/sketch \
  -H "Content-Type: application/json" \
  -d '{
    "content": "datatype Nat = Zero | Succ(pred: Nat)\n\nfunction add(n: Nat, m: Nat): Nat {\n  match n\n  case Zero => m\n  case Succ(p) => Succ(add(p, m))\n}\n\nlemma {:axiom} add_comm(n: Nat, m: Nat)\n  ensures add(n, m) == add(m, n)\n",
    "sketch": "induction_search",
    "method": "add_comm"
  }'
```

### Shallow Induction

```bash
curl -X POST http://localhost:8000/sketch \
  -H "Content-Type: application/json" \
  -d '{
    "content": "...",
    "sketch": "shallow_induction_search",
    "method": "add_comm"
  }'
```

### List Errors

```bash
curl -X POST http://localhost:8000/sketch \
  -H "Content-Type: application/json" \
  -d '{
    "content": "lemma foo() ensures false {}",
    "sketch": "errors"
  }'
```

### List TODOs

```bash
curl -X POST http://localhost:8000/sketch \
  -H "Content-Type: application/json" \
  -d '{
    "content": "function foo(): int\nlemma {:axiom} bar()\n  ensures true",
    "sketch": "todo"
  }'
```

### Find Counterexamples

```bash
curl -X POST http://localhost:8000/sketch \
  -H "Content-Type: application/json" \
  -d '{
    "content": "...",
    "sketch": "counterexamples",
    "method": "myLemma"
  }'
```

### AI Whole-Program Generation

```bash
curl -X POST http://localhost:8000/sketch \
  -H "Content-Type: application/json" \
  -d '{
    "content": "",
    "sketch": "ai_whole",
    "prompt": "Generate an ADT for arithmetic expressions with integers, variables and binary additions."
  }'
```

## Environment Variables

The server inherits environment variables from `sketcher.py`:

| Variable | Description |
|----------|-------------|
| `DAFNY_SKETCHER_CLI_DLL_PATH` | Path to CLI DLL (default: `../cli/bin/Release/net8.0/DafnySketcherCli.dll`) |
| `CACHE_DAFNY` | Enable caching (`true`, `1`, `yes`, `on`) |
