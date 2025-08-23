datatype Expr =
  | Const(value: int)
  | Var(name: string)
  | Add(left: Expr, right: Expr)

predicate optimal(e: Expr)
{
  match e
  case Const(_) => true
  case Var(_) => true
  case Add(Const(0), _) => false
  case Add(_, Const(0)) => false
  case Add(e1, e2) => optimal(e1) && optimal(e2)
}

function optimize(e: Expr): Expr
{
  match e
  case Const(v) => Const(v)
  case Var(x) => Var(x)
  case Add(Const(0), e2) => optimize(e2)
  case Add(e1, Const(0)) => optimize(e1)
  case Add(e1, e2) => 
    var o1 := optimize(e1);
    var o2 := optimize(e2);
    match o1
    case Const(0) => o2
    case _ => match o2
      case Const(0) => o1
      case _ => Add(o1, o2)
}

lemma OptimizerOptimal(e: Expr)
  ensures optimal(optimize(e))
{
  match e
  case Const(_) =>
  case Var(_) =>
  case Add(e1, e2) =>
    OptimizerOptimal(e1);
    OptimizerOptimal(e2);
    var o1 := optimize(e1);
    var o2 := optimize(e2);
    assert optimal(o1) && optimal(o2);
}