// Tree operations: size, height, inorder traversal

datatype BinaryTree<T> = Empty | Node(value: T, left: BinaryTree<T>, right: BinaryTree<T>)

function {:spec} treeSize<T>(t: BinaryTree<T>): nat
{
  match t
  case Empty => 0
  case Node(_, l, r) => 1 + treeSize(l) + treeSize(r)
}

function {:spec} treeHeight<T>(t: BinaryTree<T>): nat
{
  match t
  case Empty => 0
  case Node(_, l, r) =>
    var lh := treeHeight(l);
    var rh := treeHeight(r);
    1 + if lh > rh then lh else rh
}

function {:spec} inorder<T>(t: BinaryTree<T>): seq<T>
{
  match t
  case Empty => []
  case Node(v, l, r) => inorder(l) + [v] + inorder(r)
}

function {:spec} preorder<T>(t: BinaryTree<T>): seq<T>
{
  match t
  case Empty => []
  case Node(v, l, r) => [v] + preorder(l) + preorder(r)
}

function {:spec} postorder<T>(t: BinaryTree<T>): seq<T>
{
  match t
  case Empty => []
  case Node(v, l, r) => postorder(l) + postorder(r) + [v]
}

predicate {:spec} isLeaf<T>(t: BinaryTree<T>)
{
  t.Node? && t.left == Empty && t.right == Empty
}

function {:spec} leafCount<T>(t: BinaryTree<T>): nat
{
  match t
  case Empty => 0
  case Node(_, Empty, Empty) => 1
  case Node(_, l, r) => leafCount(l) + leafCount(r)
}

predicate {:spec} inTree<T(==)>(x: T, t: BinaryTree<T>)
{
  match t
  case Empty => false
  case Node(v, l, r) => v == x || inTree(x, l) || inTree(x, r)
}

function {:spec} mirror<T>(t: BinaryTree<T>): BinaryTree<T>
{
  match t
  case Empty => Empty
  case Node(v, l, r) => Node(v, mirror(r), mirror(l))
}

predicate {:spec} isBalanced<T>(t: BinaryTree<T>)
{
  match t
  case Empty => true
  case Node(_, l, r) =>
    isBalanced(l) && isBalanced(r) &&
    var diff := if treeHeight(l) > treeHeight(r)
                then treeHeight(l) - treeHeight(r)
                else treeHeight(r) - treeHeight(l);
    diff <= 1
}

lemma InorderLength<T>(t: BinaryTree<T>)
  ensures |inorder(t)| == treeSize(t)
{
  match t
  case Empty =>
  case Node(v, l, r) =>
    InorderLength(l);
    InorderLength(r);
    assert |inorder(t)| == |inorder(l)| + 1 + |inorder(r)|;
}

lemma PreorderLength<T>(t: BinaryTree<T>)
  ensures |preorder(t)| == treeSize(t)
{
  match t
  case Empty =>
  case Node(v, l, r) =>
    PreorderLength(l);
    PreorderLength(r);
}

lemma PostorderLength<T>(t: BinaryTree<T>)
  ensures |postorder(t)| == treeSize(t)
{
  match t
  case Empty =>
  case Node(v, l, r) =>
    PostorderLength(l);
    PostorderLength(r);
}

lemma MirrorTwice<T>(t: BinaryTree<T>)
  ensures mirror(mirror(t)) == t
{
  match t
  case Empty =>
  case Node(v, l, r) =>
    MirrorTwice(l);
    MirrorTwice(r);
}

lemma MirrorSize<T>(t: BinaryTree<T>)
  ensures treeSize(mirror(t)) == treeSize(t)
{
  match t
  case Empty =>
  case Node(v, l, r) =>
    MirrorSize(l);
    MirrorSize(r);
}

lemma MirrorHeight<T>(t: BinaryTree<T>)
  ensures treeHeight(mirror(t)) == treeHeight(t)
{
  match t
  case Empty =>
  case Node(v, l, r) =>
    MirrorHeight(l);
    MirrorHeight(r);
    var lh := treeHeight(l);
    var rh := treeHeight(r);
    var mlh := treeHeight(mirror(r));
    var mrh := treeHeight(mirror(l));
    assert mlh == rh && mrh == lh;
}

lemma LeafCountBound<T>(t: BinaryTree<T>)
  ensures leafCount(t) <= treeSize(t)
{
  match t
  case Empty =>
  case Node(_, l, r) =>
    if l == Empty && r == Empty {
      assert leafCount(t) == 1;
      assert treeSize(t) == 1;
    } else {
      LeafCountBound(l);
      LeafCountBound(r);
    }
}

lemma InTreeInorder<T>(x: T, t: BinaryTree<T>)
  ensures inTree(x, t) <==> x in inorder(t)
{
  match t
  case Empty =>
  case Node(v, l, r) =>
    InTreeInorder(x, l);
    InTreeInorder(x, r);
    if x == v {
      assert x in inorder(t);
    } else if inTree(x, l) {
      assert x in inorder(l);
      assert x in inorder(t);
    } else if inTree(x, r) {
      assert x in inorder(r);
      assert x in inorder(t);
    }
}

lemma HeightLogBound<T>(t: BinaryTree<T>)
  requires isBalanced(t) && t != Empty
  ensures treeHeight(t) <= treeSize(t)
{
  match t
  case Node(_, l, r) =>
    if l != Empty {
      HeightLogBound(l);
    }
    if r != Empty {
      HeightLogBound(r);
    }
}