function sum(xs: seq<int>): int

function sumTail(xs: seq<int>, acc: int): int

lemma {:axiom} sumCorrect(xs: seq<int>)
  ensures sum(xs) == sumTail(xs, 0)

lemma {:axiom} sumAppend(xs: seq<int>, ys: seq<int>)
  ensures sum(xs + ys) == sum(xs) + sum(ys)

lemma {:axiom} sumDistributive(xs: seq<int>, c: int)
  ensures sum(seq(|xs|, i requires 0 <= i < |xs| => c * xs[i])) == c * sum(xs)