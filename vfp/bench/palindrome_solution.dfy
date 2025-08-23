datatype List<T> = Nil | Cons(head: T, tail: List<T>)

function reverse<T>(xs: List<T>): List<T>
{
  match xs
  case Nil => Nil
  case Cons(h, t) => append(reverse(t), Cons(h, Nil))
}

function append<T>(xs: List<T>, ys: List<T>): List<T>
{
  match xs
  case Nil => ys
  case Cons(h, t) => Cons(h, append(t, ys))
}

predicate {:spec} isPalindrome<T(==)>(xs: List<T>)
{
  xs == reverse(xs)
}

function makePalindrome<T>(xs: List<T>): List<T>
{
  append(xs, reverse(xs))
}

lemma appendNilRight<T>(xs: List<T>)
  ensures append(xs, Nil) == xs
{
  match xs
  case Nil => 
  case Cons(h, t) => appendNilRight(t);
}

lemma appendAssoc<T>(xs: List<T>, ys: List<T>, zs: List<T>)
  ensures append(append(xs, ys), zs) == append(xs, append(ys, zs))
{
  match xs
  case Nil =>
  case Cons(h, t) => appendAssoc(t, ys, zs);
}

lemma reverseAppend<T>(xs: List<T>, ys: List<T>)
  ensures reverse(append(xs, ys)) == append(reverse(ys), reverse(xs))
{
  match xs
  case Nil => 
    assert reverse(append(Nil, ys)) == reverse(ys);
    appendNilRight(reverse(ys));
  case Cons(h, t) =>
    reverseAppend(t, ys);
    appendAssoc(reverse(ys), reverse(t), Cons(h, Nil));
}

lemma reverseReverse<T>(xs: List<T>)
  ensures reverse(reverse(xs)) == xs
{
  match xs
  case Nil =>
  case Cons(h, t) =>
    reverseReverse(t);
    reverseAppend(reverse(t), Cons(h, Nil));
    assert reverse(Cons(h, Nil)) == Cons(h, Nil);
}

lemma makePalindromeCorrect<T>(xs: List<T>)
  ensures isPalindrome(makePalindrome(xs))
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