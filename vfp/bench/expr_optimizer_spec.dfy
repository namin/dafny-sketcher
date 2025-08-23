datatype Expr =
  | Const(value: int)
  | Var(name: string)
  | Add(left: Expr, right: Expr)

predicate {:spec} optimal(e: Expr)
{
  match e
  case Const(_) => true
  case Var(_) => true
  case Add(Const(0), _) => false
  case Add(_, Const(0)) => false
  case Add(e1, e2) => optimal(e1) && optimal(e2)
}

function optimize(e: Expr): Expr

lemma {:axiom} OptimizerOptimal(e: Expr)
  ensures optimal(optimize(e))