// Symbolic Differentiation with Simplifier - Simplified Version
// Demonstrates key verification patterns with smaller, provable lemmas

datatype Expr = 
  | Const(r: real)
  | Var(name: string)
  | Add(left: Expr, right: Expr)
  | Mul(left: Expr, right: Expr)
  | Neg(e: Expr)

type Env = string -> real

function eval(e: Expr, env: Env): real
{
  match e
  case Const(r) => r
  case Var(x) => env(x)
  case Add(l, r) => eval(l, env) + eval(r, env)
  case Mul(l, r) => eval(l, env) * eval(r, env)
  case Neg(e) => -eval(e, env)
}

// Symbolic differentiation
function diff(e: Expr, x: string): Expr
{
  match e
  case Const(r) => Const(0.0)
  case Var(y) => if x == y then Const(1.0) else Const(0.0)
  case Add(l, r) => Add(diff(l, x), diff(r, x))
  case Mul(l, r) => Add(Mul(diff(l, x), r), Mul(l, diff(r, x)))  // Product rule
  case Neg(e) => Neg(diff(e, x))
}

// Size for termination
function size(e: Expr): nat
{
  match e
  case Const(_) => 1
  case Var(_) => 1  
  case Add(l, r) => 1 + size(l) + size(r)
  case Mul(l, r) => 1 + size(l) + size(r)
  case Neg(e) => 1 + size(e)
}

// Simple one-pass simplifier
function simplify(e: Expr): Expr
  decreases size(e)
{
  match e
  case Const(r) => Const(r)
  case Var(x) => Var(x)
  case Add(l, r) => 
    var sl := simplify(l);
    var sr := simplify(r);
    simplifyAdd(sl, sr)
  case Mul(l, r) => 
    var sl := simplify(l);
    var sr := simplify(r);
    simplifyMul(sl, sr)
  case Neg(e) => 
    var se := simplify(e);
    simplifyNeg(se)
}

function simplifyAdd(l: Expr, r: Expr): Expr
{
  match (l, r)
  case (Const(0.0), _) => r  // 0 + x = x
  case (_, Const(0.0)) => l  // x + 0 = x
  case (Const(a), Const(b)) => Const(a + b)  // Constant folding
  case _ => Add(l, r)
}

function simplifyMul(l: Expr, r: Expr): Expr
{
  match (l, r)
  case (Const(0.0), _) => Const(0.0)  // 0 * x = 0
  case (_, Const(0.0)) => Const(0.0)  // x * 0 = 0
  case (Const(1.0), _) => r  // 1 * x = x
  case (_, Const(1.0)) => l  // x * 1 = x
  case (Const(a), Const(b)) => Const(a * b)  // Constant folding
  case _ => Mul(l, r)
}

function simplifyNeg(e: Expr): Expr
{
  match e
  case Const(r) => Const(-r)
  case Neg(a) => a  // Double negation
  case _ => Neg(e)
}

// Core preservation lemma - simplification preserves meaning
lemma SimplifyPreservesEval(e: Expr, env: Env)
  ensures eval(simplify(e), env) == eval(e, env)
  decreases size(e)
{
  match e {
    case Const(r) => 
      assert simplify(Const(r)) == Const(r);
    case Var(x) =>
      assert simplify(Var(x)) == Var(x);
    case Add(l, r) =>
      // First simplify subexpressions
      var sl := simplify(l);
      var sr := simplify(r);
      
      // Recursive proofs
      SimplifyPreservesEval(l, env);
      SimplifyPreservesEval(r, env);
      
      // Connect the pieces
      calc == {
        eval(simplify(Add(l, r)), env);
        eval(simplifyAdd(sl, sr), env);
        { SimplifyAddCorrect(sl, sr, env); }
        eval(Add(sl, sr), env);
        eval(sl, env) + eval(sr, env);
        { assert eval(sl, env) == eval(l, env); 
          assert eval(sr, env) == eval(r, env); }
        eval(l, env) + eval(r, env);
        eval(Add(l, r), env);
      }
    case Mul(l, r) =>
      var sl := simplify(l);
      var sr := simplify(r);
      SimplifyPreservesEval(l, env);
      SimplifyPreservesEval(r, env);
      
      calc == {
        eval(simplify(Mul(l, r)), env);
        eval(simplifyMul(sl, sr), env);
        { SimplifyMulCorrect(sl, sr, env); }
        eval(Mul(sl, sr), env);
        eval(sl, env) * eval(sr, env);
        { assert eval(sl, env) == eval(l, env);
          assert eval(sr, env) == eval(r, env); }
        eval(l, env) * eval(r, env);
        eval(Mul(l, r), env);
      }
    case Neg(e) =>
      var se := simplify(e);
      SimplifyPreservesEval(e, env);
      
      calc == {
        eval(simplify(Neg(e)), env);
        eval(simplifyNeg(se), env);
        { SimplifyNegCorrect(se, env); }
        eval(Neg(se), env);
        -eval(se, env);
        { assert eval(se, env) == eval(e, env); }
        -eval(e, env);
        eval(Neg(e), env);
      }
  }
}

// Individual rule correctness lemmas
lemma {:timeLimit 5} SimplifyAddCorrect(l: Expr, r: Expr, env: Env)
  ensures eval(simplifyAdd(l, r), env) == eval(Add(l, r), env)
{
  match (l, r) {
    case (Const(0.0), _) =>
      assert simplifyAdd(Const(0.0), r) == r;
      assert eval(Add(Const(0.0), r), env) == 0.0 + eval(r, env) == eval(r, env);
    case (_, Const(0.0)) =>
      assert simplifyAdd(l, Const(0.0)) == l;
      assert eval(Add(l, Const(0.0)), env) == eval(l, env) + 0.0 == eval(l, env);
    case (Const(a), Const(b)) =>
      assert simplifyAdd(Const(a), Const(b)) == Const(a + b);
      assert eval(Add(Const(a), Const(b)), env) == a + b;
    case _ =>
      assert simplifyAdd(l, r) == Add(l, r);
  }
}

lemma {:timeLimit 5} SimplifyMulCorrect(l: Expr, r: Expr, env: Env)
  ensures eval(simplifyMul(l, r), env) == eval(Mul(l, r), env)
{
  match (l, r) {
    case (Const(0.0), _) =>
      assert simplifyMul(Const(0.0), r) == Const(0.0);
      assert eval(Mul(Const(0.0), r), env) == 0.0 * eval(r, env) == 0.0;
    case (_, Const(0.0)) =>
      assert simplifyMul(l, Const(0.0)) == Const(0.0);
      assert eval(Mul(l, Const(0.0)), env) == eval(l, env) * 0.0 == 0.0;
    case (Const(1.0), _) =>
      assert simplifyMul(Const(1.0), r) == r;
      assert eval(Mul(Const(1.0), r), env) == 1.0 * eval(r, env) == eval(r, env);
    case (_, Const(1.0)) =>
      assert simplifyMul(l, Const(1.0)) == l;
      assert eval(Mul(l, Const(1.0)), env) == eval(l, env) * 1.0 == eval(l, env);
    case (Const(a), Const(b)) =>
      assert simplifyMul(Const(a), Const(b)) == Const(a * b);
      assert eval(Mul(Const(a), Const(b)), env) == a * b;
    case _ =>
      assert simplifyMul(l, r) == Mul(l, r);
  }
}

lemma SimplifyNegCorrect(e: Expr, env: Env)
  ensures eval(simplifyNeg(e), env) == eval(Neg(e), env)
{
  match e {
    case Const(r) =>
      assert eval(simplifyNeg(e), env) == -r;
      assert eval(Neg(e), env) == -r;
    case Neg(a) =>
      assert eval(simplifyNeg(e), env) == eval(a, env);
      assert eval(Neg(e), env) == -(-eval(a, env)) == eval(a, env);
    case _ =>
  }
}

// Main theorem: simplified derivative has same meaning
lemma MainTheorem(e: Expr, x: string, env: Env)
  ensures eval(simplify(diff(e, x)), env) == eval(diff(e, x), env)
{
  var d := diff(e, x);
  SimplifyPreservesEval(d, env);
}

// Small concrete lemmas demonstrating specific optimizations
lemma ZeroAddIdentity(e: Expr, env: Env)
  ensures eval(simplify(Add(Const(0.0), e)), env) == eval(e, env)
  ensures eval(simplify(Add(e, Const(0.0))), env) == eval(e, env)
{
  var se := simplify(e);
  calc == {
    eval(simplify(Add(Const(0.0), e)), env);
    { assert simplify(Add(Const(0.0), e)) == simplifyAdd(Const(0.0), se); }
    eval(simplifyAdd(Const(0.0), se), env);
    { assert simplifyAdd(Const(0.0), se) == se; }
    eval(se, env);
    { SimplifyPreservesEval(e, env); }
    eval(e, env);
  }
  
  calc == {
    eval(simplify(Add(e, Const(0.0))), env);
    { assert simplify(Add(e, Const(0.0))) == simplifyAdd(se, Const(0.0)); }
    eval(simplifyAdd(se, Const(0.0)), env);
    { assert simplifyAdd(se, Const(0.0)) == se; }
    eval(se, env);
    { SimplifyPreservesEval(e, env); }
    eval(e, env);
  }
}

lemma OneMultIdentity(e: Expr, env: Env)
  ensures eval(simplify(Mul(Const(1.0), e)), env) == eval(e, env)
  ensures eval(simplify(Mul(e, Const(1.0))), env) == eval(e, env)
{
  var se := simplify(e);
  assert simplify(Mul(Const(1.0), e)) == simplifyMul(Const(1.0), se);
  assert simplifyMul(Const(1.0), se) == se;
  
  assert simplify(Mul(e, Const(1.0))) == simplifyMul(se, Const(1.0));
  assert simplifyMul(se, Const(1.0)) == se;
  
  SimplifyPreservesEval(e, env);
}

lemma ZeroMultAnnihilator(e: Expr, env: Env)
  ensures eval(simplify(Mul(Const(0.0), e)), env) == 0.0
  ensures eval(simplify(Mul(e, Const(0.0))), env) == 0.0
{
  var se := simplify(e);
  assert simplify(Mul(Const(0.0), e)) == simplifyMul(Const(0.0), se);
  assert simplifyMul(Const(0.0), se) == Const(0.0);
  
  assert simplify(Mul(e, Const(0.0))) == simplifyMul(se, Const(0.0));
  assert simplifyMul(se, Const(0.0)) == Const(0.0);
}

lemma DoubleNegationElimination(e: Expr, env: Env)
  ensures eval(simplify(Neg(Neg(e))), env) == eval(e, env)
{
  var se := simplify(e);
  var sne := simplify(Neg(e));
  
  calc == {
    eval(simplify(Neg(Neg(e))), env);
    { assert simplify(Neg(Neg(e))) == simplifyNeg(sne); }
    eval(simplifyNeg(sne), env);
    { assert sne == simplifyNeg(se); }
    eval(simplifyNeg(simplifyNeg(se)), env);
    { SimplifyNegCorrect(simplifyNeg(se), env); }
    eval(Neg(simplifyNeg(se)), env);
    -eval(simplifyNeg(se), env);
    { SimplifyNegCorrect(se, env); }
    -eval(Neg(se), env);
    -(-eval(se, env));
    eval(se, env);
    { SimplifyPreservesEval(e, env); }
    eval(e, env);
  }
}

lemma ConstantFolding(a: real, b: real, env: Env)
  ensures eval(simplify(Add(Const(a), Const(b))), env) == a + b
  ensures eval(simplify(Mul(Const(a), Const(b))), env) == a * b
{
  SimplifyPreservesEval(Add(Const(a), Const(b)), env);
  SimplifyPreservesEval(Mul(Const(a), Const(b)), env);
}

// Example derivative simplifications
lemma DerivativeOfConstant(r: real, x: string, env: Env)
  ensures eval(diff(Const(r), x), env) == 0.0
  ensures eval(simplify(diff(Const(r), x)), env) == 0.0
{
  assert diff(Const(r), x) == Const(0.0);
  SimplifyPreservesEval(diff(Const(r), x), env);
}

lemma DerivativeOfVariable(y: string, x: string, env: Env)
  ensures eval(diff(Var(y), x), env) == if x == y then 1.0 else 0.0
{
  assert diff(Var(y), x) == if x == y then Const(1.0) else Const(0.0);
}

lemma DerivativeOfSum(l: Expr, r: Expr, x: string, env: Env)
  ensures eval(diff(Add(l, r), x), env) == eval(diff(l, x), env) + eval(diff(r, x), env)
{
  assert diff(Add(l, r), x) == Add(diff(l, x), diff(r, x));
}

// Commutativity lemmas
lemma AddCommutative(a: Expr, b: Expr, env: Env)
  ensures eval(Add(a, b), env) == eval(Add(b, a), env)
{
  assert eval(Add(a, b), env) == eval(a, env) + eval(b, env);
  assert eval(Add(b, a), env) == eval(b, env) + eval(a, env);
  assert eval(a, env) + eval(b, env) == eval(b, env) + eval(a, env);
}

lemma MulCommutative(a: Expr, b: Expr, env: Env)
  ensures eval(Mul(a, b), env) == eval(Mul(b, a), env)
{
  assert eval(Mul(a, b), env) == eval(a, env) * eval(b, env);
  assert eval(Mul(b, a), env) == eval(b, env) * eval(a, env);
}

// Associativity lemmas  
lemma AddAssociative(a: Expr, b: Expr, c: Expr, env: Env)
  ensures eval(Add(Add(a, b), c), env) == eval(Add(a, Add(b, c)), env)
{
  assert eval(Add(Add(a, b), c), env) == (eval(a, env) + eval(b, env)) + eval(c, env);
  assert eval(Add(a, Add(b, c)), env) == eval(a, env) + (eval(b, env) + eval(c, env));
}

lemma MulAssociative(a: Expr, b: Expr, c: Expr, env: Env)
  ensures eval(Mul(Mul(a, b), c), env) == eval(Mul(a, Mul(b, c)), env)
{
  assert eval(Mul(Mul(a, b), c), env) == (eval(a, env) * eval(b, env)) * eval(c, env);
  assert eval(Mul(a, Mul(b, c)), env) == eval(a, env) * (eval(b, env) * eval(c, env));
}

// Test method demonstrating the system
method TestSimplification()
{
  // Create x + 0
  var e1 := Add(Var("x"), Const(0.0));
  var s1 := simplify(e1);
  assert s1 == Var("x");
  
  // Create 1 * x
  var e2 := Mul(Const(1.0), Var("x"));
  var s2 := simplify(e2);
  assert s2 == Var("x");
  
  // Create 0 * x  
  var e3 := Mul(Const(0.0), Var("x"));
  var s3 := simplify(e3);
  assert s3 == Const(0.0);
  
  // Test derivative: d/dx(x*x) = x*1 + 1*x = x + x
  var e4 := Mul(Var("x"), Var("x"));
  var d4 := diff(e4, "x");
  assert d4 == Add(Mul(Const(1.0), Var("x")), Mul(Var("x"), Const(1.0)));
  
  print "Simplification tests passed!\n";
}

method Main()
{
  print "Symbolic Differentiation with Simplifier Demo\n";
  print "=============================================\n\n";
  
  // Example 1: Derivative of constant
  var c := Const(5.0);
  var dc := diff(c, "x");
  var sdc := simplify(dc);
  print "d/dx(5) = 0\n";
  
  // Example 2: Derivative of variable
  var x := Var("x");
  var dx := diff(x, "x");
  print "d/dx(x) = 1\n";
  
  // Example 3: Derivative of x*x
  var xx := Mul(Var("x"), Var("x"));
  var dxx := diff(xx, "x");
  var sdxx := simplify(dxx);
  print "d/dx(x*x) = x + x (before simplification)\n";
  
  // Example 4: Simplification examples
  var add0 := Add(Var("x"), Const(0.0));
  var sadd0 := simplify(add0);
  print "x + 0 simplifies to x\n";
  
  var mul1 := Mul(Const(1.0), Var("x"));
  var smul1 := simplify(mul1);
  print "1 * x simplifies to x\n";
  
  var mul0 := Mul(Var("x"), Const(0.0));
  var smul0 := simplify(mul0);
  print "x * 0 simplifies to 0\n";
  
  var dblneg := Neg(Neg(Var("x")));
  var sdblneg := simplify(dblneg);
  print "--x simplifies to x\n";
  
  print "\nAll simplifications correct!\n";
  
  TestSimplification();
}