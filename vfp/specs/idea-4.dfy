datatype Tree =
    | Empty
    | Node(val: nat, left: Tree, right: Tree)

// Checks whether a given tree is a binary search tree (BST).
function IsBST(tree: Tree): bool

// Inserts an element into a binary search tree while preserving the BST property.
function insert(tree: Tree, element: nat): Tree

// Checks whether a given tree contains a given element.
function Contains(tree: Tree, element: nat): bool

// Ensures that the tree resulting from inserting an element contains that element (without requiring nor ensuring the BST property).
lemma {:axiom} InsertContains(tree: Tree, element: nat)
ensures Contains(insert(tree, element), element)

// Checks the BST property continues to hold after insertion. This lemma should take bounds on the BST, and require that the element to be inserted is within those bounds.
lemma {:axiom} InsertPreservesBST(tree: Tree, element: nat, min: nat, max: nat)
requires IsBST(tree)
requires (min <= element && element <= max)
ensures IsBST(insert(tree, element))
