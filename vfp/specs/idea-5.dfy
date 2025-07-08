datatype Expr =
  | Const(value: int)
  | Var(name: string)
  | Add(left: Expr, right: Expr)

// Evaluates an expression given an environment.
function Eval(e: Expr, env: string -> int) : int

// Optimizes an expression by removing additions by 0.
function Optimize(e: Expr) : Expr

// Lemma to prove that optimization preserves semantics.
lemma {:axiom} OptimizePreservesSemantics(e: Expr, env: string -> int)
  ensures Eval(Optimize(e), env) == Eval(e, env)
