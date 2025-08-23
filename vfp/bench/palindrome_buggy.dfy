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
  match xs
  case Nil => Nil
  case Cons(h, t) => append(xs, reverse(t))  // Bug: should be reverse(xs) not reverse(t)
}

lemma {:axiom} makePalindromeCorrect<T>(xs: List<T>)
  ensures isPalindrome(makePalindrome(xs))