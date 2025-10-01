# lemmas to investigate
## lemma `binarySearchCorrect`
### working solution
```dafny
{
  binarySearchHelperCorrect(s, key, 0, |s|);
}
```
### failed inductive sketch
```dafny
    // Inductive proof using rule induction
    // following function: sorted


```
#### errors
* a postcondition could not be proved on this return path -- `{`
## lemma `Insert_Preserves_BST`
### working solution
```dafny
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
```
### failed inductive sketch
```dafny
    // Inductive proof using rule induction
    // following function: Insert
    match t {
        case Leaf => {
        }
        case Node(v, l, r) => {
            if (x == v) {
            } else if (x < v) {
                Insert_Preserves_BST(l, x);
            } else {
                Insert_Preserves_BST(r, x);
            }
        }
    }


```
#### errors
* a postcondition could not be proved on this return path -- `} else if (x < v) {`
* a postcondition could not be proved on this return path -- `} else {`
## lemma `Insert_New_Min`
### working solution
```dafny
{
  match t
  case Node(v, l, r) =>
    match l
    case Leaf =>
    case Node(_, _, _) =>
      Min_Absolute(l);
}
```
### failed inductive sketch
```dafny
    // Inductive proof using rule induction
    // following function: Contains
    match t {
        case Leaf => {
        }
        case Node(v, l, r) => {
            if (x == v) {
            } else if (x < v) {
                Insert_New_Min(l, x);
            } else {
                Insert_New_Min(r, x);
            }
        }
    }


```
#### errors
* a precondition for this call could not be proved -- `Insert_New_Min(l, x);`
* a postcondition could not be proved on this return path -- `} else {`
* a precondition for this call could not be proved -- `Insert_New_Min(r, x);`
## lemma `dedupCorrect`
### working solution
```dafny
{
  if |xs| == 0 {
  } else {
    dedupCorrect(xs[1..]);
    var rest := dedup(xs[1..]);
    
    if xs[0] in rest {
      assert dedup(xs) == rest;
      assert xs[0] in rest;
      assert toSet(rest) == toSet(xs[1..]);
      assert xs[0] in xs[1..];
      assert toSet(xs) == toSet(xs[1..]) + {xs[0]};
      assert toSet(xs) == toSet(xs[1..]);
    } else {
      assert dedup(xs) == [xs[0]] + rest;
      assert noDuplicates(rest);
      assert !(xs[0] in rest);
      
      forall i, j | 0 <= i < j < |dedup(xs)|
        ensures dedup(xs)[i] != dedup(xs)[j]
      {
        if i == 0 {
          assert dedup(xs)[0] == xs[0];
          assert dedup(xs)[j] == rest[j-1];
          assert !(xs[0] in rest);
        } else {
          assert dedup(xs)[i] == rest[i-1];
          assert dedup(xs)[j] == rest[j-1];
        }
      }
      
      assert toSet(dedup(xs)) == toSet([xs[0]] + rest);
      assert toSet([xs[0]] + rest) == {xs[0]} + toSet(rest);
      assert toSet(rest) == toSet(xs[1..]);
      assert toSet(xs) == {xs[0]} + toSet(xs[1..]);
    }
  }
}
```
### failed inductive sketch
```dafny
    // Inductive proof using rule induction
    // following function: dedup
    if (|xs| == 0) {
    } else if (xs[0] in dedup(xs[1..])) {
        dedupCorrect(xs[1..]);
    } else {
        dedupCorrect(xs[1..]);
    }


```
#### errors
* a postcondition could not be proved on this return path -- `} else {`
## lemma `toMultisetAppend`
### working solution
```dafny
{
  if |s1| == 0 {
    assert s1 + s2 == s2;
  } else {
    toMultisetAppend(s1[1..], s2);
    assert s1 + s2 == [s1[0]] + (s1[1..] + s2);
  }
}
```
### failed inductive sketch
```dafny
    // Inductive proof using rule induction
    // following function: toMultiset
    if (|s2| == 0) {
    } else {
        toMultisetAppend(s1, s2[1..]);
    }


```
#### errors
* a postcondition could not be proved on this return path -- `} else {`
## lemma `flattenCorrect`
### working solution
```dafny
{
  match t
  case Leaf(v) =>
  case Node(l, r) =>
    flattenCorrect(l);
    flattenCorrect(r);
    toMultisetAppend(flatten(l), flatten(r));
}
```
### failed inductive sketch
```dafny
    // Inductive proof using rule induction
    // following function: size
    match t {
        case Leaf(_) => {
        }
        case Node(l, r) => {
            flattenCorrect(l);
            flattenCorrect(r);
        }
    }


```
#### errors
* a postcondition could not be proved on this return path -- `case Node(l, r) => {`
## lemma `SelfReachable`
### working solution
```dafny
{
  var path := [n];
  assert |path| == 1;
  assert |path| >= 1;
  assert path[0] == n;
  assert path[|path| - 1] == n;

  // Show isPath
  forall i | 0 <= i < |path|
    ensures path[i] in g.nodes
  {
    assert path[i] == n;
  }

  forall i | 0 <= i < |path| - 1
    ensures hasEdge(g, path[i], path[i+1])
  {
    assert false;  // No such i exists since |path| == 1
  }

  assert isPath(g, path);
}
```
### failed inductive sketch
```dafny


```
#### errors
* a postcondition could not be proved on this return path -- `{`
## lemma `DirectEdgeReachable`
### working solution
```dafny
{
  assert b in neighbors(g, a);
  if a == b {
    SelfReachable(g, a);
  } else {
    var path := [a, b];
    assert |path| == 2;
    assert |path| >= 1;
    assert path[0] == a;
    assert path[|path| - 1] == b;

    // Show isPath
    forall i | 0 <= i < |path|
      ensures path[i] in g.nodes
    {
      if i == 0 { assert path[i] == a; }
      else { assert path[i] == b; }
    }

    forall i | 0 <= i < |path| - 1
      ensures hasEdge(g, path[i], path[i+1])
    {
      assert i == 0;
      assert path[i] == a && path[i+1] == b;
    }

    assert isPath(g, path);
  }
}
```
### failed inductive sketch
```dafny


```
#### errors
* a postcondition could not be proved on this return path -- `{`
## lemma `EmptyGraphAcyclic`
### working solution
```dafny
{
  if hasCycle(g) {
    var path :| isPath(g, path) && |path| > 1 && path[0] == path[|path| - 1];
    assert |path| >= 2;
    assert hasEdge(g, path[0], path[1]);
    assert (path[0], path[1]) in g.edges;
    assert false;
  }
}
```
### failed inductive sketch
```dafny


```
#### errors
* a postcondition could not be proved on this return path -- `{`
## lemma `SingleNodeAcyclic`
### working solution
```dafny
{
  EmptyGraphAcyclic(g);
}
```
### failed inductive sketch
```dafny


```
#### errors
* a postcondition could not be proved on this return path -- `{`
## lemma `MinHeapRootIsMinimum`
### working solution
```dafny
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
```
### failed inductive sketch
```dafny
    // Structural induction on h
    match h {
        case Heap(elements) => {
        }
    }


```
#### errors
* a postcondition could not be proved on this return path -- `case Heap(elements) => {`
## lemma `MinHeapPathToRoot`
### working solution
```dafny
{
  if parent(i) == 0 {
    assert h.elements[0] <= h.elements[i];
  } else {
    assert h.elements[parent(i)] <= h.elements[i];
    MinHeapPathToRoot(h, parent(i));
  }
}
```
### failed inductive sketch
```dafny
    // Structural induction on h
    match h {
        case Heap(elements) => {
        }
    }


```
#### errors
* a postcondition could not be proved on this return path -- `case Heap(elements) => {`
## lemma `MaxHeapRootIsMaximum`
### working solution
```dafny
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
```
### failed inductive sketch
```dafny
    // Structural induction on h
    match h {
        case Heap(elements) => {
        }
    }


```
#### errors
* a postcondition could not be proved on this return path -- `case Heap(elements) => {`
## lemma `MaxHeapPathToRoot`
### working solution
```dafny
{
  if parent(i) == 0 {
    assert h.elements[0] >= h.elements[i];
  } else {
    assert h.elements[parent(i)] >= h.elements[i];
    MaxHeapPathToRoot(h, parent(i));
  }
}
```
### failed inductive sketch
```dafny
    // Structural induction on h
    match h {
        case Heap(elements) => {
        }
    }


```
#### errors
* a postcondition could not be proved on this return path -- `case Heap(elements) => {`
## lemma `HeapHeightBound`
### working solution
```dafny
{
  if |h.elements| == 0 {
    assert heapHeight(h) == 0;
  } else {
    Log2FloorBound(|h.elements|);
  }
}
```
### failed inductive sketch
```dafny
    // Inductive proof using rule induction
    // following function: heapHeight
    if (|h.elements| == 0) {
    } else {
    }


```
#### errors
* a postcondition could not be proved on this return path -- `} else {`
## lemma `CompleteInduction`
### working solution
```dafny
{
  if n == 0 {
    // Base case
    assert P(0);
  } else {
    // Need to show all j < n satisfy P(j)
    forall j: nat | j < n
      ensures P(j)
    {
      if j == 0 {
        assert P(0);
      } else {
        CompleteInduction(j, P);
      }
    }

    // Now apply the inductive hypothesis
    assert forall j: nat :: j < n ==> P(j);
    assert P(n);
  }
}
```
### failed inductive sketch
```dafny
Error: Dafny Sketcher timed out
```
#### errors
* invalid statement beginning here (is a 'label' keyword missing? or a 'const' or 'var' keyword?) -- `Error: Dafny Sketcher timed out`
* missing semicolon at end of statement -- `Error: Dafny Sketcher timed out`
* missing semicolon at end of statement -- `Error: Dafny Sketcher timed out`
* missing semicolon at end of statement -- `Error: Dafny Sketcher timed out`
* missing semicolon at end of statement -- `Error: Dafny Sketcher timed out`
## lemma `ReverseLength`
### working solution
```dafny
{
  ReverseHelperLength(list, Nil);
}
```
### failed inductive sketch
```dafny
    // Inductive proof using rule induction
    // following function: length
    match list {
        case Nil => {
        }
        case Cons(_, tail) => {
            ReverseLength(tail);
        }
    }


```
#### errors
* a postcondition could not be proved on this return path -- `case Cons(_, tail) => {`
## lemma `ReverseReverse`
### working solution
```dafny
{
  ReverseReverseHelper(list, Nil);
}
```
### failed inductive sketch
```dafny
    // Inductive proof using rule induction
    // following function: reverse
    ReverseReverse(list);


```
#### errors
* cannot prove termination; try supplying a decreases clause -- `ReverseReverse(list);`
## lemma `sumCorrect`
### working solution
```dafny
{
  sumCorrectHelper(xs, 0);
}
```
### failed inductive sketch
```dafny
    // Inductive proof using rule induction
    // following function: sumTail
    if (|xs| == 0) {
    } else {
        sumCorrect(xs[1..]);
    }


```
#### errors
* a postcondition could not be proved on this return path -- `} else {`
## lemma `sumAppend`
### working solution
```dafny
{
  if |xs| == 0 {
    assert xs + ys == ys;
  } else {
    assert xs + ys == [xs[0]] + (xs[1..] + ys);
    calc {
      sum(xs + ys);
      == xs[0] + sum((xs[1..] + ys));
      == { sumAppend(xs[1..], ys); }
      xs[0] + (sum(xs[1..]) + sum(ys));
      == (xs[0] + sum(xs[1..])) + sum(ys);
      == sum(xs) + sum(ys);
    }
  }
}
```
### failed inductive sketch
```dafny
    // Inductive proof using rule induction
    // following function: sum
    if (|ys| == 0) {
    } else {
        sumAppend(xs, ys[1..]);
    }


```
#### errors
* a postcondition could not be proved on this return path -- `} else {`
## lemma `sumDistributive`
### working solution
```dafny
{
  if |xs| == 0 {
    // Base case: empty sequence
    assert seq(|xs|, i requires 0 <= i < |xs| => c * xs[i]) == [];
    assert sum([]) == 0;
    assert c * sum([]) == c * 0 == 0;
  } else {
    // Inductive case: non-empty sequence
    var scaled_xs := seq(|xs|, i requires 0 <= i < |xs| => c * xs[i]);
    assert scaled_xs == [c * xs[0]] + seq(|xs[1..]|, i requires 0 <= i < |xs[1..]| => c * xs[1..][i]);
    
    calc {
      sum(scaled_xs);
      == sum([c * xs[0]] + seq(|xs[1..]|, i requires 0 <= i < |xs[1..]| => c * xs[1..][i]));
      == { sumAppend([c * xs[0]], seq(|xs[1..]|, i requires 0 <= i < |xs[1..]| => c * xs[1..][i])); }
      sum([c * xs[0]]) + sum(seq(|xs[1..]|, i requires 0 <= i < |xs[1..]| => c * xs[1..][i]));
      == c * xs[0] + sum(seq(|xs[1..]|, i requires 0 <= i < |xs[1..]| => c * xs[1..][i]));
      == { sumDistributive(xs[1..], c); }
      c * xs[0] + c * sum(xs[1..]);
      == c * (xs[0] + sum(xs[1..]));
      == c * sum(xs);
    }
  }
}
```
### failed inductive sketch
```dafny
    // Inductive proof using rule induction
    // following function: sum
    if (|xs| == 0) {
    } else {
        sumDistributive(xs[1..], c);
    }


```
#### errors
* a postcondition could not be proved on this return path -- `} else {`
## lemma `GcdDividesBoth`
### working solution
```dafny
{
  GcdPositive(a, b);
}
```
### failed inductive sketch
```dafny
    // Inductive proof using rule induction
    // following function: gcd
    if (b == 0) {
    } else {
        GcdDividesBoth(b, a % b);
    }


```
#### errors
* cannot prove termination; try supplying a decreases clause -- `GcdDividesBoth(b, a % b);`
* a precondition for this call could not be proved -- `GcdDividesBoth(b, a % b);`
## lemma `maxIsCorrect`
### working solution
```dafny
{
  if |s| == 1 {
    // Base case is trivial
  } else {
    var restMax := max(s[1..]);
    maxIsCorrect(s[1..]);
    // We know isMax(s[1..], restMax)
    // So restMax in s[1..] and forall x in s[1..] :: x <= restMax
    
    if s[0] >= restMax {
      // max returns s[0]
      // Need to show: s[0] in s (trivial) and forall x in s :: x <= s[0]
      forall x | x in s
        ensures x <= s[0]
      {
        if x == s[0] {
          // x <= s[0] trivially
        } else {
          // x must be in s[1..]
          assert x in s[1..];
          // From induction hypothesis: x <= restMax
          // We know s[0] >= restMax
          // Therefore x <= s[0]
        }
      }
    } else {
      // max returns restMax
      // Need to show: restMax in s and forall x in s :: x <= restMax
      assert restMax in s[1..];
      assert restMax in s;
      
      forall x | x in s
        ensures x <= restMax
      {
        if x == s[0] {
          // We know s[0] < restMax
        } else {
          // x must be in s[1..]
          assert x in s[1..];
          // From induction hypothesis: x <= restMax
        }
      }
    }
  }
}
```
### failed inductive sketch
```dafny
    // Inductive proof using rule induction
    // following function: max
    if (|s| == 1) {
    } else {
        var restMax := max(s[1..]);
        maxIsCorrect(s[1..]);
        if (s[0] >= restMax) {
        } else {
        }
    }


```
#### errors
* a postcondition could not be proved on this return path -- `if (s[0] >= restMax) {`
## lemma `reverseAppend`
### working solution
```dafny
{
  match xs
  case Nil => 
    assert reverse(append(Nil, ys)) == reverse(ys);
    appendNilRight(reverse(ys));
  case Cons(h, t) =>
    reverseAppend(t, ys);
    appendAssoc(reverse(ys), reverse(t), Cons(h, Nil));
}
```
### failed inductive sketch
```dafny
    // Inductive proof using rule induction
    // following function: reverse
    match xs {
        case Nil => {
        }
        case Cons(h, t) => {
            reverseAppend(t, ys);
        }
    }


```
#### errors
* a postcondition could not be proved on this return path -- `case Cons(h, t) => {`
## lemma `reverseReverse`
### working solution
```dafny
{
  match xs
  case Nil =>
  case Cons(h, t) =>
    reverseReverse(t);
    reverseAppend(reverse(t), Cons(h, Nil));
    assert reverse(Cons(h, Nil)) == Cons(h, Nil);
}
```
### failed inductive sketch
```dafny
    // Inductive proof using rule induction
    // following function: reverse
    match xs {
        case Nil => {
        }
        case Cons(h, t) => {
            reverseReverse(t);
        }
    }


```
#### errors
* a postcondition could not be proved on this return path -- `case Cons(h, t) => {`
## lemma `makePalindromeCorrect`
### working solution
```dafny
{
  calc == {
    reverse(makePalindrome(xs));
    reverse(append(xs, reverse(xs)));
    { reverseAppend(xs, reverse(xs)); }
    append(reverse(reverse(xs)), reverse(xs));
    { reverseReverse(xs); }
    append(xs, reverse(xs));
    makePalindrome(xs);
  }
}
```
### failed inductive sketch
```dafny
    // Structural induction on xs
    match xs {
        case Nil() => {
        }
        case Cons(head, tail) => {
            makePalindromeCorrect(tail);
        }
    }


```
#### errors
* a postcondition could not be proved on this return path -- `case Cons(head, tail) => {`
## lemma `ReverseReverse`
### working solution
```dafny
{
  if |s| == 0 {
    // Base case
  } else {
    ReverseReverse(s[1..]);
    ReverseAppend(reverse(s[1..]), [s[0]]);
    assert reverse(reverse(s)) == s;
  }
}
```
### failed inductive sketch
```dafny
    // Inductive proof using rule induction
    // following function: reverse
    if (|s| == 0) {
    } else {
        ReverseReverse(s[1..]);
    }


```
#### errors
* a postcondition could not be proved on this return path -- `} else {`
## lemma `ReverseAppend`
### working solution
```dafny
{
  if |s1| == 0 {
    assert s1 + s2 == s2;
    assert reverse(s1) == [];
  } else {
    assert s1 + s2 == [s1[0]] + (s1[1..] + s2);
    ReverseAppend(s1[1..], s2);
  }
}
```
### failed inductive sketch
```dafny
    // Inductive proof using rule induction
    // following function: reverse
    if (|s1| == 0) {
    } else {
        ReverseAppend(s1[1..], s2);
    }


```
#### errors
* a postcondition could not be proved on this return path -- `} else {`
## lemma `QueueSizeProperty`
### working solution
```dafny
{
  ReverseLength(q.rear);
}
```
### failed inductive sketch
```dafny
    // Structural induction on q
    match q {
        case Queue(front, rear) => {
        }
    }


```
#### errors
* a postcondition could not be proved on this return path -- `case Queue(front, rear) => {`
## lemma `DequeueCorrect`
### working solution
```dafny
{
  if |q.front| > 0 {
    assert queueToSeq(q) == q.front + reverse(q.rear);
    assert queueToSeq(dequeue(q)) == q.front[1..] + reverse(q.rear);
    assert queueFront(q) == q.front[0];
  } else {
    assert q.front == [];
    assert |q.rear| > 0;
    var rev := reverse(q.rear);
    ReverseLength(q.rear);
    assert |rev| == |q.rear|;
    assert queueToSeq(q) == rev;
    assert queueFront(q) == q.rear[|q.rear| - 1];

    ReverseFirst(q.rear);
    assert rev[0] == q.rear[|q.rear| - 1];

    if |q.rear| == 1 {
      assert rev == [q.rear[0]];
      assert queueToSeq(q) == [q.rear[0]];
      assert queueFront(q) == q.rear[0];
      assert queueToSeq(q)[0] == q.rear[0];
    } else {
      assert |rev| > 1;
      assert queueToSeq(dequeue(q)) == rev[1..];
      assert queueFront(q) == rev[0];
    }
  }
}
```
### failed inductive sketch
```dafny
    // Inductive proof using rule induction
    // following function: dequeue
    if (|q.front| > 0) {
    } else if (|q.rear| == 1) {
    } else {
    }


```
#### errors
* a postcondition could not be proved on this return path -- `} else if (|q.rear| == 1) {`
* a postcondition could not be proved on this return path -- `} else {`
## lemma `SimpleQueueEquivalence`
### working solution
```dafny
{
  if queueIsEmpty(q) {
    assert q.front == [] && q.rear == [];
    assert queueToSeq(q) == [];
    assert sq.elements == [];
  }
  QueueSizeProperty(q);
}
```
### failed inductive sketch
```dafny
    // Structural induction on sq
    match sq {
        case SimpleQueue(elements) => {
        }
    }


```
#### errors
* a postcondition could not be proved on this return path -- `case SimpleQueue(elements) => {`
## lemma `reverse_append`
### working solution
```dafny
{
  if |s1| == 0 {
    assert s1 + s2 == s2;
    assert reverse(s1) == [];
    assert reverse(s2) + [] == reverse(s2);
  } else {
    assert s1 == [s1[0]] + s1[1..];
    assert s1 + s2 == ([s1[0]] + s1[1..]) + s2 == [s1[0]] + (s1[1..] + s2);
    
    calc {
      reverse(s1 + s2);
      == reverse([s1[0]] + (s1[1..] + s2));
      == reverse((s1[1..] + s2)) + [s1[0]];
      == { reverse_append(s1[1..], s2); }
      (reverse(s2) + reverse(s1[1..])) + [s1[0]];
      == { assert (reverse(s2) + reverse(s1[1..])) + [s1[0]] == 
           reverse(s2) + (reverse(s1[1..]) + [s1[0]]); }
      reverse(s2) + (reverse(s1[1..]) + [s1[0]]);
      == reverse(s2) + reverse(s1);
    }
  }
}
```
### failed inductive sketch
```dafny
    // Inductive proof using rule induction
    // following function: reverse
    if (|s1| == 0) {
    } else {
        reverse_append(s1[1..], s2);
    }


```
#### errors
* a postcondition could not be proved on this return path -- `} else {`
## lemma `reverse_involutes`
### working solution
```dafny
{
  if |l| == 0 {
  } else {
    calc {
      reverse(reverse(l));
      == reverse(reverse(l[1..]) + [l[0]]);
      == { reverse_append(reverse(l[1..]), [l[0]]); }
      reverse([l[0]]) + reverse(reverse(l[1..]));
      == [l[0]] + reverse(reverse(l[1..]));
      == { reverse_involutes(l[1..]); }
      [l[0]] + l[1..];
      == l;
    }
  }
}
```
### failed inductive sketch
```dafny
    // Inductive proof using rule induction
    // following function: reverse
    if (|l| == 0) {
    } else {
        reverse_involutes(l[1..]);
    }


```
#### errors
* a postcondition could not be proved on this return path -- `} else {`
## lemma `encodeDecodeRoundTrip`
### working solution
```dafny
{
  if |s| == 0 {
    // Base case: empty sequence
  } else if |s| == 1 {
    // Base case: single character
    assert decode([RLE(1, s[0])]) == repeatChar(1, s[0]) == [s[0]] == s;
  } else {
    var rest := encode(s[1..]);
    encodeDecodeRoundTrip(s[1..]); // Induction hypothesis
    assert decode(rest) == s[1..];
    
    if |rest| > 0 && rest[0].ch == s[0] {
      // Case: merging with first element of rest
      var merged := [RLE(rest[0].count + 1, s[0])] + rest[1..];
      assert decode(merged) == repeatChar(rest[0].count + 1, s[0]) + decode(rest[1..]);
      assert repeatChar(rest[0].count + 1, s[0]) == [s[0]] + repeatChar(rest[0].count, s[0]);
      assert decode(rest) == repeatChar(rest[0].count, rest[0].ch) + decode(rest[1..]);
      assert s[0] == rest[0].ch;
      assert decode(merged) == [s[0]] + decode(rest) == [s[0]] + s[1..] == s;
    } else {
      // Case: not merging
      var result := [RLE(1, s[0])] + rest;
      assert decode(result) == repeatChar(1, s[0]) + decode(rest);
      assert repeatChar(1, s[0]) == [s[0]];
      assert decode(result) == [s[0]] + s[1..] == s;
    }
  }
}
```
### failed inductive sketch
```dafny


```
#### errors
* a postcondition could not be proved on this return path -- `{`
## lemma `RevAcc_Helper`
### working solution
```dafny
{
  match xs {
    case Nil => 
      assert revAcc(Nil, acc) == acc;
      assert revAcc(Nil, Nil) == Nil;
      assert app(Nil, acc) == acc;
    case Cons(x, xs') => 
      RevAcc_Helper(xs', Cons(x, acc));
      RevAcc_Helper(xs', Cons(x, Nil));
      AppendAssoc(revAcc(xs', Nil), Cons(x, Nil), acc);
  }
}
```
### failed inductive sketch
```dafny
    // Inductive proof using rule induction
    // following function: revAcc
    match xs {
        case Nil => {
        }
        case Cons(x, xs') => {
            RevAcc_Helper(xs', acc);
        }
    }


```
#### errors
* a postcondition could not be proved on this return path -- `case Cons(x, xs') => {`
## lemma `RevAcc_Correct`
### working solution
```dafny
{
  RevAcc_Helper(xs, acc);
}
```
### failed inductive sketch
```dafny
    // Inductive proof using rule induction
    // following function: revAcc
    match xs {
        case Nil => {
        }
        case Cons(x, xs') => {
            RevAcc_Correct(xs', acc);
        }
    }


```
#### errors
* a postcondition could not be proved on this return path -- `case Cons(x, xs') => {`
## lemma `StackInduction`
### working solution
```dafny
{
  if isEmpty(s) {
    assert s == emptyStack();
  } else {
    var s' := pop(s);
    var x := peek(s);
    assert s == push(s', x);
  }
}
```
### failed inductive sketch
```dafny
    // Structural induction on s
    match s {
        case Stack(elements) => {
        }
    }


```
#### errors
* a postcondition could not be proved on this return path -- `case Stack(elements) => {`
## summary
### empty proofs
120: `binarySearchHelperCorrect`, `Contains_Correct`, `Min_Absolute`, `Insert_Preserves_Node`, `iter5_biz_day_idempotent`, `OptimizePreservesSemantics`, `FacPositive`, `factorialCorrect`, `factorialPositive`, `factorialIncreasing`, `fibCorrect`, `fibIncreasing`, `ok3_pizza`, `PathOfLengthTwo`, `TreeNoCycle`, `ValidGraphSubgraph`, `EmptyHeapIsMinHeap`, `EmptyHeapIsMaxHeap`, `SingletonIsMinHeap`, `SingletonIsMaxHeap`, `ParentChildRelation`, `Log2FloorBound`, `SwapPreservesMultiset`, `SumToFormula`, `SumOddsIsSquare`, `SumSquaresFormula`, `PowerOfTwo`, `PowerMonotonic`, `PowerPositive`, `FibonacciInequality`, `StrongInduction`, `isSortedCorrect`, `isSortedTransitive`, `isSortedSubsequence`, `LengthAppend`, `AppendNil`, `AppendAssociative`, `ReverseHelperLength`, `ReverseReverseHelper`, `ToSeqFromSeq`, `FromSeqToSeq`, `MapLength`, `FilterSubset`, `TakeDropConcat`, `RemoveDecreasesLength`, `InsertAtLength`, `AppendAssociative`, `AppendNeutral`, `AppendLength`, `NthAppend`, `IndexOfCorrect`, `TakeDropConcat`, `FilterSubset`, `MapLength`, `MapCompose`, `sumCorrectHelper`, `GcdZero`, `GcdPositive`, `PrimeHasOnlyTwoDivisors`, `TwoPrime`, `ThreePrime`, `PowerSquare`, `SumFormula`, `FactorialPositive`, `FibonacciMonotonic`, `BinomialSymmetry`, `appendNilRight`, `appendAssoc`, `partitionCorrect`, `powerCorrect`, `powerZero`, `powerOne`, `ReverseLength`, `ReverseFirst`, `SeqAssoc`, `EnqueueCorrect`, `repeat_correct`, `reverse_permutes`, `encodeProducesValidRLE`, `UnionCommutative`, `UnionAssociative`, `UnionIdentity`, `IntersectionCommutative`, `IntersectionAssociative`, `IntersectionDistributive`, `UnionDistributive`, `DifferenceProperties`, `SubsetTransitive`, `SubsetAntisymmetric`, `PowersetEmpty`, `PowersetSubsetProperty`, `PowerProduct`, `DeMorgan`, `InsertPreservesSortedBetween`, `AppendAssoc`, `PushPopIdentity`, `PopPushNotIdentity`, `PushIncreaseSize`, `PopDecreaseSize`, `EmptyStackProperties`, `LIFOProperty`, `PushAllCorrect`, `PopNCorrect`, `PushPreservesContains`, `StackToFromSeq`, `PushOrder`, `NthFromTopCorrect`, `sumToCorrect`, `sumToFormula`, `sumToIncreasing`, `check_activation`, `InorderLength`, `PreorderLength`, `PostorderLength`, `MirrorTwice`, `MirrorSize`, `MirrorHeight`, `LeafCountBound`, `InTreeInorder`, `HeightLogBound`
### induction proofs
7: `Insert_InTree_Subset`, `OptimizerOptimal`, `fibPairCorrect`, `NthCorrect`, `PowerAddition`, `optimizeOptimal`, `powerAdd`
### other proofs
37: `binarySearchCorrect`, `Insert_Preserves_BST`, `Insert_New_Min`, `dedupCorrect`, `toMultisetAppend`, `flattenCorrect`, `SelfReachable`, `DirectEdgeReachable`, `EmptyGraphAcyclic`, `SingleNodeAcyclic`, `MinHeapRootIsMinimum`, `MinHeapPathToRoot`, `MaxHeapRootIsMaximum`, `MaxHeapPathToRoot`, `HeapHeightBound`, `CompleteInduction`, `ReverseLength`, `ReverseReverse`, `sumCorrect`, `sumAppend`, `sumDistributive`, `GcdDividesBoth`, `maxIsCorrect`, `reverseAppend`, `reverseReverse`, `makePalindromeCorrect`, `ReverseReverse`, `ReverseAppend`, `QueueSizeProperty`, `DequeueCorrect`, `SimpleQueueEquivalence`, `reverse_append`, `reverse_involutes`, `encodeDecodeRoundTrip`, `RevAcc_Helper`, `RevAcc_Correct`, `StackInduction`
