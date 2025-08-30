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
  case Add(e1, e2) =>
    var o1 := optimize(e1);
    var o2 := optimize(e2);
    if o2 == Const(0) then o1 else
    if o1 == Const(0) then o2 else Add(o1, o2)
  case _ => e
}

lemma {:axiom} optimizeOptimal(e: Expr)
ensures optimal(optimize(e))