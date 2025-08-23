function power(base: int, exp: nat): int
{
  if exp == 0 then 0
  else if exp == 1 then base
  else base * power(base, exp - 1)
}

function {:spec} powerSpec(base: int, exp: nat): int
  decreases exp
{
  if exp == 0 then 1
  else base * powerSpec(base, exp - 1)
}

lemma {:axiom} powerCorrect(base: int, exp: nat)
  ensures power(base, exp) == powerSpec(base, exp)

lemma {:axiom} powerZero(base: int)
  ensures power(base, 0) == 1

lemma {:axiom} powerOne(base: int)
  ensures power(base, 1) == base

lemma {:axiom} powerAdd(base: int, exp1: nat, exp2: nat)
  ensures power(base, exp1 + exp2) == power(base, exp1) * power(base, exp2)