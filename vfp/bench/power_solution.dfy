function power(base: int, exp: nat): int
{
  if exp == 0 then 1
  else base * power(base, exp - 1)
}

function {:spec} powerSpec(base: int, exp: nat): int
  decreases exp
{
  if exp == 0 then 1
  else base * powerSpec(base, exp - 1)
}

lemma powerCorrect(base: int, exp: nat)
  ensures power(base, exp) == powerSpec(base, exp)
{
}

lemma powerZero(base: int)
  ensures power(base, 0) == 1
{
}

lemma powerOne(base: int)
  ensures power(base, 1) == base
{
  calc {
    power(base, 1);
    == base * power(base, 0);
    == base * 1;
    == base;
  }
}

lemma powerAdd(base: int, exp1: nat, exp2: nat)
  ensures power(base, exp1 + exp2) == power(base, exp1) * power(base, exp2)
{
  if exp1 == 0 {
    calc {
      power(base, exp1 + exp2);
      == power(base, 0 + exp2);
      == power(base, exp2);
      == 1 * power(base, exp2);
      == power(base, 0) * power(base, exp2);
      == power(base, exp1) * power(base, exp2);
    }
  } else {
    powerAdd(base, exp1 - 1, exp2);
    calc {
      power(base, exp1 + exp2);
      == { assert exp1 + exp2 == (exp1 - 1) + exp2 + 1; }
      power(base, (exp1 - 1) + exp2 + 1);
      == base * power(base, (exp1 - 1) + exp2);
      == { powerAdd(base, exp1 - 1, exp2); }
      base * (power(base, exp1 - 1) * power(base, exp2));
      == (base * power(base, exp1 - 1)) * power(base, exp2);
      == power(base, exp1) * power(base, exp2);
    }
  }
}