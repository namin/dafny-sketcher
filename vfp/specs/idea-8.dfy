datatype List<T> = Nil | Cons(head: T, tail: List<T>)

// This function should reverse a list.
function reverse<T>(l: List<T>): List<T>

// This lemma should prove that reversing a list preserves the elements (permutation).
lemma {:axiom} reverse_permutes<T>(l: List<T>, element: T)
ensures contains(l, element) <==> contains(reverse(l), element)

// This lemma should prove that reversing a list twice yields the original list.
lemma {:axiom} reverse_involutes<T>(l: List<T>)
ensures reverse(reverse(l)) == l

//Helper function to check if an element exists in a list.
function contains<T>(l: List<T>, element: T): bool
