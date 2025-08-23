datatype Topping = Tomato | Cheese | Olive | Broccoli | Mushroom | Pepper

datatype Food = Pasta(toppings: seq<Topping>) | Pizza(toppings: seq<Topping>)

predicate ok(f: Food)
{
  match f
  case Pizza(tops) => |tops| <= 5
  case Pasta(tops) => |tops| <= 2
}

lemma ok3_pizza(f: Food)
  requires ok(f)
  requires |f.toppings| >= 3
  ensures f.Pizza?
{
  match f
  case Pizza(_) =>
    // Already a pizza
  case Pasta(tops) =>
    // Pasta with ok(f) means |tops| <= 2
    // But we require |f.toppings| >= 3
    assert |tops| <= 2;
    assert |tops| >= 3;
    assert false;
}