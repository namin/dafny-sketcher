function sum(xs: seq<int>): int
{
  if |xs| == 0 then 0
  else xs[0] + sum(xs[1..])
}

function sumTail(xs: seq<int>, acc: int): int
  decreases |xs|
{
  if |xs| == 0 then acc
  else sumTail(xs[1..], acc + xs[0])
}

lemma sumCorrect(xs: seq<int>)
  ensures sum(xs) == sumTail(xs, 0)
{
  sumCorrectHelper(xs, 0);
}

lemma sumCorrectHelper(xs: seq<int>, acc: int)
  ensures sumTail(xs, acc) == acc + sum(xs)
{
  if |xs| == 0 {
  } else {
    calc {
      sumTail(xs, acc);
      == sumTail(xs[1..], acc + xs[0]);
      == { sumCorrectHelper(xs[1..], acc + xs[0]); }
      (acc + xs[0]) + sum(xs[1..]);
      == acc + (xs[0] + sum(xs[1..]));
      == acc + sum(xs);
    }
  }
}

lemma sumAppend(xs: seq<int>, ys: seq<int>)
  ensures sum(xs + ys) == sum(xs) + sum(ys)
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

lemma sumDistributive(xs: seq<int>, c: int)
  ensures sum(seq(|xs|, i requires 0 <= i < |xs| => c * xs[i])) == c * sum(xs)
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
