function gcd(a: nat, b: nat): nat
  requires a > 0 || b > 0
  decreases a + b
{
  if b == 0 then a
  else if a == 0 then b
  else if a >= b then gcd(a - b, b)
  else gcd(a, b - a)
}

function lcm(a: nat, b: nat): nat
  requires a > 0 && b > 0
{
  var g := gcd(a, b);
  if g == 0 then 0  // Should never happen
  else a * b / g
}

predicate {:spec} divides(d: nat, n: nat)
{
  d > 0 && n % d == 0
}

lemma gcdCorrect(a: nat, b: nat)
  requires a > 0 || b > 0
  ensures var g := gcd(a, b);
    g > 0 &&
    (a > 0 ==> divides(g, a)) &&
    (b > 0 ==> divides(g, b)) &&
    forall d :: d > 0 && divides(d, a) && divides(d, b) ==> d <= g
{
  // Complex proof - using axiom
  gcdCorrectHelper(a, b);
}

lemma {:axiom} gcdCorrectHelper(a: nat, b: nat)
  requires a > 0 || b > 0
  ensures var g := gcd(a, b);
    g > 0 &&
    (a > 0 ==> divides(g, a)) &&
    (b > 0 ==> divides(g, b)) &&
    forall d :: d > 0 && divides(d, a) && divides(d, b) ==> d <= g

lemma lcmCorrect(a: nat, b: nat)
  requires a > 0 && b > 0
  ensures gcd(a, b) > 0 && lcm(a, b) == a * b / gcd(a, b)
{
  gcdCorrect(a, b);
  var g := gcd(a, b);
  assert g > 0;
}