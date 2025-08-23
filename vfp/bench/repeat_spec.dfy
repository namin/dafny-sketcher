function repeat(x: int, n: nat): seq<int>

lemma {:axiom} repeat_correct(x: int, n: nat)
  ensures |repeat(x, n)| == n
  ensures forall i :: 0 <= i < n ==> repeat(x, n)[i] == x