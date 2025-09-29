// Queue operations: enqueue, dequeue, isEmpty, size

datatype Queue<T> = Queue(front: seq<T>, rear: seq<T>)

function {:spec} queueEmpty<T>(): Queue<T>
{
  Queue([], [])
}

predicate {:spec} queueIsEmpty<T>(q: Queue<T>)
{
  q.front == [] && q.rear == []
}

function {:spec} enqueue<T>(q: Queue<T>, x: T): Queue<T>
{
  Queue(q.front, [x] + q.rear)
}

function {:spec} dequeue<T>(q: Queue<T>): Queue<T>
  requires !queueIsEmpty(q)
{
  if |q.front| > 0 then
    Queue(q.front[1..], q.rear)
  else
    // Front is empty, so we reverse rear and put it in front
    if |q.rear| == 1 then
      Queue([], [])
    else
      Queue(reverse(q.rear)[1..], [])
}

function {:spec} queueFront<T>(q: Queue<T>): T
  requires !queueIsEmpty(q)
{
  if |q.front| > 0 then
    q.front[0]
  else
    // Front is empty, so the front element is the first element of rear (when reversed)
    q.rear[|q.rear| - 1]
}

function {:spec} queueSize<T>(q: Queue<T>): nat
{
  |q.front| + |q.rear|
}

function {:spec} queueToSeq<T>(q: Queue<T>): seq<T>
{
  q.front + reverse(q.rear)
}

function reverse<T>(s: seq<T>): seq<T>
{
  if |s| == 0 then []
  else reverse(s[1..]) + [s[0]]
}

// Alternative queue representation with invariant
datatype SimpleQueue<T> = SimpleQueue(elements: seq<T>)

function {:spec} simpleQueueEmpty<T>(): SimpleQueue<T>
{
  SimpleQueue([])
}

predicate {:spec} simpleQueueIsEmpty<T>(q: SimpleQueue<T>)
{
  q.elements == []
}

function {:spec} simpleEnqueue<T>(q: SimpleQueue<T>, x: T): SimpleQueue<T>
{
  SimpleQueue(q.elements + [x])
}

function {:spec} simpleDequeue<T>(q: SimpleQueue<T>): SimpleQueue<T>
  requires !simpleQueueIsEmpty(q)
{
  SimpleQueue(q.elements[1..])
}

function {:spec} simpleQueueFront<T>(q: SimpleQueue<T>): T
  requires !simpleQueueIsEmpty(q)
{
  q.elements[0]
}

function {:spec} simpleQueueSize<T>(q: SimpleQueue<T>): nat
{
  |q.elements|
}

lemma ReverseLength<T>(s: seq<T>)
  ensures |reverse(s)| == |s|
{
  if |s| == 0 {
    // Base case
  } else {
    ReverseLength(s[1..]);
    assert |reverse(s)| == |reverse(s[1..])| + 1;
  }
}

lemma ReverseReverse<T>(s: seq<T>)
  ensures reverse(reverse(s)) == s
{
  if |s| == 0 {
    // Base case
  } else {
    ReverseReverse(s[1..]);
    ReverseAppend(reverse(s[1..]), [s[0]]);
    assert reverse(reverse(s)) == s;
  }
}

lemma ReverseAppend<T>(s1: seq<T>, s2: seq<T>)
  ensures reverse(s1 + s2) == reverse(s2) + reverse(s1)
{
  if |s1| == 0 {
    assert s1 + s2 == s2;
    assert reverse(s1) == [];
  } else {
    assert s1 + s2 == [s1[0]] + (s1[1..] + s2);
    ReverseAppend(s1[1..], s2);
  }
}

lemma ReverseFirst<T>(s: seq<T>)
  requires |s| > 0
  ensures |reverse(s)| == |s|
  ensures reverse(s)[|reverse(s)| - 1] == s[0]
  ensures reverse(s)[0] == s[|s| - 1]
{
  ReverseLength(s);
  if |s| == 1 {
    assert reverse(s) == [s[0]];
  } else {
    ReverseFirst(s[1..]);
    assert reverse(s) == reverse(s[1..]) + [s[0]];
    ReverseLength(s[1..]);
    assert |reverse(s[1..])| == |s| - 1;
  }
}

lemma SeqAssoc<T>(a: seq<T>, b: seq<T>, c: seq<T>)
  ensures a + (b + c) == (a + b) + c
{
  // Dafny proves this automatically
}

lemma QueueSizeProperty<T>(q: Queue<T>)
  ensures queueSize(q) == |queueToSeq(q)|
{
  ReverseLength(q.rear);
}

lemma EnqueueCorrect<T>(q: Queue<T>, x: T)
  ensures queueToSeq(enqueue(q, x)) == queueToSeq(q) + [x]
  ensures queueSize(enqueue(q, x)) == queueSize(q) + 1
{
  var q' := enqueue(q, x);
  assert q'.front == q.front;
  assert q'.rear == [x] + q.rear;

  ReverseAppend([x], q.rear);
  assert reverse([x]) == [x];
  assert reverse([x] + q.rear) == reverse(q.rear) + reverse([x]);
  assert reverse([x] + q.rear) == reverse(q.rear) + [x];

  calc == {
    queueToSeq(q');
    q'.front + reverse(q'.rear);
    q.front + reverse([x] + q.rear);
    q.front + (reverse(q.rear) + [x]);
    { SeqAssoc(q.front, reverse(q.rear), [x]); }
    (q.front + reverse(q.rear)) + [x];
    queueToSeq(q) + [x];
  }

  QueueSizeProperty(q);
  QueueSizeProperty(q');
}

lemma DequeueCorrect<T>(q: Queue<T>)
  requires !queueIsEmpty(q)
  ensures |queueToSeq(q)| > 0
  ensures queueToSeq(dequeue(q)) == queueToSeq(q)[1..]
  ensures queueFront(q) == queueToSeq(q)[0]
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

lemma SimpleQueueEquivalence<T>(sq: SimpleQueue<T>, q: Queue<T>)
  requires sq.elements == queueToSeq(q)
  ensures simpleQueueIsEmpty(sq) == queueIsEmpty(q)
  ensures simpleQueueSize(sq) == queueSize(q)
{
  if queueIsEmpty(q) {
    assert q.front == [] && q.rear == [];
    assert queueToSeq(q) == [];
    assert sq.elements == [];
  }
  QueueSizeProperty(q);
}