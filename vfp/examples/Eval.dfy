datatype Expr =
  | Const(value: int)
  | Var(name: string)
  | Add(left: Expr, right: Expr)

type Environment = string -> int

function eval(e: Expr, env: Environment): int
{
  match e
  case Const(val) => val
  case Var(name) => env(name)
  case Add(e1, e2) => eval(e1, env) + eval(e2, env)
}

function optimize(e: Expr): Expr
{
  match e
  case Add(e1, e2) =>
    var o1 := optimize(e1);
    var o2 := optimize(e2);
    if o2 == Const(0) then o1 else
    if o1 == Const(0) then o2 else Add(o1, o2)
  case _ => e
}

lemma {:axiom} optimizePreservesSemantics(e: Expr, env: Environment)
ensures eval(optimize(e), env) == eval(e, env)