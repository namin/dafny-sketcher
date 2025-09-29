// List operations: append, length, nth element

function {:spec} length<T>(l: seq<T>): nat
{
  |l|
}

function {:spec} append<T>(l1: seq<T>, l2: seq<T>): seq<T>
{
  l1 + l2
}

function {:spec} nth<T>(l: seq<T>, n: nat): T
  requires n < |l|
{
  l[n]
}

predicate {:spec} contains<T(==)>(l: seq<T>, x: T)
{
  x in l
}

function {:spec} indexOf<T(==)>(l: seq<T>, x: T): int
  requires x in l
{
  if l[0] == x then 0
  else 1 + indexOf(l[1..], x)
}

function {:spec} take<T>(l: seq<T>, n: nat): seq<T>
{
  if n >= |l| then l
  else l[..n]
}

function {:spec} drop<T>(l: seq<T>, n: nat): seq<T>
{
  if n >= |l| then []
  else l[n..]
}

function {:spec} filter<T>(l: seq<T>, p: T -> bool): seq<T>
{
  if |l| == 0 then []
  else if p(l[0]) then [l[0]] + filter(l[1..], p)
  else filter(l[1..], p)
}

function {:spec} listMap<T, U>(l: seq<T>, f: T -> U): seq<U>
{
  if |l| == 0 then []
  else [f(l[0])] + listMap(l[1..], f)
}

lemma AppendAssociative<T>(a: seq<T>, b: seq<T>, c: seq<T>)
  ensures append(append(a, b), c) == append(a, append(b, c))
{
  // Dafny proves this automatically
}

lemma AppendNeutral<T>(l: seq<T>)
  ensures append(l, []) == l
  ensures append([], l) == l
{
  // Dafny proves this automatically
}

lemma AppendLength<T>(l1: seq<T>, l2: seq<T>)
  ensures length(append(l1, l2)) == length(l1) + length(l2)
{
  // Dafny proves this automatically
}

lemma NthAppend<T>(l1: seq<T>, l2: seq<T>, n: nat)
  requires n < |l1| + |l2|
  ensures nth(append(l1, l2), n) == (if n < |l1| then nth(l1, n) else nth(l2, n - |l1|))
{
  // Dafny proves this automatically
}

lemma IndexOfCorrect<T>(l: seq<T>, x: T)
  requires x in l
  ensures 0 <= indexOf(l, x) < |l|
  ensures l[indexOf(l, x)] == x
  ensures forall i :: 0 <= i < indexOf(l, x) ==> l[i] != x
{
  if l[0] == x {
    // Base case
  } else {
    IndexOfCorrect(l[1..], x);
  }
}

lemma TakeDropConcat<T>(l: seq<T>, n: nat)
  ensures append(take(l, n), drop(l, n)) == l
{
  if n >= |l| {
    assert take(l, n) == l;
    assert drop(l, n) == [];
  }
}

lemma FilterSubset<T>(l: seq<T>, p: T -> bool, x: T)
  requires x in filter(l, p)
  ensures x in l && p(x)
{
  if |l| > 0 {
    if p(l[0]) && x == l[0] {
      // Found it
    } else if p(l[0]) {
      assert x in filter(l[1..], p);
      FilterSubset(l[1..], p, x);
    } else {
      FilterSubset(l[1..], p, x);
    }
  }
}

lemma MapLength<T, U>(l: seq<T>, f: T -> U)
  ensures |listMap(l, f)| == |l|
{
  if |l| == 0 {
    // Base case
  } else {
    MapLength(l[1..], f);
  }
}

lemma MapCompose<T, U, V>(l: seq<T>, f: T -> U, g: U -> V)
  ensures listMap(listMap(l, f), g) == listMap(l, (x: T) => g(f(x)))
{
  if |l| == 0 {
    // Base case
  } else {
    MapCompose(l[1..], f, g);
  }
}