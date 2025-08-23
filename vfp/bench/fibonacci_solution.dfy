function fib(n: nat): nat
{
  if n == 0 then 0
  else if n == 1 then 1
  else fib(n-1) + fib(n-2)
}

function fibPair(n: nat): (nat, nat)
{
  if n == 0 then (0, 1)
  else
    var (a, b) := fibPair(n-1);
    (b, a + b)
}

lemma fibCorrect(n: nat)
  ensures fib(0) == 0
  ensures fib(1) == 1
  ensures n >= 2 ==> fib(n) == fib(n-1) + fib(n-2)
{
  // Trivial by definition
}

lemma fibPairCorrect(n: nat)
  ensures fibPair(n) == (fib(n), fib(n+1))
{
  if n == 0 {
    assert fibPair(0) == (0, 1);
    assert fib(0) == 0;
    assert fib(1) == 1;
  } else {
    fibPairCorrect(n-1);
    var (a, b) := fibPair(n-1);
    assert a == fib(n-1);
    assert b == fib(n);
    assert fibPair(n) == (b, a + b);
    assert fibPair(n) == (fib(n), fib(n-1) + fib(n));
    if n == 1 {
      assert fib(2) == fib(1) + fib(0) == 1 + 0 == 1;
      assert fibPair(1) == (1, 1);
      assert fib(1) == 1;
    } else {
      assert fib(n+1) == fib(n) + fib(n-1);
    }
  }
}

lemma fibIncreasing(n: nat)
  ensures fib(n) <= fib(n+1)
{
  if n == 0 {
    assert fib(0) == 0;
    assert fib(1) == 1;
  } else if n == 1 {
    assert fib(1) == 1;
    assert fib(2) == 1;
  } else {
    assert fib(n+1) == fib(n) + fib(n-1);
    assert fib(n-1) >= 0;
    assert fib(n+1) >= fib(n);
  }
}