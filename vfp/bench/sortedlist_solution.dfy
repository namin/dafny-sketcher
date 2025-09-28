datatype List = Nil | Cons(head: int, tail: List)

predicate SortedBetween(l: List, lo: int, hi: int)
{
  match l
    case Nil => true
    case Cons(x, xs) => lo <= x < hi && SortedBetween(xs, x, hi)
}

function insert(l: List, x: int): List {
  match l
    case Nil => Cons(x, Nil)
    case Cons(y, ys) =>
      if x < y then Cons(x, l) else Cons(y, insert(ys, x))
}

lemma InsertPreservesSortedBetween(l: List, x: int, lo: int, hi: int)
  requires SortedBetween(l, lo, hi)
  requires lo <= x < hi
  ensures  SortedBetween(insert(l, x), lo, hi)
{
}

function app(xs: List, ys: List): List {
  match xs
    case Nil => ys
    case Cons(x, xs') => Cons(x, app(xs', ys))
}

function revAcc(xs: List, acc: List): List {
  match xs
    case Nil => acc
    case Cons(x, xs') => revAcc(xs', Cons(x, acc))
}

lemma RevAcc_Helper(xs: List, acc: List)
  ensures revAcc(xs, acc) == app(revAcc(xs, Nil), acc)
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

lemma AppendAssoc(xs: List, ys: List, zs: List)
  ensures app(app(xs, ys), zs) == app(xs, app(ys, zs))
{
  match xs {
    case Nil => 
    case Cons(x, xs') => 
      AppendAssoc(xs', ys, zs);
  }
}

lemma RevAcc_Correct(xs: List, acc: List)
  ensures revAcc(xs, acc) == app(revAcc(xs, Nil), acc)
{
  RevAcc_Helper(xs, acc);
}