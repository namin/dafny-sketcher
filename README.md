# Dafny Sketcher
piggybacking on the Dafny language implementation to explore interactive semi-automated verified program synthesis, combining LLMs and symbolic reasoning

Besides the dev setup to use Dafny Sketcher in a VSCode extension, Dafny Sketcher is available through a [CLI](cli), an [MCP](mcp), and [VFP](vfp) (a testbed for verified functional programming).

## Dev Setup

- Clone this repo, making sure to recursively clone all submodules:
- `git clone --recursive https://github.com/namin/dafny-sketcher.git`

### Submodules

The submodules are forked (namin) branches (sketcher) of the Dafny repositories: [dafny-lang/dafny](https://github.com/dafny-lang/dafny) and [dafny-lang/ide-vscode](https://github.com/dafny-lang/ide-vscode).
- [diff for dafny-lang/dafny](https://github.com/namin/dafny/compare/master...namin:dafny:sketcher)
- [diff for dafny-lang/ide-vscode](https://github.com/namin/ide-vscode/compare/master...namin:ide-vscode:sketcher)
- [proof sketchers](https://github.com/namin/dafny/tree/sketcher/Source/DafnyCore/Sketchers)

### Quick compilation script
- `./compile.sh`

### Core unit tests
- From subdirectory `dafny/Source`,
- `dotnet build DafnyCore.Test/DafnyCore.Test.csproj; dotnet test DafnyCore.Test/DafnyCore.Test.csproj`

### LLM models

#### Configuration
You can specify by environment export `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, or else Ollama is assumed available by default.

Note: for VSCode, that environment variable has to be specified in the environment where VSCode is started. So for example, from a terminal in the ide-vscode directory:
```
export GEMINI_API_KEY=your_key
code .
```

#### Running the `LLMProgram`
(just a thin wrapper over the bare `LLMClient`)
- From subdirectory `dafny`, e.g.,
- `dotnet run --project Source/DafnyCore/DafnyCore.csproj -- What is 2 and 2`

### Dafny's Language Server Protocol (LSP)

- From subdirectory `dafny`,
- try the command **`make exe`**.
- Then, from subdirectory `dafny/Source/DafnyLanguageServer`,
- try the command **`dotnet build`**,
- which should create the file `dafny/Binaries/DafnyLanguageServer.dll`.
- If this command doesn't work, see Dafny wiki [INSTALL](https://github.com/dafny-lang/dafny/wiki/INSTALL).
- Verify that this created a file called "Binaries/Dafny.dll". Sometimes, that file apparently ends up in the "net8.0" folder. If that happens, creating a symlink helps: ln -s net8.0/Dafny.dll Binaries/Dafny.dll


### VSCode Extension

- From subdirectory `ide-vscode`,
- try the command **`npm install`**.
- Open the `ide-vscode` project in VSCode, either in VSCode or perhaps
- try the command **`code .`**.
- In VSCode, change the user settings (`Cmd-Shift-P` then type `User Settings`) to use a custom Dafny Core LSP and VSCode Extension, typically adding the following configuration options (replace `YOUR_REPO_PATH` with the absolute path to this repo):
```
    "dafny.version": "custom",
    "dafny.cliPath": "YOUR_REPO_PATH/dafny/Binaries/Dafny.dll",
    "dafny.languageServerLaunchArgs": [
        "--server", "YOUR_REPO_PATH/dafny/Binaries/DafnyLanguageServer.dll"
    ]
```
- Install and run the extension in VSCode or Cursor:
  - From the `ide-vscode` project in VSCode, `Run Debug` the configuration `Run with default server`. This will pop-up a new VSCode window, where the extension is enabled. 
  - Alternatively, package the extension with `npx vsce package` in the command line, and then in VSCode or Cursor, pick `Extensions: Install from VSIX`.
- Try `Cmd-Shift-P` then `Dafny: Generate Sketch` then `induction` from within a `.dfy` file.

#### Example (originally from [VerMCTS](https://github.com/namin/llm-verified-with-monte-carlo-tree-search))

```
datatype Expr = Const(n: int) | Var(name: string) | Add(e1: Expr, e2: Expr)

function optimize(e: Expr): Expr
{
  match e
  case Add(e1, e2) =>
    var oe1 := optimize(e1);
    var oe2 := optimize(e2);
    if oe1 == Const(0) then oe2
    else if oe2 == Const(0) then oe1
    else Add(oe1, oe2)
  case _ => e
}

function eval(e: Expr, env: string -> int): int
{
  match e
  case Const(n) => n
  case Var(name) => env(name)
  case Add(e1, e2) => eval(e1, env) + eval(e2, env)
}

lemma OptimizerPreservesSemantics(e: Expr, env: string -> int)
ensures eval(optimize(e), env) == eval(e, env)
{
// Run sketcher with cursor on line below

}
```

The lemma doesn't verify automatically, but the sketcher adds the following inductive case analysis,
which is sufficient to prove the lemma.

```
    match e {
        case Const(n) => {
        }
        case Var(name) => {
        }
        case Add(e1, e2) => {
            OptimizerPreservesSemantics(e1, env);
            OptimizerPreservesSemantics(e2, env);
        }
    }
```

### Hint: Interactively debugging the Dafny core implementation and LSP server

If it doesn't exist, created the file `dafny/.vscode/launch.json`:
```
{
    "version": "0.2.0",
    "configurations": [

    ]
}
```

Now, add a generic configuration to attach any manually picked process to the `configurations` list within the file `dafny/.vscode/launch.json`:
```
      {
        "name": "Attach",
        "type": "coreclr",
        "request": "attach",
        "processId": "${command:pickProcess}",
        "justMyCode": false,
      }
```

Now, the workflow is to first start debugging in the `ide-vscode` project,
and then to start debugging by running the `Attach` configuration in the `dafny` project,
and then to select the `DafnyLanguageServer.dll` `dotnet` process.

You can put a breakpoint in the `dafny` project,
and it will get triggered when hit by the VSCode extension run.
