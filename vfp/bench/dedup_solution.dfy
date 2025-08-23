function dedup(xs: seq<int>): seq<int>
{
  if |xs| == 0 then []
  else if xs[0] in dedup(xs[1..]) then dedup(xs[1..])
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

lemma dedupCorrect(xs: seq<int>)
  ensures noDuplicates(dedup(xs))
  ensures toSet(dedup(xs)) == toSet(xs)
{
  if |xs| == 0 {
  } else {
    dedupCorrect(xs[1..]);
    var rest := dedup(xs[1..]);
    
    if xs[0] in rest {
      assert dedup(xs) == rest;
      assert xs[0] in rest;
      assert toSet(rest) == toSet(xs[1..]);
      assert xs[0] in xs[1..];
      assert toSet(xs) == toSet(xs[1..]) + {xs[0]};
      assert toSet(xs) == toSet(xs[1..]);
    } else {
      assert dedup(xs) == [xs[0]] + rest;
      assert noDuplicates(rest);
      assert !(xs[0] in rest);
      
      forall i, j | 0 <= i < j < |dedup(xs)|
        ensures dedup(xs)[i] != dedup(xs)[j]
      {
        if i == 0 {
          assert dedup(xs)[0] == xs[0];
          assert dedup(xs)[j] == rest[j-1];
          assert !(xs[0] in rest);
        } else {
          assert dedup(xs)[i] == rest[i-1];
          assert dedup(xs)[j] == rest[j-1];
        }
      }
      
      assert toSet(dedup(xs)) == toSet([xs[0]] + rest);
      assert toSet([xs[0]] + rest) == {xs[0]} + toSet(rest);
      assert toSet(rest) == toSet(xs[1..]);
      assert toSet(xs) == {xs[0]} + toSet(xs[1..]);
    }
  }
}