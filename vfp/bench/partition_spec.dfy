function partition(s: seq<int>): (seq<int>, seq<int>)

predicate {:spec} isEven(n: int)
{
  n % 2 == 0
}

lemma {:axiom} partitionCorrect(s: seq<int>)
  ensures var (evens, odds) := partition(s);
    (forall x :: x in evens ==> isEven(x)) &&
    (forall x :: x in odds ==> !isEven(x)) &&
    |evens| + |odds| == |s| &&
    multiset(evens + odds) == multiset(s)