function fac(n: nat): nat

lemma {:axiom} FacPositive(n: nat)
  ensures fac(n) > 0