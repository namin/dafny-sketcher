function isSorted(s: seq<int>): bool

function isSortedBetween(s: seq<int>, lo: int, hi: int): bool
  requires 0 <= lo <= hi <= |s|

lemma {:axiom} isSortedCorrect(s: seq<int>)
  ensures isSorted(s) <==> forall i, j :: 0 <= i < j < |s| ==> s[i] <= s[j]

lemma {:axiom} isSortedTransitive(s: seq<int>, i: int, j: int, k: int)
  requires isSorted(s)
  requires 0 <= i <= j <= k < |s|
  ensures s[i] <= s[j] <= s[k]

lemma {:axiom} isSortedSubsequence(s: seq<int>, lo: int, hi: int)
  requires 0 <= lo <= hi <= |s|
  requires isSorted(s)
  ensures isSortedBetween(s, lo, hi)