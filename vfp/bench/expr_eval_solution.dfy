datatype Expr =
  | Const(value: int)
  | Var(name: string)
  | Add(left: Expr, right: Expr)

type Environment = string -> int

function Eval(e: Expr, env: Environment): int
{
  match e
  case Const(v) => v
  case Var(x) => env(x)
  case Add(e1, e2) => Eval(e1, env) + Eval(e2, env)
}

function Optimize(e: Expr): Expr
{
  match e
  case Const(v) => Const(v)
  case Var(x) => Var(x)
  case Add(e1, e2) =>
    var o1 := Optimize(e1);
    var o2 := Optimize(e2);
    match (o1, o2)
    case (Const(0), _) => o2
    case (_, Const(0)) => o1
    case _ => Add(o1, o2)
}

lemma OptimizePreservesSemantics(e: Expr, env: Environment)
  ensures Eval(Optimize(e), env) == Eval(e, env)
{
  match e
  case Const(_) =>
  case Var(_) =>
  case Add(e1, e2) =>
    OptimizePreservesSemantics(e1, env);
    OptimizePreservesSemantics(e2, env);
    var o1 := Optimize(e1);
    var o2 := Optimize(e2);
    assert Eval(o1, env) == Eval(e1, env);
    assert Eval(o2, env) == Eval(e2, env);
    
    match (o1, o2)
    case (Const(0), _) =>
      calc {
        Eval(Optimize(e), env);
        == Eval(o2, env);
        == Eval(e2, env);
        == 0 + Eval(e2, env);
        == Eval(e1, env) + Eval(e2, env);
        == Eval(e, env);
      }
    case (_, Const(0)) =>
      calc {
        Eval(Optimize(e), env);
        == Eval(o1, env);
        == Eval(e1, env);
        == Eval(e1, env) + 0;
        == Eval(e1, env) + Eval(e2, env);
        == Eval(e, env);
      }
    case _ =>
      calc {
        Eval(Optimize(e), env);
        == Eval(Add(o1, o2), env);
        == Eval(o1, env) + Eval(o2, env);
        == Eval(e1, env) + Eval(e2, env);
        == Eval(e, env);
      }
}