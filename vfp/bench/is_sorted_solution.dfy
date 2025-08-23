function isSorted(s: seq<int>): bool
{
  forall i, j :: 0 <= i < j < |s| ==> s[i] <= s[j]
}

function isSortedBetween(s: seq<int>, lo: int, hi: int): bool
  requires 0 <= lo <= hi <= |s|
{
  forall i, j :: lo <= i < j < hi ==> s[i] <= s[j]
}

lemma isSortedCorrect(s: seq<int>)
  ensures isSorted(s) <==> forall i, j :: 0 <= i < j < |s| ==> s[i] <= s[j]
{
  // Trivial by definition
}

lemma isSortedTransitive(s: seq<int>, i: int, j: int, k: int)
  requires isSorted(s)
  requires 0 <= i <= j <= k < |s|
  ensures s[i] <= s[j] <= s[k]
{
  if i < j {
    assert s[i] <= s[j];
  } else {
    assert i == j;
    assert s[i] == s[j];
  }
  
  if j < k {
    assert s[j] <= s[k];
  } else {
    assert j == k;
    assert s[j] == s[k];
  }
}

lemma isSortedSubsequence(s: seq<int>, lo: int, hi: int)
  requires 0 <= lo <= hi <= |s|
  requires isSorted(s)
  ensures isSortedBetween(s, lo, hi)
{
  forall i, j | lo <= i < j < hi
    ensures s[i] <= s[j]
  {
    assert 0 <= i < j < |s|;
    assert s[i] <= s[j];
  }
}