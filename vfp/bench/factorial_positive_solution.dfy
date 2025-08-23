function fac(n: nat): nat
{
  if n == 0 then 1
  else n * fac(n - 1)
}

lemma FacPositive(n: nat)
  ensures fac(n) > 0
{
  if n == 0 {
    assert fac(0) == 1 > 0;
  } else {
    FacPositive(n - 1);
    assert fac(n - 1) > 0;
    assert n > 0;
    assert fac(n) == n * fac(n - 1) > 0;
  }
}