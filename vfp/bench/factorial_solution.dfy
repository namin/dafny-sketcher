function factorial(n: nat): nat
{
  if n == 0 then 1
  else n * factorial(n - 1)
}

function {:spec} factorialSpec(n: nat): nat
{
  if n == 0 then 1
  else n * factorialSpec(n - 1)
}

lemma factorialCorrect(n: nat)
  ensures factorial(n) == factorialSpec(n)
{
}

lemma factorialPositive(n: nat)
  ensures factorial(n) > 0
{
  if n == 0 {
    assert factorial(0) == 1;
  } else {
    factorialPositive(n - 1);
    assert factorial(n - 1) > 0;
    assert n > 0;
    assert factorial(n) == n * factorial(n - 1);
    assert n * factorial(n - 1) > 0;
  }
}

lemma factorialIncreasing(n: nat)
  requires n > 0
  ensures factorial(n) >= factorial(n - 1)
{
  factorialPositive(n - 1);
  assert factorial(n) == n * factorial(n - 1);
  assert n >= 1;
  assert factorial(n - 1) > 0;
  
  calc {
    factorial(n);
    == n * factorial(n - 1);
    >= 1 * factorial(n - 1);
    == factorial(n - 1);
  }
}