datatype light = Red | Yellow | Green

function activation(source: light, target: light): seq<light>

predicate {:spec} adjacent_ok(l1: light, l2: light)
{
  !(l1 == Red && l2 == Green) && !(l1 == Green && l2 == Red)
}

predicate {:spec} all_adjacent_ok(lights: seq<light>)
{
  forall i :: 0 <= i < |lights| - 1 ==> adjacent_ok(lights[i], lights[i+1])
}

lemma {:axiom} check_activation(source: light, target: light)
  ensures all_adjacent_ok(activation(source, target))