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
    if s[0] >= restMax then s[0] else restMax
}

lemma maxIsCorrect(s: seq<int>)
  requires |s| > 0
  ensures isMax(s, max(s))
{
  if |s| == 1 {
    // Base case is trivial
  } else {
    var restMax := max(s[1..]);
    maxIsCorrect(s[1..]);
    // We know isMax(s[1..], restMax)
    // So restMax in s[1..] and forall x in s[1..] :: x <= restMax
    
    if s[0] >= restMax {
      // max returns s[0]
      // Need to show: s[0] in s (trivial) and forall x in s :: x <= s[0]
      forall x | x in s
        ensures x <= s[0]
      {
        if x == s[0] {
          // x <= s[0] trivially
        } else {
          // x must be in s[1..]
          assert x in s[1..];
          // From induction hypothesis: x <= restMax
          // We know s[0] >= restMax
          // Therefore x <= s[0]
        }
      }
    } else {
      // max returns restMax
      // Need to show: restMax in s and forall x in s :: x <= restMax
      assert restMax in s[1..];
      assert restMax in s;
      
      forall x | x in s
        ensures x <= restMax
      {
        if x == s[0] {
          // We know s[0] < restMax
        } else {
          // x must be in s[1..]
          assert x in s[1..];
          // From induction hypothesis: x <= restMax
        }
      }
    }
  }
}