# Dafny Sketcher CLI

This CLI is to serve as a building block in more automated workflow.

## Building

- `dotnet build DafnySketcherCli.csproj -c Release`

## Configuration

Like for Dafny Sketcher, the API keys can be set as environment variables and decide which LLM to use.

## Running

### Whole-program generation

```
dotnet bin/Release/net8.0/DafnySketcherCli.dll --sketch ai_whole --prompt "In Dafny, generate an ADT for arithmetic expressions with integers, variables and binary additions. Generate an evaluator which takes an expression and an environment mapping variable names to integers, and return an integer. Write an optimizer that removes additions by 0. Write a lemma to show that the optimizer preserves the semantics." >out.dfy
```

### List errors by methods

```
dotnet bin/Release/net8.0/DafnySketcherCli.dll --file out.dfy --sketch errors
```

### Use any Dafny Sketcher routine

```
dotnet bin/Release/net8.0/DafnySketcherCli.dll --file examples/opt0opt_todo.dfy --sketch induction --method OptimizerOptimal
```

Or to build and test at the same time:
```
dotnet run --project DafnySketcherCli.csproj -- --file examples/opt0opt_todo.dfy --sketch induction --method OptimizerOptimal
```

Return whole-file replacement instead of just sketch:
```
dotnet bin/Release/net8.0/DafnySketcherCli.dll --file examples/opt0opt_todo.dfy --sketch induction --method OptimizerOptimal --replace
```

### See usage options

```
dotnet bin/Release/net8.0/DafnySketcherCli.dll
```