datatype Expr =
  | Const(value: int)
  | Var(name: string)
  | Add(left: Expr, right: Expr)

type Environment = string -> int

function Eval(e: Expr, env: Environment): int

function Optimize(e: Expr): Expr

lemma {:axiom} OptimizePreservesSemantics(e: Expr, env: Environment)
  ensures Eval(Optimize(e), env) == Eval(e, env)