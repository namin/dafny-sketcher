function repeat(x: int, n: nat): seq<int>
{
  if n == 0 then []
  else [x] + repeat(x, n - 1)
}

lemma repeat_correct(x: int, n: nat)
  ensures |repeat(x, n)| == n
  ensures forall i :: 0 <= i < n ==> repeat(x, n)[i] == x
{
  if n == 0 {
  } else {
    repeat_correct(x, n - 1);
    assert repeat(x, n) == [x] + repeat(x, n - 1);
    assert |repeat(x, n)| == 1 + |repeat(x, n - 1)| == 1 + (n - 1) == n;
    forall i | 0 <= i < n
      ensures repeat(x, n)[i] == x
    {
      if i == 0 {
        assert repeat(x, n)[0] == x;
      } else {
        assert repeat(x, n)[i] == repeat(x, n - 1)[i - 1] == x;
      }
    }
  }
}