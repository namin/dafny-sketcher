// Stack operations: push, pop, peek, isEmpty with LIFO properties

datatype Stack<T> = Stack(elements: seq<T>)

function {:spec} emptyStack<T>(): Stack<T>
{
  Stack([])
}

predicate {:spec} isEmpty<T>(s: Stack<T>)
{
  s.elements == []
}

function {:spec} push<T>(s: Stack<T>, x: T): Stack<T>
{
  Stack([x] + s.elements)
}

function {:spec} pop<T>(s: Stack<T>): Stack<T>
  requires !isEmpty(s)
{
  Stack(s.elements[1..])
}

function {:spec} peek<T>(s: Stack<T>): T
  requires !isEmpty(s)
{
  s.elements[0]
}

function {:spec} size<T>(s: Stack<T>): nat
{
  |s.elements|
}

predicate {:spec} contains<T(==)>(s: Stack<T>, x: T)
{
  x in s.elements
}

function {:spec} toSeq<T>(s: Stack<T>): seq<T>
{
  s.elements
}

// Stack from sequence
function {:spec} fromSeq<T>(elements: seq<T>): Stack<T>
{
  Stack(elements)
}

// Multiple push operations
function {:spec} pushAll<T>(s: Stack<T>, items: seq<T>): Stack<T>
  decreases |items|
{
  if |items| == 0 then s
  else pushAll(push(s, items[0]), items[1..])
}

// Multiple pop operations
function {:spec} popN<T>(s: Stack<T>, n: nat): Stack<T>
  requires n <= size(s)
  decreases n
{
  if n == 0 then s
  else popN(pop(s), n - 1)
}

// Get the nth element from top (0-indexed)
function {:spec} nthFromTop<T>(s: Stack<T>, n: nat): T
  requires n < size(s)
{
  s.elements[n]
}

lemma PushPopIdentity<T>(s: Stack<T>, x: T)
  ensures pop(push(s, x)) == s
  ensures peek(push(s, x)) == x
{
  // Automatic
}

lemma PopPushNotIdentity<T>(s: Stack<T>, x: T)
  requires !isEmpty(s)
  requires x != peek(s)
  ensures push(pop(s), x) != s
{
  assert push(pop(s), x).elements[0] == x;
  assert s.elements[0] == peek(s);
  assert x != peek(s);
}

lemma PushIncreaseSize<T>(s: Stack<T>, x: T)
  ensures size(push(s, x)) == size(s) + 1
{
  // Automatic
}

lemma PopDecreaseSize<T>(s: Stack<T>)
  requires !isEmpty(s)
  ensures size(pop(s)) == size(s) - 1
{
  // Automatic
}

lemma EmptyStackProperties<T>(s: Stack<T>)
  ensures isEmpty(s) <==> size(s) == 0
  ensures isEmpty(s) <==> s.elements == []
{
  // Automatic
}

lemma LIFOProperty<T>(s: Stack<T>, x: T, y: T)
  ensures peek(push(push(s, x), y)) == y
  ensures peek(pop(push(push(s, x), y))) == x
{
  // Automatic - Last In First Out
}

lemma PushAllCorrect<T>(s: Stack<T>, items: seq<T>)
  ensures size(pushAll(s, items)) == size(s) + |items|
  decreases |items|
{
  if |items| == 0 {
    // Base case
  } else {
    PushAllCorrect(push(s, items[0]), items[1..]);
  }
}

lemma PopNCorrect<T>(s: Stack<T>, n: nat)
  requires n <= size(s)
  ensures size(popN(s, n)) == size(s) - n
  decreases n
{
  if n == 0 {
    // Base case
  } else {
    PopNCorrect(pop(s), n - 1);
  }
}

lemma PushPreservesContains<T>(s: Stack<T>, x: T, y: T)
  ensures contains(push(s, x), y) <==> (y == x || contains(s, y))
{
  // Automatic
}

lemma StackToFromSeq<T>(s: Stack<T>)
  ensures fromSeq(toSeq(s)) == s
  ensures toSeq(fromSeq(s.elements)) == s.elements
{
  // Automatic
}

lemma PushOrder<T>(s: Stack<T>, x: T, y: T)
  ensures toSeq(push(push(s, x), y)) == [y, x] + toSeq(s)
{
  calc == {
    toSeq(push(push(s, x), y));
    push(push(s, x), y).elements;
    [y] + push(s, x).elements;
    [y] + ([x] + s.elements);
    [y, x] + s.elements;
    [y, x] + toSeq(s);
  }
}

lemma NthFromTopCorrect<T>(s: Stack<T>, n: nat)
  requires n < size(s)
  ensures nthFromTop(s, n) == toSeq(s)[n]
{
  // Automatic
}

lemma StackInduction<T>(s: Stack<T>)
  ensures s == emptyStack() || exists x, s' :: s == push(s', x)
{
  if isEmpty(s) {
    assert s == emptyStack();
  } else {
    var s' := pop(s);
    var x := peek(s);
    assert s == push(s', x);
  }
}