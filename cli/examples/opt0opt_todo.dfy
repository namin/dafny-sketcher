// ADT for arithmetic expressions
datatype Expr = Const(val: int)
              | Var(name: string)
              | Add(e1: Expr, e2: Expr)

// Evaluator
function Eval(e: Expr, env: string -> int): int
{
  match e
  case Const(val) => val
  case Var(name) => env(name)
  case Add(e1, e2) => Eval(e1, env) + Eval(e2, env)
}

// Optimizer
function Optimize(e: Expr): Expr
{
  match e
  case Add(e1, e2) => 
    var o1 := Optimize(e1);
    var o2 := Optimize(e2);
    if o2 == Const(0) then o1 else
    if o1 == Const(0) then o2 else Add(o1, o2)
  case _ => e
}

predicate Optimal(e: Expr)
{
    match e
    case Add(e, Const(0)) => false
    case Add(Const(0), e) => false
    case Add(e1, e2) => Optimal(e1) && Optimal(e2)
    case _ => true 
}

lemma OptimizerOptimal(e: Expr)
  ensures Optimal(Optimize(e))
{
// TODO
}