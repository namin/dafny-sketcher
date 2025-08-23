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
  match e {
  case Add(e1, e2) =>
    match (optimize(e1), optimize(e2)) {
    case (Const(0), oe2) => oe2
    case (oe1, Const(0)) => oe1
    case (oe1, oe2) => Add(oe1, oe2)
    }
  case _ => e
  }
}

lemma optimizeOptimal(e: Expr)
ensures optimal(optimize(e))
{
  // Structural induction on e
  match e {
      case Const(value) => {
      }
      case Var(name) => {
      }
      case Add(left, right) => {
          optimizeOptimal(left);
          optimizeOptimal(right);
      }
  }
}