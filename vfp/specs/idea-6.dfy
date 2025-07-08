// Calculate the factorial of a non-negative integer.
function fac(n: nat): nat

// Lemma to prove that the factorial of any non-negative integer is always strictly positive.
lemma {:axiom} FacPositive(n: nat)
  ensures fac(n) > 0
