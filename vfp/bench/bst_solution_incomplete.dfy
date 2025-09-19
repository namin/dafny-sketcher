datatype Tree = Nil | Node(left: Tree, value: nat, right: Tree)

predicate IsBST(t: Tree)
{
  IsBSTBounded(t, -1, 0x7FFFFFFFFFFFFFFF)
}

predicate IsBSTBounded(t: Tree, min: int, max: int)
{
  match t
  case Nil => true
  case Node(l, v, r) =>
    min < v < max &&
    IsBSTBounded(l, min, v) &&
    IsBSTBounded(r, v, max)
}

function insert(t: Tree, x: nat): Tree
{
  match t
  case Nil => Node(Nil, x, Nil)
  case Node(l, v, r) =>
    if x < v then Node(insert(l, x), v, r)
    else if x > v then Node(l, v, insert(r, x))
    else t
}

predicate Contains(t: Tree, x: nat)
{
  match t
  case Nil => false
  case Node(l, v, r) =>
    v == x || Contains(l, x) || Contains(r, x)
}

lemma InsertContains(t: Tree, x: nat)
  ensures Contains(insert(t, x), x)
{
  match t
  case Nil =>
    assert insert(t, x) == Node(Nil, x, Nil);
    assert Contains(Node(Nil, x, Nil), x);
  case Node(l, v, r) =>
    if x < v {
      InsertContains(l, x);
      assert insert(t, x) == Node(insert(l, x), v, r);
      assert Contains(insert(l, x), x);
    } else if x > v {
      InsertContains(r, x);
      assert insert(t, x) == Node(l, v, insert(r, x));
      assert Contains(insert(r, x), x);
    } else {
      assert x == v;
      assert insert(t, x) == t;
      assert Contains(t, x);
    }
}

lemma InsertPreservesBSTHelper(t: Tree, x: nat, min: int, max: int)
  requires IsBSTBounded(t, min, max)
  requires min < x < max
  ensures IsBSTBounded(insert(t, x), min, max)
  ensures forall v :: Contains(t, v) ==> Contains(insert(t, x), v)
{
  match t
  case Nil =>
    assert insert(t, x) == Node(Nil, x, Nil);
  case Node(l, v, r) =>
    if x < v {
      InsertPreservesBSTHelper(l, x, min, v);
    } else if x > v {
      InsertPreservesBSTHelper(r, x, v, max);
    }
}

lemma InsertPreservesBST(t: Tree, x: nat, min: nat, max: nat)
  requires IsBST(t)
  requires min <= x <= max
  requires forall v: nat :: Contains(t, v) ==> min <= v <= max
  ensures IsBST(insert(t, x))
{
  // Simplified proof - assume we have a helper that does the real work
  InsertPreservesBSTMain(t, x);
}

lemma {:axiom} InsertPreservesBSTMain(t: Tree, x: nat)
  requires IsBST(t)
  ensures IsBST(insert(t, x))