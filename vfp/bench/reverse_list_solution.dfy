function reverse<T>(l: seq<T>): seq<T>
{
  if |l| == 0 then []
  else reverse(l[1..]) + [l[0]]
}

lemma reverse_permutes<T>(l: seq<T>)
  ensures forall x :: x in l <==> x in reverse(l)
{
  if |l| == 0 {
  } else {
    reverse_permutes(l[1..]);
    forall x
      ensures x in l <==> x in reverse(l)
    {
      if x == l[0] {
        assert x in reverse(l);
      } else {
        assert x in l <==> x in l[1..];
        assert x in l[1..] <==> x in reverse(l[1..]);
        assert x in reverse(l[1..]) ==> x in reverse(l[1..]) + [l[0]];
      }
    }
  }
}

lemma reverse_append<T>(s1: seq<T>, s2: seq<T>)
  ensures reverse(s1 + s2) == reverse(s2) + reverse(s1)
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

lemma reverse_involutes<T>(l: seq<T>)
  ensures reverse(reverse(l)) == l
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