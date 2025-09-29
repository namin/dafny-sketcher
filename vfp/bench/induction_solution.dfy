// Induction proofs with detailed reasoning steps

// Sum of first n natural numbers
function {:spec} sumTo(n: nat): nat
{
  if n == 0 then 0 else n + sumTo(n - 1)
}

// Sum of first n odd numbers
function {:spec} sumOdds(n: nat): nat
{
  if n == 0 then 0 else (2 * n - 1) + sumOdds(n - 1)
}

// Sum of first n squares
function {:spec} sumSquares(n: nat): nat
{
  if n == 0 then 0 else n * n + sumSquares(n - 1)
}

// Power function
function {:spec} power(base: nat, exp: nat): nat
{
  if exp == 0 then 1 else base * power(base, exp - 1)
}

// Fibonacci
function {:spec} fib(n: nat): nat
{
  if n == 0 then 0
  else if n == 1 then 1
  else fib(n - 1) + fib(n - 2)
}

// --- Detailed Inductive Proofs ---

lemma SumToFormula(n: nat)
  ensures sumTo(n) == n * (n + 1) / 2
{
  if n == 0 {
    // Base case
    assert sumTo(0) == 0;
    assert 0 * (0 + 1) / 2 == 0;
  } else {
    // Inductive step
    SumToFormula(n - 1);

    calc == {
      sumTo(n);
      n + sumTo(n - 1);
      { // Induction hypothesis
        assert sumTo(n - 1) == (n - 1) * n / 2;
      }
      n + (n - 1) * n / 2;
      { // Algebra
        assert n == 2 * n / 2;
      }
      2 * n / 2 + (n - 1) * n / 2;
      (2 * n + (n - 1) * n) / 2;
      (2 * n + n * n - n) / 2;
      (n + n * n) / 2;
      n * (1 + n) / 2;
      n * (n + 1) / 2;
    }
  }
}

lemma SumOddsIsSquare(n: nat)
  ensures sumOdds(n) == n * n
{
  if n == 0 {
    // Base case
    assert sumOdds(0) == 0;
    assert 0 * 0 == 0;
  } else {
    // Inductive step
    SumOddsIsSquare(n - 1);

    calc == {
      sumOdds(n);
      (2 * n - 1) + sumOdds(n - 1);
      { // Induction hypothesis
        assert sumOdds(n - 1) == (n - 1) * (n - 1);
      }
      (2 * n - 1) + (n - 1) * (n - 1);
      { // Expand (n-1)²
        assert (n - 1) * (n - 1) == n * n - 2 * n + 1;
      }
      (2 * n - 1) + (n * n - 2 * n + 1);
      2 * n - 1 + n * n - 2 * n + 1;
      n * n;
    }
  }
}

lemma SumSquaresFormula(n: nat)
  ensures sumSquares(n) == n * (n + 1) * (2 * n + 1) / 6
{
  if n == 0 {
    // Base case
    assert sumSquares(0) == 0;
    assert 0 * (0 + 1) * (2 * 0 + 1) / 6 == 0;
  } else {
    // Inductive step
    SumSquaresFormula(n - 1);

    calc == {
      sumSquares(n);
      n * n + sumSquares(n - 1);
      { // Induction hypothesis
        assert sumSquares(n - 1) == (n - 1) * n * (2 * n - 1) / 6;
      }
      n * n + (n - 1) * n * (2 * n - 1) / 6;
      { // Factor out common terms
        assert n * n == 6 * n * n / 6;
      }
      6 * n * n / 6 + (n - 1) * n * (2 * n - 1) / 6;
      (6 * n * n + (n - 1) * n * (2 * n - 1)) / 6;
      { // Expand
        assert (n - 1) * n * (2 * n - 1) == n * (n - 1) * (2 * n - 1);
        assert n * (n - 1) * (2 * n - 1) == n * (2 * n * n - 3 * n + 1);
        assert n * (2 * n * n - 3 * n + 1) == 2 * n * n * n - 3 * n * n + n;
      }
      (6 * n * n + 2 * n * n * n - 3 * n * n + n) / 6;
      (2 * n * n * n + 3 * n * n + n) / 6;
      n * (2 * n * n + 3 * n + 1) / 6;
      { // Factor
        assert 2 * n * n + 3 * n + 1 == (n + 1) * (2 * n + 1);
      }
      n * (n + 1) * (2 * n + 1) / 6;
    }
  }
}

lemma PowerOfTwo(n: nat)
  ensures power(2, n) >= n + 1
{
  if n == 0 {
    // Base case
    assert power(2, 0) == 1;
    assert 1 >= 0 + 1;
  } else {
    // Inductive step
    PowerOfTwo(n - 1);

    calc >= {
      power(2, n);
      2 * power(2, n - 1);
      { // Induction hypothesis
        assert power(2, n - 1) >= n;
      }
      2 * n;
      { // Since n >= 1
        assert n >= 1;
        assert 2 * n >= n + 1;
      }
      n + 1;
    }
  }
}

lemma PowerMonotonic(base: nat, exp1: nat, exp2: nat)
  requires base > 1
  requires exp1 <= exp2
  ensures power(base, exp1) <= power(base, exp2)
{
  if exp1 == exp2 {
    // Equal case
    assert power(base, exp1) == power(base, exp2);
  } else {
    // exp1 < exp2
    assert exp1 < exp2;

    if exp1 == 0 {
      assert power(base, exp1) == 1;
      PowerPositive(base, exp2);
      assert power(base, exp2) >= 1;
    } else {
      // Both exp1 and exp2 are positive
      PowerMonotonic(base, exp1 - 1, exp2 - 1);

      calc <= {
        power(base, exp1);
        base * power(base, exp1 - 1);
        { // Induction hypothesis
          assert power(base, exp1 - 1) <= power(base, exp2 - 1);
        }
        base * power(base, exp2 - 1);
        power(base, exp2);
      }
    }
  }
}

lemma PowerPositive(base: nat, exp: nat)
  requires base > 0
  ensures power(base, exp) > 0
{
  if exp == 0 {
    assert power(base, 0) == 1;
  } else {
    PowerPositive(base, exp - 1);
    assert power(base, exp) == base * power(base, exp - 1);
    assert base > 0 && power(base, exp - 1) > 0;
  }
}

lemma FibonacciInequality(n: nat)
  requires n >= 1
  ensures fib(n) <= power(2, n - 1)
{
  if n == 1 {
    // Base case
    assert fib(1) == 1;
    assert power(2, 0) == 1;
  } else if n == 2 {
    // Base case
    assert fib(2) == 1;
    assert power(2, 1) == 2;
    assert 1 <= 2;
  } else {
    // Inductive step (n >= 3)
    assert n >= 3;
    FibonacciInequality(n - 1);
    FibonacciInequality(n - 2);

    calc <= {
      fib(n);
      fib(n - 1) + fib(n - 2);
      { // Induction hypotheses
        assert fib(n - 1) <= power(2, n - 2);
        assert fib(n - 2) <= power(2, n - 3);
      }
      power(2, n - 2) + power(2, n - 3);
      { // Factor out power(2, n - 3)
        assert power(2, n - 2) == 2 * power(2, n - 3);
      }
      2 * power(2, n - 3) + power(2, n - 3);
      3 * power(2, n - 3);
      { // 3 * 2^(n-3) <= 4 * 2^(n-3) = 2^(n-1)
        assert 3 <= 4;
        assert power(2, n - 1) == 4 * power(2, n - 3);
      }
      power(2, n - 1);
    }
  }
}

lemma StrongInduction(n: nat, P: nat -> bool)
  requires forall k :: 0 <= k < n ==> P(k)
  requires forall m :: m >= n && (forall j :: n <= j < m ==> P(j)) ==> P(m)
  ensures P(n)
{
  // This demonstrates the strong induction principle
  // Base case: all k < n satisfy P(k) by hypothesis
  // Inductive case: if all j in [n, m) satisfy P, then P(m) holds

  // The proof would proceed by showing P(n) directly
  // using the second hypothesis with m = n
  assert forall j :: n <= j < n ==> P(j); // Vacuously true
}

lemma CompleteInduction(n: nat, P: nat -> bool)
  requires P(0)
  requires forall k: nat :: k > 0 && (forall j: nat :: j < k ==> P(j)) ==> P(k)
  ensures P(n)
{
  if n == 0 {
    // Base case
    assert P(0);
  } else {
    // Need to show all j < n satisfy P(j)
    forall j: nat | j < n
      ensures P(j)
    {
      if j == 0 {
        assert P(0);
      } else {
        CompleteInduction(j, P);
      }
    }

    // Now apply the inductive hypothesis
    assert forall j: nat :: j < n ==> P(j);
    assert P(n);
  }
}