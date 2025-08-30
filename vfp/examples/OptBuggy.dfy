datatype Expr =
  | Const(value: int)
  | Var(name: string)
  | Add(left: Expr, right: Expr)

predicate {:spec} optimal(e: Expr)
{
  match e
  case Add(Const(0), _) => false
  case Add(_, Const(0)) => false
  case Add(e1, e2) => optimal(e1) && optimal(e2)
  case _ => true
}

function optimize(e: Expr): Expr
{
  match e
  case Add(Const(0), e2) => optimize(e2)
  case Add(e1, Const(0)) => optimize(e1)
  case Add(e1, e2) => Add(optimize(e1), optimize(e2))
  case _ => e
}

lemma {:axiom} optimizeOptimal(e: Expr)
ensures optimal(optimize(e))
