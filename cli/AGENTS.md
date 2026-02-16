# Dafny Sketcher CLI

Dafny Sketcher CLI is a collection of routines that can help develop verified programs in Dafny.

## Commands

- Print errors or OK if no errors:
  `dafny-sketcher-cli --file FILE.dfy --sketch errors_warnings`
- Produce an inductive sketch for the given method lemma:
  `dafny-sketcher-cli --file FILE.dfy --sketch induction_search --method METHOD_NAME`
- Find some counterexamples for the given method lemma, returning a (possibly empty) list of counterexamples, each a boolean condition on the parameters:
  `dafny-sketcher-cli --file FILE.dfy --sketch counterexamples --method METHOD_NAME`
- List unit-level TODOs as JSON:
  `dafny-sketcher-cli --file FILE.dfy --sketch todo`
- List implemented units as JSON:
  `dafny-sketcher-cli --file FILE.dfy --sketch done`
- List lemmas with remaining TODOs (for fine-grained edits) as JSON:
  `dafny-sketcher-cli --file FILE.dfy --sketch todo_lemmas`

## Hints

For the any sketcher that takes a `--method`, you need to make sure the method has a body and is not marked `:axiom`.

### Controlling induction with `{:induction_on}`

By default, the induction sketcher auto-detects the induction variable (first `decreases` expression, or first `nat`/datatype parameter). To override this, add a `{:induction_on x}` attribute to your method/lemma, where `x` is:

- **A parameter name** — performs structural induction on that parameter:
  ```dafny
  lemma {:induction_on xs} AppendAssoc(xs: List, ys: List, zs: List)
    ensures Append(Append(xs, ys), zs) == Append(xs, Append(ys, zs))
  { }
  ```

- **A function name** — performs rule induction following that function (looked up from calls in requires/ensures):
  ```dafny
  lemma {:induction_on optimize} OptimizerPreservesSemantics(e: Expr, env: string -> int)
    ensures eval(optimize(e), env) == eval(e, env)
  { }
  ```

- **A function application** — performs rule induction using that specific call expression:
  ```dafny
  lemma {:induction_on optimize(e)} OptimizerPreservesSemantics(e: Expr, env: string -> int)
    ensures eval(optimize(e), env) == eval(e, env)
  { }
  ```