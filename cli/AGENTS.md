# Dafny Sketcher CLI

Dafny Sketcher is a collection of routines that can help develop verified programs in Dafny.

- Print errors or OK if no errors:
  `dafny-sketcher-cli --file FILE.dfy --sketch errors_warnings`
- Produce an inductive sketch for the given method lemma:
  `dafny-sketcher-cli --file FILE.dfy --sketch induction_search --method METHOD_NAME`
- Find some counterexamples for the given method lemma, returning a (possibly empty) list of counterexamples, each a boolean condition on the paramters:
  `dafny-sketcher-cli --file FILE.dfy --sketch counterexamples --method METHOD_NAME`
- List unit-level TODOs as JSON:
  `dafny-sketcher-cli --file FILE.dfy --sketch todo`
- List implemented units as JSON:
  `dafny-sketcher-cli --file FILE.dfy --sketch done`
- List lemmas with remaining TODOs as JSON:
  `dafny-sketcher-cli --file FILE.dfy --sketch todo_lemmas`
