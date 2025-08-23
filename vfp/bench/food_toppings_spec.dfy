datatype Topping = Tomato | Cheese | Olive | Broccoli | Mushroom | Pepper

datatype Food = Pasta(toppings: seq<Topping>) | Pizza(toppings: seq<Topping>)

predicate {:spec} ok(f: Food)
{
  match f
  case Pizza(tops) => |tops| <= 5
  case Pasta(tops) => |tops| <= 2
}

lemma {:axiom} ok3_pizza(f: Food)
  requires ok(f)
  requires |f.toppings| >= 3
  ensures f.Pizza?