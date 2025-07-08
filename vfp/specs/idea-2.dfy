datatype Expr =
  | Const(val: int)
  | Var(name: string)
  | Add(left: Expr, right: Expr)

// Predicate to check if an expression is optimal (no additions by 0).
function optimal(e: Expr): bool

// Function to optimize an expression by removing additions by 0.
function optimize(e: Expr): Expr

// Lemma to ensure that the optimizer produces an optimal expression.
lemma {:axiom} OptimizerOptimal(e: Expr)
ensures optimal(optimize(e))
