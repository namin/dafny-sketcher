predicate {:spec} sorted(s: seq<int>)
{
  forall i, j :: 0 <= i < j < |s| ==> s[i] <= s[j]
}

function binarySearch(s: seq<int>, key: int): int
  requires sorted(s)

lemma {:axiom} binarySearchCorrect(s: seq<int>, key: int)
  requires sorted(s)
  ensures var idx := binarySearch(s, key);
    0 <= idx <= |s| &&
    (idx < |s| ==> s[idx] == key) &&
    (idx == |s| ==> key !in s)