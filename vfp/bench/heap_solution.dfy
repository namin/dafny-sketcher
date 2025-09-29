// Min-heap operations: insert, extractMin, heapify with heap property

datatype Heap = Heap(elements: seq<int>)

// Check if heap is empty
predicate {:spec} heapIsEmpty(h: Heap)
{
  |h.elements| == 0
}

// Get heap size
function {:spec} heapSize(h: Heap): nat
{
  |h.elements|
}

// Parent index in heap
function {:spec} parent(i: nat): nat
  requires i > 0
{
  (i - 1) / 2
}

// Left child index
function {:spec} leftChild(i: nat): nat
{
  2 * i + 1
}

// Right child index
function {:spec} rightChild(i: nat): nat
{
  2 * i + 2
}

// Check min-heap property
predicate {:spec} isMinHeap(h: Heap)
{
  forall i :: 0 < i < |h.elements| ==> h.elements[parent(i)] <= h.elements[i]
}

// Check max-heap property
predicate {:spec} isMaxHeap(h: Heap)
{
  forall i :: 0 < i < |h.elements| ==> h.elements[parent(i)] >= h.elements[i]
}

// Get minimum element (root of min-heap)
function {:spec} getMin(h: Heap): int
  requires !heapIsEmpty(h)
  requires isMinHeap(h)
{
  h.elements[0]
}

// Get maximum element (root of max-heap)
function {:spec} getMax(h: Heap): int
  requires !heapIsEmpty(h)
  requires isMaxHeap(h)
{
  h.elements[0]
}

// Check if element exists in heap
predicate {:spec} heapContains(h: Heap, x: int)
{
  x in h.elements
}

// Create empty heap
function {:spec} emptyHeap(): Heap
{
  Heap([])
}

// Create heap from single element
function {:spec} singletonHeap(x: int): Heap
{
  Heap([x])
}

// Swap two elements in sequence
function {:spec} swap(s: seq<int>, i: nat, j: nat): seq<int>
  requires i < |s| && j < |s|
{
  s[i := s[j]][j := s[i]]
}

// Check if heap is complete binary tree (always true for array representation)
predicate {:spec} isComplete(h: Heap)
{
  true  // Array representation is always complete
}

// Get height of heap
function {:spec} heapHeight(h: Heap): nat
{
  if |h.elements| == 0 then 0
  else log2Floor(|h.elements|) + 1
}

// Floor of log base 2
function {:spec} log2Floor(n: nat): nat
  requires n > 0
  decreases n
{
  if n == 1 then 0
  else 1 + log2Floor(n / 2)
}

// Check if index is valid
predicate {:spec} validIndex(h: Heap, i: nat)
{
  i < |h.elements|
}

// Get all elements at a given level
function {:spec} getLevel(h: Heap, level: nat): seq<int>
{
  getLevelHelper(h, level, 0)
}

function getLevelHelper(h: Heap, targetLevel: nat, currentLevel: nat): seq<int>
  decreases |h.elements| - currentLevel
{
  if currentLevel >= |h.elements| || currentLevel >= Power2(targetLevel) then []
  else if currentLevel >= Power2(targetLevel) - 1 && currentLevel < Power2(targetLevel + 1) - 1 then
    if currentLevel < |h.elements| then [h.elements[currentLevel]] + getLevelHelper(h, targetLevel, currentLevel + 1)
    else []
  else getLevelHelper(h, targetLevel, currentLevel + 1)
}

function Power2(n: nat): nat
{
  if n == 0 then 1
  else 2 * Power2(n - 1)
}

// --- Lemmas for correctness ---

lemma EmptyHeapIsMinHeap()
  ensures isMinHeap(emptyHeap())
{
  var h := emptyHeap();
  forall i | 0 < i < |h.elements|
    ensures h.elements[parent(i)] <= h.elements[i]
  {
    assert false;  // No such i exists
  }
}

lemma EmptyHeapIsMaxHeap()
  ensures isMaxHeap(emptyHeap())
{
  var h := emptyHeap();
  forall i | 0 < i < |h.elements|
    ensures h.elements[parent(i)] >= h.elements[i]
  {
    assert false;  // No such i exists
  }
}

lemma SingletonIsMinHeap(x: int)
  ensures isMinHeap(singletonHeap(x))
{
  var h := singletonHeap(x);
  forall i | 0 < i < |h.elements|
    ensures h.elements[parent(i)] <= h.elements[i]
  {
    assert false;  // No such i exists since |h.elements| == 1
  }
}

lemma SingletonIsMaxHeap(x: int)
  ensures isMaxHeap(singletonHeap(x))
{
  var h := singletonHeap(x);
  forall i | 0 < i < |h.elements|
    ensures h.elements[parent(i)] >= h.elements[i]
  {
    assert false;  // No such i exists since |h.elements| == 1
  }
}

lemma MinHeapRootIsMinimum(h: Heap)
  requires !heapIsEmpty(h)
  requires isMinHeap(h)
  ensures forall i :: 0 <= i < |h.elements| ==> h.elements[0] <= h.elements[i]
{
  if |h.elements| == 1 {
    forall i | 0 <= i < |h.elements|
      ensures h.elements[0] <= h.elements[i]
    {
      assert i == 0;
    }
  } else {
    forall i | 0 <= i < |h.elements|
      ensures h.elements[0] <= h.elements[i]
    {
      if i == 0 {
        // Trivial
      } else {
        MinHeapPathToRoot(h, i);
      }
    }
  }
}

lemma MinHeapPathToRoot(h: Heap, i: nat)
  requires isMinHeap(h)
  requires 0 < i < |h.elements|
  ensures h.elements[0] <= h.elements[i]
{
  if parent(i) == 0 {
    assert h.elements[0] <= h.elements[i];
  } else {
    assert h.elements[parent(i)] <= h.elements[i];
    MinHeapPathToRoot(h, parent(i));
  }
}

lemma MaxHeapRootIsMaximum(h: Heap)
  requires !heapIsEmpty(h)
  requires isMaxHeap(h)
  ensures forall i :: 0 <= i < |h.elements| ==> h.elements[0] >= h.elements[i]
{
  if |h.elements| == 1 {
    forall i | 0 <= i < |h.elements|
      ensures h.elements[0] >= h.elements[i]
    {
      assert i == 0;
    }
  } else {
    forall i | 0 <= i < |h.elements|
      ensures h.elements[0] >= h.elements[i]
    {
      if i == 0 {
        // Trivial
      } else {
        MaxHeapPathToRoot(h, i);
      }
    }
  }
}

lemma MaxHeapPathToRoot(h: Heap, i: nat)
  requires isMaxHeap(h)
  requires 0 < i < |h.elements|
  ensures h.elements[0] >= h.elements[i]
{
  if parent(i) == 0 {
    assert h.elements[0] >= h.elements[i];
  } else {
    assert h.elements[parent(i)] >= h.elements[i];
    MaxHeapPathToRoot(h, parent(i));
  }
}

lemma ParentChildRelation(i: nat)
  requires i > 0
  ensures leftChild(parent(i)) == i || rightChild(parent(i)) == i
  ensures leftChild(parent(i)) == i <==> i % 2 == 1
  ensures rightChild(parent(i)) == i <==> i % 2 == 0
{
  var p := parent(i);
  assert p == (i - 1) / 2;
  assert leftChild(p) == 2 * p + 1;
  assert rightChild(p) == 2 * p + 2;

  if i % 2 == 1 {
    assert i == 2 * ((i - 1) / 2) + 1;
    assert leftChild(p) == i;
  } else {
    assert i % 2 == 0;
    assert i == 2 * ((i - 1) / 2) + 2;
    assert rightChild(p) == i;
  }
}

lemma HeapHeightBound(h: Heap)
  ensures heapHeight(h) <= |h.elements|
{
  if |h.elements| == 0 {
    assert heapHeight(h) == 0;
  } else {
    Log2FloorBound(|h.elements|);
  }
}

lemma Log2FloorBound(n: nat)
  requires n > 0
  ensures log2Floor(n) < n
  decreases n
{
  if n == 1 {
    assert log2Floor(1) == 0;
  } else {
    Log2FloorBound(n / 2);
    assert log2Floor(n) == 1 + log2Floor(n / 2);
    assert n / 2 < n;
  }
}

lemma SwapPreservesMultiset(s: seq<int>, i: nat, j: nat)
  requires i < |s| && j < |s|
  ensures multiset(swap(s, i, j)) == multiset(s)
{
  var s' := swap(s, i, j);
  assert s'[i] == s[j];
  assert s'[j] == s[i];
  forall k | 0 <= k < |s| && k != i && k != j
    ensures s'[k] == s[k]
  {
    // Elements other than i and j are unchanged
  }
}