function partition(s: seq<int>): (seq<int>, seq<int>)
{
  if |s| == 0 then ([], [])
  else
    var (evens, odds) := partition(s[1..]);
    if isEven(s[0]) then ([s[0]] + evens, odds)
    else (evens, [s[0]] + odds)
}

predicate {:spec} isEven(n: int)
{
  n % 2 == 0
}

lemma partitionCorrect(s: seq<int>)
  ensures var (evens, odds) := partition(s);
    (forall x :: x in evens ==> isEven(x)) &&
    (forall x :: x in odds ==> !isEven(x)) &&
    |evens| + |odds| == |s| &&
    multiset(evens + odds) == multiset(s)
{
  if |s| == 0 {
  } else {
    partitionCorrect(s[1..]);
    var (evens, odds) := partition(s);
    var (evens', odds') := partition(s[1..]);
    
    if isEven(s[0]) {
      assert evens == [s[0]] + evens';
      assert odds == odds';
      assert multiset(evens + odds) == multiset([s[0]] + evens' + odds');
      assert multiset([s[0]] + evens' + odds') == multiset{s[0]} + multiset(evens' + odds');
      assert multiset(evens' + odds') == multiset(s[1..]);
      assert multiset{s[0]} + multiset(s[1..]) == multiset(s);
    } else {
      assert evens == evens';
      assert odds == [s[0]] + odds';
      assert multiset(evens + odds) == multiset(evens' + [s[0]] + odds');
      assert multiset(evens' + [s[0]] + odds') == multiset{s[0]} + multiset(evens' + odds');
      assert multiset(evens' + odds') == multiset(s[1..]);
      assert multiset{s[0]} + multiset(s[1..]) == multiset(s);
    }
  }
}