function gcd(a: nat, b: nat): nat
  requires a > 0 || b > 0

function lcm(a: nat, b: nat): nat
  requires a > 0 && b > 0

predicate {:spec} divides(d: nat, n: nat)
{
  d > 0 && n % d == 0
}

lemma {:axiom} gcdCorrect(a: nat, b: nat)
  requires a > 0 || b > 0
  ensures var g := gcd(a, b);
    g > 0 &&
    (a > 0 ==> divides(g, a)) &&
    (b > 0 ==> divides(g, b)) &&
    forall d :: d > 0 && divides(d, a) && divides(d, b) ==> d <= g

lemma {:axiom} lcmCorrect(a: nat, b: nat)
  requires a > 0 && b > 0
  ensures gcd(a, b) > 0 && lcm(a, b) == a * b / gcd(a, b)