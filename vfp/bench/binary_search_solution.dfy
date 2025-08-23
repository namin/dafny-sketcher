predicate {:spec} sorted(s: seq<int>)
{
  forall i, j :: 0 <= i < j < |s| ==> s[i] <= s[j]
}

function binarySearch(s: seq<int>, key: int): int
  requires sorted(s)
{
  binarySearchHelper(s, key, 0, |s|)
}

function binarySearchHelper(s: seq<int>, key: int, lo: int, hi: int): int
  requires 0 <= lo <= hi <= |s|
  requires sorted(s)
  decreases hi - lo
{
  if lo >= hi then |s|
  else
    var mid := lo + (hi - lo) / 2;
    if s[mid] == key then mid
    else if s[mid] > key then binarySearchHelper(s, key, lo, mid)
    else binarySearchHelper(s, key, mid + 1, hi)
}

lemma binarySearchCorrect(s: seq<int>, key: int)
  requires sorted(s)
  ensures var idx := binarySearch(s, key);
    0 <= idx <= |s| &&
    (idx < |s| ==> s[idx] == key) &&
    (idx == |s| ==> key !in s)
{
  binarySearchHelperCorrect(s, key, 0, |s|);
}

lemma binarySearchHelperCorrect(s: seq<int>, key: int, lo: int, hi: int)
  requires 0 <= lo <= hi <= |s|
  requires sorted(s)
  ensures var idx := binarySearchHelper(s, key, lo, hi);
    0 <= idx <= |s| &&
    (idx < |s| ==> s[idx] == key) &&
    (idx == |s| ==> (forall i :: lo <= i < hi ==> s[i] != key))
  decreases hi - lo
{
  if lo >= hi {
  } else {
    var mid := lo + (hi - lo) / 2;
    if s[mid] == key {
    } else if s[mid] > key {
      binarySearchHelperCorrect(s, key, lo, mid);
      var idx := binarySearchHelper(s, key, lo, mid);
      if idx == |s| {
        forall i | mid <= i < hi
          ensures s[i] != key
        {
          assert s[mid] > key;
          assert sorted(s);
          assert s[i] >= s[mid];
          assert s[i] > key;
        }
      }
    } else {
      binarySearchHelperCorrect(s, key, mid + 1, hi);
      var idx := binarySearchHelper(s, key, mid + 1, hi);
      if idx == |s| {
        forall i | lo <= i <= mid
          ensures s[i] != key
        {
          assert s[mid] < key;
          assert sorted(s);
          assert s[i] <= s[mid];
          assert s[i] < key;
        }
      }
    }
  }
}