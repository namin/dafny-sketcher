datatype Tree = Nil | Node(left: Tree, value: nat, right: Tree)

predicate {:spec} IsBST(t: Tree)
{
  IsBSTBounded(t, -1, 0x7FFFFFFFFFFFFFFF)
}

predicate {:spec} IsBSTBounded(t: Tree, min: int, max: int)
{
  match t
  case Nil => true
  case Node(l, v, r) =>
    min < v < max &&
    IsBSTBounded(l, min, v) &&
    IsBSTBounded(r, v, max)
}

function insert(t: Tree, x: nat): Tree

predicate Contains(t: Tree, x: nat)

lemma {:axiom} InsertContains(t: Tree, x: nat)
  ensures Contains(insert(t, x), x)

lemma {:axiom} InsertPreservesBST(t: Tree, x: nat, min: nat, max: nat)
  requires IsBST(t)
  requires min <= x <= max
  requires forall v: nat :: Contains(t, v) ==> min <= v <= max
  ensures IsBST(insert(t, x))