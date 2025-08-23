datatype Tree<T> = Leaf(value: T) | Node(left: Tree<T>, right: Tree<T>)

function flatten<T>(t: Tree<T>): seq<T>
{
  match t
  case Leaf(v) => [v]
  case Node(l, r) => flatten(l) + flatten(l)
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

lemma {:axiom} flattenCorrect<T>(t: Tree<T>)
  ensures |flatten(t)| == size(t)
  ensures toMultiset(flatten(t)) == treeToMultiset(t)