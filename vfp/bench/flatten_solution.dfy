datatype Tree<T> = Leaf(value: T) | Node(left: Tree<T>, right: Tree<T>)

function flatten<T>(t: Tree<T>): seq<T>
{
  match t
  case Leaf(v) => [v]
  case Node(l, r) => flatten(l) + flatten(r)
}

function size<T>(t: Tree<T>): nat
{
  match t
  case Leaf(_) => 1
  case Node(l, r) => size(l) + size(r)
}

function toMultiset<T>(s: seq<T>): multiset<T>
{
  if |s| == 0 then multiset{}
  else multiset{s[0]} + toMultiset(s[1..])
}

function treeToMultiset<T>(t: Tree<T>): multiset<T>
{
  match t
  case Leaf(v) => multiset{v}
  case Node(l, r) => treeToMultiset(l) + treeToMultiset(r)
}

lemma toMultisetAppend<T>(s1: seq<T>, s2: seq<T>)
  ensures toMultiset(s1 + s2) == toMultiset(s1) + toMultiset(s2)
{
  if |s1| == 0 {
    assert s1 + s2 == s2;
  } else {
    toMultisetAppend(s1[1..], s2);
    assert s1 + s2 == [s1[0]] + (s1[1..] + s2);
  }
}

lemma flattenCorrect<T>(t: Tree<T>)
  ensures |flatten(t)| == size(t)
  ensures toMultiset(flatten(t)) == treeToMultiset(t)
{
  match t
  case Leaf(v) =>
    assert flatten(t) == [v];
    assert toMultiset([v]) == multiset{v};
  case Node(l, r) =>
    flattenCorrect(l);
    flattenCorrect(r);
    assert |flatten(t)| == |flatten(l) + flatten(r)| == |flatten(l)| + |flatten(r)|;
    assert |flatten(l)| == size(l);
    assert |flatten(r)| == size(r);
    toMultisetAppend(flatten(l), flatten(r));
    assert toMultiset(flatten(t)) == toMultiset(flatten(l) + flatten(r));
    assert toMultiset(flatten(l) + flatten(r)) == toMultiset(flatten(l)) + toMultiset(flatten(r));
    assert toMultiset(flatten(l)) == treeToMultiset(l);
    assert toMultiset(flatten(r)) == treeToMultiset(r);
}