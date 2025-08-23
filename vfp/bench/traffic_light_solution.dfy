datatype light = Red | Yellow | Green

function activation(source: light, target: light): seq<light>
{
  if source == target then [source]
  else if source == Yellow || target == Yellow then [source, target]
  else [source, Yellow, target]
}

predicate adjacent_ok(l1: light, l2: light)
{
  !(l1 == Red && l2 == Green) && !(l1 == Green && l2 == Red)
}

predicate all_adjacent_ok(lights: seq<light>)
{
  forall i :: 0 <= i < |lights| - 1 ==> adjacent_ok(lights[i], lights[i+1])
}

lemma check_activation(source: light, target: light)
  ensures all_adjacent_ok(activation(source, target))
{
  var result := activation(source, target);
  
  if source == target {
    assert result == [source];
    assert |result| == 1;
    assert all_adjacent_ok(result);
  } else if source == Yellow || target == Yellow {
    assert result == [source, target];
    assert |result| == 2;
    if source == Yellow {
      assert adjacent_ok(Yellow, target);
    } else {
      assert target == Yellow;
      assert adjacent_ok(source, Yellow);
    }
  } else {
    assert result == [source, Yellow, target];
    assert |result| == 3;
    assert source != Yellow && target != Yellow;
    assert source != target;
    assert adjacent_ok(source, Yellow);
    assert adjacent_ok(Yellow, target);
  }
}