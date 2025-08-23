// Finding maximum element in a sequence

predicate {:spec} isMax(s: seq<int>, m: int)
{
  m in s && forall x :: x in s ==> x <= m
}

function max(s: seq<int>): int
  requires |s| > 0
{
  if |s| == 1 then s[0]
  else 
    var restMax := max(s[1..]);
    if s[0] > restMax then s[0] else restMax
}

lemma {:axiom} maxIsCorrect(s: seq<int>)
  requires |s| > 0
  ensures isMax(s, max(s))