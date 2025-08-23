function fib(n: nat): nat

function fibPair(n: nat): (nat, nat)

lemma {:axiom} fibCorrect(n: nat)
  ensures fib(0) == 0
  ensures fib(1) == 1
  ensures n >= 2 ==> fib(n) == fib(n-1) + fib(n-2)

lemma {:axiom} fibPairCorrect(n: nat)
  ensures fibPair(n) == (fib(n), fib(n+1))

lemma {:axiom} fibIncreasing(n: nat)
  ensures fib(n) <= fib(n+1)