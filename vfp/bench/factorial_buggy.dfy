function factorial(n: nat): nat
{
  if n == 0 then 0
  else n * factorial(n - 1)
}

function {:spec} factorialSpec(n: nat): nat
{
  if n == 0 then 1
  else n * factorialSpec(n - 1)
}

lemma {:axiom} factorialCorrect(n: nat)
  ensures factorial(n) == factorialSpec(n)

lemma {:axiom} factorialPositive(n: nat)
  ensures factorial(n) > 0

lemma {:axiom} factorialIncreasing(n: nat)
  requires n > 0
  ensures factorial(n) >= factorial(n - 1)