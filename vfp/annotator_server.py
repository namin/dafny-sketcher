from fastapi import FastAPI
from typing import List, Optional
from llm import default_generate as generate

app = FastAPI()

END = 'END###'

def make_prompt(test_program: str) -> str:
    return f"""Given each Dafny program, propose an assertion, invariant or decreases statement in order to verify the program.
Program 1:
method maxArray(a: array<int>) returns (m: int)
  requires a.Length >= 1
  ensures forall k :: 0 <= k < a.Length ==> m >= a[k]
  ensures exists k :: 0 <= k < a.Length && m == a[k]
{{
  m := a[0];
  var index := 1;
  while (index < a.Length)
    /*[CODE_HERE]*/
     decreases a.Length - index
  {{
    m := if m>a[index] then  m else a[index];
    index := index + 1;
  }}
}}

Action: invariant 0 <= index <= a.Length
{END}

Program 2:
method intersperse(numbers: seq<int>, delimiter: int) returns (interspersed: seq<int>)
    ensures |interspersed| == if |numbers| > 0 then 2 * |numbers| - 1 else 0
    ensures forall i :: 0 <= i < |interspersed| ==> i % 2 == 0 ==>
                interspersed[i] == numbers[i / 2]
    ensures forall i :: 0 <= i < |interspersed| ==> i % 2 == 1 ==>
                interspersed[i] == delimiter
{{
    interspersed := [];
    for i := 0 to |numbers|
    /*[CODE_HERE]*/
    {{
        if i > 0 {{
            interspersed := interspersed + [delimiter];
        }}
        interspersed := interspersed + [numbers[i]];
    }}
}}

Action: invariant |interspersed| == if i > 0 then 2 * i - 1 else 0
invariant forall i0 :: 0 <= i0 < |interspersed| ==> i0 % 2 == 0 ==> interspersed[i0] == numbers[i0 / 2]
invariant forall i0 :: 0 <= i0 < |interspersed| ==> i0 % 2 == 1 ==> interspersed[i0] == delimiter
{END}

Program 3:
{test_program}

Action:"""

    return p + ' ' + f'\n{END}\n'

def annotate1(program: str) -> str:
    r = generate(make_prompt(program))
    assert r.endswith('\n'+END)
    return r[:-len('\n'+END)]

@app.post("/annotate")
async def annotate(program: str) -> List[str]:
    return [annotate1(program) for i in range(0, 2)]
