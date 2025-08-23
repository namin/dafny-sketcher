function dedup(xs: seq<int>): seq<int>
{
  if |xs| == 0 then []
  else if xs[0] in xs[1..] then dedup(xs[1..])
  else [xs[0]] + dedup(xs[1..])
}

predicate {:spec} noDuplicates(xs: seq<int>)
{
  forall i, j :: 0 <= i < j < |xs| ==> xs[i] != xs[j]
}

function {:spec} toSet(xs: seq<int>): set<int>
{
  set x | x in xs
}

lemma {:axiom} dedupCorrect(xs: seq<int>)
  ensures noDuplicates(dedup(xs))
  ensures toSet(dedup(xs)) == toSet(xs)