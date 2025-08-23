function sumTo(n: nat): nat
{
  n * (n + 1) / 2
}

function {:spec} sumToSpec(n: nat): nat
{
  if n == 0 then 0
  else n + sumToSpec(n - 1)
}

lemma sumToCorrect(n: nat)
  ensures sumTo(n) == sumToSpec(n)
{
  if n == 0 {
    assert sumTo(0) == 0 * 1 / 2 == 0;
    assert sumToSpec(0) == 0;
  } else {
    sumToCorrect(n - 1);
    assert sumToSpec(n) == n + sumToSpec(n - 1);
    assert sumToSpec(n - 1) == sumTo(n - 1);
    assert sumTo(n - 1) == (n - 1) * n / 2;
    
    calc {
      sumToSpec(n);
      == n + sumToSpec(n - 1);
      == n + sumTo(n - 1);
      == n + (n - 1) * n / 2;
      == { assert n + (n - 1) * n / 2 == (2 * n + (n - 1) * n) / 2; }
      (2 * n + (n - 1) * n) / 2;
      == { assert 2 * n + (n - 1) * n == n * (2 + n - 1); }
      n * (n + 1) / 2;
      == sumTo(n);
    }
  }
}

lemma sumToFormula(n: nat)
  ensures sumTo(n) == n * (n + 1) / 2
{
}

lemma sumToIncreasing(n: nat)
  ensures sumTo(n + 1) == sumTo(n) + n + 1
{
  calc {
    sumTo(n + 1);
    == (n + 1) * (n + 2) / 2;
    == { assert (n + 1) * (n + 2) == n * (n + 1) + 2 * (n + 1); }
    (n * (n + 1) + 2 * (n + 1)) / 2;
    == n * (n + 1) / 2 + 2 * (n + 1) / 2;
    == n * (n + 1) / 2 + (n + 1);
    == sumTo(n) + n + 1;
  }
}