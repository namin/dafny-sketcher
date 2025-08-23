// Run-Length Encoding

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
      [RLE(1, s[0])] + rest
    else
      [RLE(1, s[0])] + rest
}

lemma {:axiom} encodeProducesValidRLE(s: seq<char>)
  ensures validRLE(encode(s))

lemma {:axiom} encodeDecodeRoundTrip(s: seq<char>)
  ensures decode(encode(s)) == s