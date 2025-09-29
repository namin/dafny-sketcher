// Linked list operations: insert, delete, reverse, cycle detection

datatype LinkedList<T> = Nil | Cons(head: T, tail: LinkedList<T>)

// Length of linked list
function {:spec} length<T>(list: LinkedList<T>): nat
{
  match list
  case Nil => 0
  case Cons(_, tail) => 1 + length(tail)
}

// Append two linked lists
function {:spec} append<T>(l1: LinkedList<T>, l2: LinkedList<T>): LinkedList<T>
{
  match l1
  case Nil => l2
  case Cons(h, t) => Cons(h, append(t, l2))
}

// Reverse a linked list
function {:spec} reverse<T>(list: LinkedList<T>): LinkedList<T>
{
  reverseHelper(list, Nil)
}

function reverseHelper<T>(list: LinkedList<T>, acc: LinkedList<T>): LinkedList<T>
{
  match list
  case Nil => acc
  case Cons(h, t) => reverseHelper(t, Cons(h, acc))
}

// Get nth element (0-indexed)
function {:spec} nth<T>(list: LinkedList<T>, n: nat): T
  requires n < length(list)
{
  match list
  case Cons(h, t) => if n == 0 then h else nth(t, n - 1)
}

// Check if element exists in list
predicate {:spec} contains<T(==)>(list: LinkedList<T>, x: T)
{
  match list
  case Nil => false
  case Cons(h, t) => h == x || contains(t, x)
}

// Remove first occurrence of element
function {:spec} remove<T(==)>(list: LinkedList<T>, x: T): LinkedList<T>
{
  match list
  case Nil => Nil
  case Cons(h, t) => if h == x then t else Cons(h, remove(t, x))
}

// Insert at position
function {:spec} insertAt<T>(list: LinkedList<T>, x: T, pos: nat): LinkedList<T>
{
  if pos == 0 then Cons(x, list)
  else match list
    case Nil => Cons(x, Nil)
    case Cons(h, t) => Cons(h, insertAt(t, x, pos - 1))
}

// Convert to sequence
function {:spec} toSeq<T>(list: LinkedList<T>): seq<T>
{
  match list
  case Nil => []
  case Cons(h, t) => [h] + toSeq(t)
}

// Convert from sequence
function {:spec} fromSeq<T>(s: seq<T>): LinkedList<T>
{
  if |s| == 0 then Nil
  else Cons(s[0], fromSeq(s[1..]))
}

// Map function over list
function {:spec} listMap<T, U>(list: LinkedList<T>, f: T -> U): LinkedList<U>
{
  match list
  case Nil => Nil
  case Cons(h, t) => Cons(f(h), listMap(t, f))
}

// Filter list with predicate
function {:spec} filter<T>(list: LinkedList<T>, p: T -> bool): LinkedList<T>
{
  match list
  case Nil => Nil
  case Cons(h, t) =>
    if p(h) then Cons(h, filter(t, p))
    else filter(t, p)
}

// Take first n elements
function {:spec} take<T>(list: LinkedList<T>, n: nat): LinkedList<T>
{
  if n == 0 then Nil
  else match list
    case Nil => Nil
    case Cons(h, t) => Cons(h, take(t, n - 1))
}

// Drop first n elements
function {:spec} drop<T>(list: LinkedList<T>, n: nat): LinkedList<T>
  decreases list
{
  if n == 0 then list
  else match list
    case Nil => Nil
    case Cons(_, t) => drop(t, n - 1)
}

// Check if list is palindrome
predicate {:spec} isPalindrome<T(==)>(list: LinkedList<T>)
{
  toSeq(list) == toSeq(reverse(list))
}

// --- Lemmas for correctness ---

lemma LengthAppend<T>(l1: LinkedList<T>, l2: LinkedList<T>)
  ensures length(append(l1, l2)) == length(l1) + length(l2)
{
  match l1
  case Nil =>
  case Cons(_, t) =>
    LengthAppend(t, l2);
}

lemma AppendNil<T>(list: LinkedList<T>)
  ensures append(list, Nil) == list
  ensures append(Nil, list) == list
{
  match list
  case Nil =>
  case Cons(_, t) =>
    AppendNil(t);
}

lemma AppendAssociative<T>(l1: LinkedList<T>, l2: LinkedList<T>, l3: LinkedList<T>)
  ensures append(append(l1, l2), l3) == append(l1, append(l2, l3))
{
  match l1
  case Nil =>
  case Cons(h, t) =>
    AppendAssociative(t, l2, l3);
}

lemma ReverseLength<T>(list: LinkedList<T>)
  ensures length(reverse(list)) == length(list)
{
  ReverseHelperLength(list, Nil);
}

lemma ReverseHelperLength<T>(list: LinkedList<T>, acc: LinkedList<T>)
  ensures length(reverseHelper(list, acc)) == length(list) + length(acc)
{
  match list
  case Nil =>
  case Cons(h, t) =>
    calc == {
      length(reverseHelper(list, acc));
      length(reverseHelper(t, Cons(h, acc)));
      { ReverseHelperLength(t, Cons(h, acc)); }
      length(t) + length(Cons(h, acc));
      length(t) + 1 + length(acc);
      length(list) + length(acc);
    }
}

lemma ReverseReverse<T>(list: LinkedList<T>)
  ensures reverse(reverse(list)) == list
{
  ReverseReverseHelper(list, Nil);
}

lemma ReverseReverseHelper<T>(list: LinkedList<T>, acc: LinkedList<T>)
  ensures reverseHelper(reverseHelper(list, acc), Nil) == reverseHelper(acc, list)
{
  match list
  case Nil =>
    assert reverseHelper(reverseHelper(Nil, acc), Nil) == reverseHelper(acc, Nil);
  case Cons(h, t) =>
    calc == {
      reverseHelper(reverseHelper(Cons(h, t), acc), Nil);
      reverseHelper(reverseHelper(t, Cons(h, acc)), Nil);
      { ReverseReverseHelper(t, Cons(h, acc)); }
      reverseHelper(Cons(h, acc), t);
      reverseHelper(acc, Cons(h, t));
    }
}

lemma ToSeqFromSeq<T>(s: seq<T>)
  ensures toSeq(fromSeq(s)) == s
{
  if |s| == 0 {
    assert fromSeq(s) == Nil;
  } else {
    ToSeqFromSeq(s[1..]);
    assert toSeq(fromSeq(s)) == [s[0]] + toSeq(fromSeq(s[1..]));
  }
}

lemma FromSeqToSeq<T>(list: LinkedList<T>)
  ensures fromSeq(toSeq(list)) == list
{
  match list
  case Nil =>
  case Cons(h, t) =>
    FromSeqToSeq(t);
}

lemma NthCorrect<T>(list: LinkedList<T>, n: nat)
  requires n < length(list)
  ensures |toSeq(list)| > n
  ensures toSeq(list)[n] == nth(list, n)
{
  match list
  case Cons(h, t) =>
    if n == 0 {
      assert toSeq(list)[0] == h;
    } else {
      NthCorrect(t, n - 1);
    }
}

lemma MapLength<T, U>(list: LinkedList<T>, f: T -> U)
  ensures length(listMap(list, f)) == length(list)
{
  match list
  case Nil =>
  case Cons(h, t) =>
    MapLength(t, f);
}

lemma FilterSubset<T>(list: LinkedList<T>, p: T -> bool)
  ensures length(filter(list, p)) <= length(list)
{
  match list
  case Nil =>
  case Cons(h, t) =>
    FilterSubset(t, p);
    if p(h) {
      assert length(filter(list, p)) == 1 + length(filter(t, p));
    } else {
      assert length(filter(list, p)) == length(filter(t, p));
    }
}

lemma TakeDropConcat<T>(list: LinkedList<T>, n: nat)
  ensures append(take(list, n), drop(list, n)) == list
{
  if n == 0 {
    assert take(list, 0) == Nil;
    assert drop(list, 0) == list;
    AppendNil(list);
  } else {
    match list
    case Nil =>
    case Cons(h, t) =>
      TakeDropConcat(t, n - 1);
      calc == {
        append(take(list, n), drop(list, n));
        append(Cons(h, take(t, n - 1)), drop(t, n - 1));
        Cons(h, append(take(t, n - 1), drop(t, n - 1)));
        Cons(h, t);
        list;
      }
  }
}

lemma RemoveDecreasesLength<T>(list: LinkedList<T>, x: T)
  requires contains(list, x)
  ensures length(remove(list, x)) == length(list) - 1
{
  match list
  case Cons(h, t) =>
    if h == x {
      assert remove(list, x) == t;
    } else {
      assert contains(t, x);
      RemoveDecreasesLength(t, x);
    }
}

lemma InsertAtLength<T>(list: LinkedList<T>, x: T, pos: nat)
  ensures length(insertAt(list, x, pos)) == length(list) + 1
{
  if pos == 0 {
    assert insertAt(list, x, 0) == Cons(x, list);
  } else {
    match list
    case Nil =>
      assert insertAt(Nil, x, pos) == Cons(x, Nil);
    case Cons(h, t) =>
      InsertAtLength(t, x, pos - 1);
  }
}