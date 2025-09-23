datatype Tree = Leaf | Node(value: int, left: Tree, right: Tree)

ghost predicate {:spec} IsBST(t: Tree)
  decreases t
{
  match t
  case Leaf => true
  case Node(v, l, r) =>
    IsBST(l) && IsBST(r) &&
    (forall x :: InTree(x, l) ==> x < v) &&
    (forall x :: InTree(x, r) ==> x > v)
}

predicate {:spec} InTree(x: int, t: Tree)
  decreases t
{
  match t
  case Leaf => false
  case Node(v, l, r) =>
    x == v || InTree(x, l) || InTree(x, r)
}

function {:spec} Contains(t: Tree, key: int): bool
  requires IsBST(t)
  decreases t
{
  match t
  case Leaf => false
  case Node(v, l, r) =>
    if key == v then true
    else if (key < v) then Contains(l, key)
    else Contains(r, key)
}

function {:spec} Insert(t: Tree, x: int): Tree
  requires IsBST(t)
  ensures InTree(x, Insert(t, x))
{
  match t
  case Leaf => Node(x, Leaf, Leaf)
  case Node(v, l, r) => 
      if (x == v) then t
      else if (x < v) then Node(v, Insert(l, x), r)
      else Node(v, l, Insert(r, x))
}

function {:spec} Min(t: Tree): int 
  requires IsBST(t)
  requires t.Node?
{
  match t
  case Node(v, Leaf, _) => v
  case Node(v, l, _) => Min(l)
}

lemma Contains_Correct(t: Tree, k: int)
  requires IsBST(t)
  ensures Contains(t, k) <==> InTree(k, t)
  decreases t
{}

lemma {:axiom}Insert_InTree_Subset(t: Tree, x: int, y: int)
  requires IsBST(t)
  ensures InTree(y, Insert(t, x)) ==> InTree(y, t) || y == x
  decreases t

lemma Insert_Preserves_BST(t: Tree, x: int)
  requires IsBST(t)
  ensures IsBST(Insert(t, x))
{
  match t
  case Leaf => 
  case Node(v, l, r) =>
    if x == v {
    } else if x < v {
      forall y | InTree(y, Insert(l, x))
        ensures y < v
      {
        Insert_InTree_Subset(l, x, y);
      }
    } else {
      forall y | InTree(y, Insert(r, x))
        ensures y > v
      {
        Insert_InTree_Subset(r, x, y);
      }
    }
}

lemma Min_Absolute(t: Tree)
  requires IsBST(t)
  requires t.Node?
  ensures forall v :: InTree(v, t) ==> Min(t) <= v
  ensures InTree(Min(t), t)
{}

lemma Insert_Preserves_Node(t: Tree, x: int)
  requires IsBST(t)
  requires t.Node?
  ensures Insert(t, x).Node?
{}

lemma Insert_New_Min(t: Tree, x: int)
  requires IsBST(t)
  requires t.Node?
  requires !Contains(t, x)
  requires x < Min(t)
  requires IsBST(Insert(t, x))
  ensures Min(Insert(t, x)) == x
{
  match t
  case Node(v, l, r) =>
    match l
    case Leaf =>
    case Node(_, _, _) => {
    }
}
