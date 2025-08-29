idea = "Write (1) a datatype for arithmetic expressions, comparising constants, variables, and binary additions, (2) an evaluator function that takes an expression and an environment (function mapping variable to value) and return an integer value, (3) an optimizer function that removes addition by zero, (4) a lemma that ensures the optimizer preserves the semantics as defined by the evaluator."

spec = """datatype Expr =
  | Const(value: int)
  | Var(name: string)
  | Add(left: Expr, right: Expr)

type Environment = string -> int

function eval(e: Expr, env: Environment): int

function optimize(e: Expr): Expr

lemma {:axiom} optimizePreservesSemantics(e: Expr, env: Environment)
ensures eval(optimize(e), env) == eval(e, env)
"""

program_without_proof = """datatype Expr =
  | Const(value: int)
  | Var(name: string)
  | Add(left: Expr, right: Expr)

type Environment = string -> int

function eval(e: Expr, env: Environment): int
{
  match e
  case Const(val) => val
  case Var(name) => env(name)
  case Add(e1, e2) => eval(e1, env) + eval(e2, env)
}

function optimize(e: Expr): Expr
{
  match e
  case Add(e1, e2) =>
    var o1 := optimize(e1);
    var o2 := optimize(e2);
    if o2 == Const(0) then o1 else
    if o1 == Const(0) then o2 else Add(o1, o2)
  case _ => e
}

lemma {:axiom} optimizePreservesSemantics(e: Expr, env: Environment)
ensures eval(optimize(e), env) == eval(e, env)
"""

program_with_bugs = """datatype Expr =
  | Const(value: int)
  | Var(name: string)
  | Add(left: Expr, right: Expr)

predicate {:spec} optimal(e: Expr)
{
  match e
  case Add(Const(0), _) => false
  case Add(_, Const(0)) => false
  case Add(e1, e2) => optimal(e1) && optimal(e2)
  case _ => true
}

function optimize(e: Expr): Expr
{
  match e
  case Add(Const(0), e2) => optimize(e2)
  case Add(e1, Const(0)) => optimize(e1)
  case Add(e1, e2) => Add(optimize(e1), optimize(e2))
  case _ => e
}

lemma {:axiom} optimizeOptimal(e: Expr)
ensures optimal(optimize(e))
"""

spec_opt = """datatype Expr =
  | Const(value: int)
  | Var(name: string)
  | Add(left: Expr, right: Expr)

predicate {:spec} optimal(e: Expr)
{
  match e
  case Add(Const(0), _) => false
  case Add(_, Const(0)) => false
  case Add(e1, e2) => optimal(e1) && optimal(e2)
  case _ => true
}

function optimize(e: Expr): Expr

lemma {:axiom} optimizeOptimal(e: Expr)
ensures optimal(optimize(e))
"""

program_with_obvious_bug = """
function magic_number(): int {
    33
}

lemma {:axiom} magic_number_is_42()
ensures magic_number() == 42
"""

spec_all = """datatype Expr =
  | Const(value: int)
  | Var(name: string)
  | Add(left: Expr, right: Expr)

type Environment = string -> int

function eval(e: Expr, env: Environment): int

function optimize(e: Expr): Expr

lemma {:axiom} optimizePreservesSemantics(e: Expr, env: Environment)
ensures eval(optimize(e), env) == eval(e, env)

predicate {:spec} optimal(e: Expr)
{
  match e
  case Add(Const(0), _) => false
  case Add(_, Const(0)) => false
  case Add(e1, e2) => optimal(e1) && optimal(e2)
  case _ => true
}

lemma {:axiom} optimizeOptimal(e: Expr)
ensures optimal(optimize(e))
"""

nat_module = """
module NatModule {
    datatype Nat = Z | S(n: Nat)
    function add(n1: Nat, n2: Nat): Nat
    {
        match n1
        case Z => n2
        case S(n) => S(add(n, n2))
    }

    lemma {:axiom} add_comm(n1: Nat, n2: Nat)
    ensures add(n1, n2) == add(n2, n1)
}
"""

nat_module_empty_lemma_body = """
module NatModule {
    datatype Nat = Z | S(n: Nat)
    function add(n1: Nat, n2: Nat): Nat
    {
        match n1
        case Z => n2
        case S(n) => S(add(n, n2))
    }

    lemma add_comm(n1: Nat, n2: Nat)
    ensures add(n1, n2) == add(n2, n1)
    {
    }
}
"""

nat_use_module = """
module NatModule {
    datatype Nat = Z | S(n: Nat)
    function add(n1: Nat, n2: Nat): Nat
    {
        match n1
        case Z => n2
        case S(n) => S(add(n, n2))
    }
}

module NatUseModule {
    import NM = NatModule

    lemma {:axiom} add_comm(n1: NM.Nat, n2: NM.Nat)
    ensures NM.add(n1, n2) == NM.add(n2, n1)
}
"""

def read_file(fn):
    with open(fn, 'r') as file:
        return file.read()

def run(solver):
    import argparse
    
    parser = argparse.ArgumentParser(description='Run Dafny solver')
    parser.add_argument('--file', type=str, help='Path to Dafny file to process')
    
    args = parser.parse_args()
    
    if args.file:
        # Read the file and use its content with the solver
        file_content = read_file(args.file)
        solver(file_content)
    else:
        # Default behavior: run the test suite
        run_test(solver)

def run_test(solver):
    if False:
        print('NAT MODULE')
        solver(nat_module)
    if False:
        print('NAT USE MODULE')
        solver(nat_use_module)
    if False:
        print('BST')
        solver(read_file('examples/BST.dfy'))
    if True:
        print('GIVEN PROGRAM WITH SUBTLE BUGS')
        solver(program_with_bugs)
    if False:
        print('GIVEN PROGRAM WITH BUGS')
        solver(program_with_obvious_bug)
    if False:
        print('GIVEN SPEC')
        solver(spec_all)
