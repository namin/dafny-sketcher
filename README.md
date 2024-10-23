# dafny-sketcher
piggy-backing on the Dafny language implementation to explore interactive semi-automated verified program synthesis, combining LLMs and symbolic reasoning

## Dev Setup

- Clone this repo, making sure to recursively clone all submodules:
- `git clone --recursive https://github.com/namin/dafny-sandbox.git`

### Dafny's Language Server Protocol (LSP)

- From subdirectory `dafny`,
- try the command **`make exe`**.
- Then, from subdirectory `dafny/Source/DafnyLanguageServer`,
- try the command **`dotnet build`**,
- which should create the file `dafny/Binaries/DafnyLanguageServer.dll`.
- If this command doesn't work, see Dafny wiki INSTALL[(https://github.com/dafny-lang/dafny/wiki/INSTALL)].

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

- Now, `Run Debug` the configuration `Run with default server`.
- This will pop-up a new VSCode window, where the extension is enabled.
- Try `Cmd-Shift-P` then `Dafny: Generate Inductive Proof Sketch` from within a `.dfy` file.

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
