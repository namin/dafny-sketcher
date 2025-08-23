// Run-Length Encoding
// RLE compresses consecutive identical characters into (count, char) pairs

datatype RLE = RLE(count: nat, ch: char)

predicate {:spec} validRLE(encoded: seq<RLE>)
{
  forall i :: 0 <= i < |encoded| ==> 
    encoded[i].count > 0 &&
    (i + 1 < |encoded| ==> encoded[i].ch != encoded[i+1].ch)
}

function {:spec} decode(encoded: seq<RLE>): seq<char>
{
  if |encoded| == 0 then []
  else repeatChar(encoded[0].count, encoded[0].ch) + decode(encoded[1..])
}

function {:spec} repeatChar(n: nat, c: char): seq<char>
{
  if n == 0 then []
  else [c] + repeatChar(n-1, c)
}

function encode(s: seq<char>): seq<RLE>
{
  if |s| == 0 then []
  else if |s| == 1 then [RLE(1, s[0])]
  else 
    var rest := encode(s[1..]);
    if |rest| > 0 && rest[0].ch == s[0] then
      [RLE(rest[0].count + 1, s[0])] + rest[1..]
    else
      [RLE(1, s[0])] + rest
}

lemma encodeProducesValidRLE(s: seq<char>)
  ensures validRLE(encode(s))
{
  if |s| <= 1 {
    // Base cases are trivial
  } else {
    var rest := encode(s[1..]);
    encodeProducesValidRLE(s[1..]); // Recursive call for induction
    if |rest| > 0 && rest[0].ch == s[0] {
      // When merging, we maintain validity since we're just incrementing count
      assert validRLE([RLE(rest[0].count + 1, s[0])] + rest[1..]);
    } else {
      // When not merging, s[0] != rest[0].ch (if rest is non-empty)
      assert validRLE([RLE(1, s[0])] + rest);
    }
  }
}

lemma encodeDecodeRoundTrip(s: seq<char>)
  ensures decode(encode(s)) == s
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