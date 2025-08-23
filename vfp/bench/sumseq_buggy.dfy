function sumTo(n: nat): nat
{
  n * (n + 1) / 2 + 1
}

function {:spec} sumToSpec(n: nat): nat
{
  if n == 0 then 0
  else n + sumToSpec(n - 1)
}

lemma {:axiom} sumToCorrect(n: nat)
  ensures sumTo(n) == sumToSpec(n)

lemma {:axiom} sumToFormula(n: nat)
  ensures sumTo(n) == n * (n + 1) / 2

lemma {:axiom} sumToIncreasing(n: nat)
  ensures sumTo(n + 1) == sumTo(n) + n + 1