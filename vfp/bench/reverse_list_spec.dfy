function reverse<T>(l: seq<T>): seq<T>

lemma {:axiom} reverse_permutes<T>(l: seq<T>)
  ensures forall x :: x in l <==> x in reverse(l)

lemma {:axiom} reverse_involutes<T>(l: seq<T>)
  ensures reverse(reverse(l)) == l