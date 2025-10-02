## patterns in lemmas to investigate

### single helper call

- `binarySearchCorrect`
- `ReverseLength`
- `GcdDividesBoth`
- `QueueSizeProperty`

### inductive sketch on track

- helper call rather than recursive call
  - `Insert_Preserves_BST`: two branches need complex `forall` arguments with helper calls rather than recursive calls
  - `Insert_New_Min`: one branch doesn't need to be expanded and calls helper lemma rather than recursive call

- assertions needed
  - `dedupCorrect`
  - `maxIsCorrect`
  - `DequeueCorrect`

- helper call needed
  - `flattenCorrect`
  - `HeapHeightBound`
  - `reverseAppend`
  - `ReverseAppend`
  - `reverse_involutes`

- missing both assertions and helper calls
  - `sumDistributive`
  - `reverseReverse`
  - `ReverseReverse`
  - `reverse_append`

### inductive sketch is wrong

- `toMultisetAppend`: wrong term inducted on? plus asserts
- `sumAppend`: use wrong argument but following function

### inductive sketch doesn't go deep enough into the structure

- `MinHeapRootIsMinimum`
- `MinHeapPathToRoot`
- `MaxHeapRootIsMaximum`
- `StackInduction`

### sketch is not useful

- `makePalindromeCorrect`
- `SimpleQueueEquivalence`
- `RevAcc_Helper`

### time out

- `CompleteInduction`

## bugs

- `binarySearchCorrect` has a sketch promising induction on `sorted` function, but delivers nothing but the comment

### missing inductive sketch, not even comment

- `SelfReachable`
- `DirectEdgeReachable`
- `EmptyGraphAcyclic`
- `SingleNodeAcyclic`
- `encodeDecodeRoundTrip`
