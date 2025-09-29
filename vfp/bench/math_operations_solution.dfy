// Mathematical operations: GCD, LCM, primes, modular arithmetic

// Absolute value
function {:spec} abs(x: int): nat
{
  if x < 0 then -x else x
}

// Greatest Common Divisor using Euclidean algorithm
function {:spec} gcd(a: nat, b: nat): nat
  decreases b
{
  if b == 0 then a
  else gcd(b, a % b)
}

// Least Common Multiple
function {:spec} lcm(a: nat, b: nat): nat
  requires a > 0 && b > 0
{
  var g := gcd(a, b);
  assert g > 0 by { GcdPositive(a, b); }
  a / g * b  // Reordered to avoid overflow and ensure positive
}

// Check if a number divides another
predicate {:spec} divides(d: nat, n: nat)
  requires d > 0
{
  n % d == 0
}

// Check if a number is prime
predicate {:spec} isPrime(n: nat)
{
  n > 1 && forall d :: 2 <= d < n ==> !divides(d, n)
}

// Check if two numbers are coprime (relatively prime)
predicate {:spec} coprime(a: nat, b: nat)
  requires a > 0 && b > 0
{
  gcd(a, b) == 1
}

// Modular exponentiation: (base^exp) mod m
function {:spec} modPow(base: nat, exp: nat, m: nat): nat
  requires m > 0
  decreases exp
{
  if exp == 0 then 1 % m
  else if exp % 2 == 0 then
    var half := modPow(base, exp / 2, m);
    (half * half) % m
  else
    ((base % m) * modPow(base, exp - 1, m)) % m
}

// Fibonacci function
function {:spec} fib(n: nat): nat
{
  if n == 0 then 0
  else if n == 1 then 1
  else fib(n - 1) + fib(n - 2)
}

// Factorial function
function {:spec} fact(n: nat): nat
{
  if n == 0 then 1
  else n * fact(n - 1)
}

// Binomial coefficient (n choose k)
function {:spec} binomial(n: nat, k: nat): nat
  requires k <= n
{
  var denominator := fact(k) * fact(n - k);
  if denominator == 0 then 0  // Can't happen but helps verifier
  else fact(n) / denominator
}

// Sum of first n natural numbers
function {:spec} sumToN(n: nat): nat
{
  if n == 0 then 0
  else n + sumToN(n - 1)
}

// Check if a number is perfect (sum of divisors equals the number)
predicate {:spec} isPerfect(n: nat)
  requires n > 0
{
  sumOfDivisors(n) == 2 * n  // Including n itself
}

function {:spec} sumOfDivisors(n: nat): nat
  requires n > 0
{
  sumOfDivisorsHelper(n, n)
}

function sumOfDivisorsHelper(n: nat, d: nat): nat
  requires n > 0
  requires d > 0
  decreases d
{
  if d == 1 then 1
  else if divides(d, n) then d + sumOfDivisorsHelper(n, d - 1)
  else sumOfDivisorsHelper(n, d - 1)
}

// --- Lemmas for correctness ---

lemma GcdZero(a: nat)
  ensures gcd(a, 0) == a
{
  // Automatic by definition
}

lemma GcdPositive(a: nat, b: nat)
  requires a > 0 || b > 0
  ensures gcd(a, b) > 0
  decreases b
{
  if b == 0 {
    assert gcd(a, b) == a;
    assert a > 0;
  } else {
    GcdPositive(b, a % b);
  }
}

lemma GcdDividesBoth(a: nat, b: nat)
  requires a > 0 && b > 0
  ensures gcd(a, b) > 0
{
  GcdPositive(a, b);
}

lemma PrimeHasOnlyTwoDivisors(n: nat)
  requires isPrime(n)
  ensures divides(1, n) && divides(n, n)
  ensures forall d: nat :: d > 0 && d < n && d != 1 ==> !divides(d, n)
{
  assert divides(1, n);
  assert divides(n, n);
  forall d: nat | d > 0 && d < n && d != 1
    ensures !divides(d, n)
  {
    if d >= 2 {
      assert 2 <= d < n;
      // By definition of isPrime
    }
  }
}

lemma TwoPrime()
  ensures isPrime(2)
{
  assert forall d :: 2 <= d < 2 ==> !divides(d, 2);
}

lemma ThreePrime()
  ensures isPrime(3)
{
  assert !divides(2, 3);
}

function Power(base: nat, exp: nat): nat
  decreases exp
{
  if exp == 0 then 1
  else base * Power(base, exp - 1)
}

lemma PowerSquare(base: nat)
  ensures Power(base, 2) == base * base
{
  assert Power(base, 2) == base * Power(base, 1);
  assert Power(base, 1) == base;
}

lemma PowerAddition(base: nat, exp1: nat, exp2: nat)
  ensures Power(base, exp1 + exp2) == Power(base, exp1) * Power(base, exp2)
  decreases exp1
{
  if exp1 == 0 {
    assert Power(base, 0) == 1;
  } else {
    PowerAddition(base, exp1 - 1, exp2);
    assert Power(base, exp1 + exp2) == base * Power(base, exp1 - 1 + exp2);
    assert Power(base, exp1) == base * Power(base, exp1 - 1);
  }
}

lemma SumFormula(n: nat)
  ensures sumToN(n) == n * (n + 1) / 2
{
  if n == 0 {
    assert sumToN(0) == 0;
  } else {
    SumFormula(n - 1);
    assert sumToN(n - 1) == (n - 1) * n / 2;
    assert sumToN(n) == n + sumToN(n - 1);
    assert sumToN(n) == n + (n - 1) * n / 2;
    assert sumToN(n) == (2 * n + (n - 1) * n) / 2;
    assert sumToN(n) == (2 * n + n * n - n) / 2;
    assert sumToN(n) == (n + n * n) / 2;
    assert sumToN(n) == n * (1 + n) / 2;
  }
}

lemma FactorialPositive(n: nat)
  ensures fact(n) > 0
{
  if n == 0 {
    assert fact(0) == 1;
  } else {
    FactorialPositive(n - 1);
  }
}

lemma FibonacciMonotonic(n: nat)
  requires n > 0
  ensures fib(n) <= fib(n + 1)
{
  if n == 1 {
    assert fib(1) == 1;
    assert fib(2) == 1;
  } else {
    assert fib(n + 1) == fib(n) + fib(n - 1);
    if n > 1 {
      assert fib(n - 1) >= 0;
    }
  }
}

lemma BinomialSymmetry(n: nat, k: nat)
  requires k <= n
  ensures binomial(n, k) == binomial(n, n - k)
{
  assert fact(k) * fact(n - k) == fact(n - k) * fact(k);
}