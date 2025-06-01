import re
from llm import default_generate as generate
import sketcher

def drive_ex(ex):
    p = None
    while p is None:
        p = spec_maker(ex)
    print("SPEC")
    print(p)
    return drive_program(p)

def drive_program(p: str) -> str:
    while True:
        todo = sketcher.sketch_next_todo(p)
        if todo is None:
            return p
        xp = dispatch_implementer(p, todo)
        if xp is None:
            print("Didn't solve todo")
            continue
        p = xp
        print("PROGRAM")
        print(p)
    return p

def spec_maker(idea: str) -> str:
    prompt = prompt_spec_maker(idea)
    r = generate(prompt)
    p = extract_dafny_program(r)
    if p is None:
        print("Missing Dafny program")
        return None
    e = sketcher.show_errors(p)
    if e is not None:
        print("Errors in spec maker:", e)
        return None
    return p

def dispatch_implementer(p: str, todo) -> str:
    if todo['type'] == 'function':
        return llm_implementer(p, todo)
    elif todo['type'] == 'lemma':
        return lemma_implementer(p, todo)

def lemma_implementer(p: str, todo) -> str:
    xp = implementer(p, "", todo)
    if xp:
        print("Empty proof works!")
        return xp
    x = sketcher.sketch_induction(p, todo['name'])
    xp = implementer(p, x, todo)
    if xp:
        print("Induction sketcher works!")
        return xp
    # TODO: could also try passing in the sketch as a starting point
    return llm_implementer(p, todo)

def llm_implementer(p: str, todo, prev: str = None) -> str:
    prompt = prompt_function_implementer(p, todo['name']) if todo['type'] == 'function' else prompt_lemma_implementer(p, todo['name'])
    if prev is not None:
        prompt += f"FYI only, a previous attempt on this {todo['type']} had the following errors:\n{prev}"
    r = generate(prompt)
    print(r)
    x = extract_dafny_program(r)
    if x is not None:
        x = extract_dafny_body(x, todo)
    if x is None:
        print("Missing Dafny program")
        return None
    xp = insert_progam_todo(todo, p, x)
    if xp is None:
        print("Couldn't patch program")
        return None
    e = sketcher.show_errors(xp)
    if e is not None:
        print("Errors in implementer:", e)
        if prev is None:
            return llm_implementer(p, todo, e)
        return None
    return xp

def remove_think_blocks(text):
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)

def extract_dafny_program(text: str) -> str:
    text = remove_think_blocks(text)
    """Extract the Dafny program between the markers."""
    start_marker = '// BEGIN DAFNY'
    end_marker = '// END DAFNY'
    start_idx = text.find(start_marker)
    end_idx = text.find(end_marker)
    if start_idx == -1 or end_idx == -1:
        return None
    return text[start_idx + len(start_marker):end_idx].strip()

def extract_dafny_body(x: str, todo) -> str:
    if todo['type'] in x:
        start = x.find('{')
        if start == -1:
            sign = todo['insertLine'] - todo['startLine'] + 1
            lines = x.split('\n')
            return '\n'.join(lines[sign:])
        else:
            return x[x.index('{')+1:x.rindex('}')-1]
    return x

def implementer(p: str, x: str, todo) -> str:
    if x is None:
        print("Missing Dafny program")
        return None
    xp = insert_progam_todo(todo, p, x)
    if xp is None:
        print("Couldn't patch program")
        return None
    e = sketcher.show_errors(xp)
    if e is not None:
        print("Errors in implementer:", e)
        return None
    return xp

def insert_progam_todo(todo, p, x):
    line = todo['insertLine']
    lines = p.split('\n')
    lines[line-1] = lines[line-1] + "\n{\n" + x + "\n}\n"
    if todo['type'] == 'lemma':
        line_lemma = todo['startLine']
        lines[line_lemma-1] = lines[line_lemma-1].replace('{:axiom}', '')
    xp = '\n'.join(lines)
    print("XP")
    print(xp)
    return xp

def prompt_spec_maker(idea: str) -> str:
    return f"You are translating an idea for a Dafny program into a specification, consisting of datatypes, function signatures (without implementation bodies) and lemmas (for lemmas only, using the {{:axiom}} attribute after lemma keyword and without body). Here is the idea:\n{idea}\n\nPlease output the specification without using an explicit module. Omit the bodies for functions and lemmas -- Do not even include the outer braces.  Please keep a comment before each function to explain what it should do. Provide the program spec, starting with a line \"// BEGIN DAFNY\", ending with a line \"// END DAFNY\"." + """\n
General hints about Dafny:
Do not generally use semicolons at the end of lines.
The attribute {:axiom} comes after the lemma keyword, and should not be used for functions. Example:
lemma {:axiom} lemma_zero_neutral(i: int)
ensures i + 0 == i
"""

def prompt_function_implementer(program: str, name: str) -> str:
    return f"You are implementing a function in a Dafny program that is specified but not fully implemented. The current program is\n{program}\n\nThe function to implement is {name}. Please just provide the body of the function (without the outer braces), starting with a line \"// BEGIN DAFNY\", ending with a line \"// END DAFNY\".\nSome hints about Dafny:\n" + """
The syntax for pattern match in Dafny is
match e
case Case1(arg1, arg2) => result1
case Case2(arg1) => result2
case _ => result3
You'll also need to have braces surrounding a result if is made of complex statements such as variable assignments.
For nested pattern matches, put the nested pattern match in parentheses:
match e1
case Case1(e2, ) => (
  match e2
  case Case2(c2) => result 2
)
case _ => result3

The syntax for variable assignment is
var x := e;

Variable assignments is one of the rare cases where semicolons are needed.
Do not use semicolons at the end of lines otherwise.
"""

def prompt_lemma_implementer(program: str, name: str) -> str:
    return f"You are implementing a lemma in a Dafny program that is specified but not fully implemented. The current program is\n{program}\n\nThe lemma to implement is {name}. Please just provide the body of the lemma (without the outer braces), starting with a line \"// BEGIN DAFNY\", ending with a line \"// END DAFNY\"."

if __name__ == "__main__":
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

    print('GIVEN SPEC')
    p = spec
    e = sketcher.show_errors(p)
    if e is not None:
        print("Errors")
        print(e)
    else:
      result = drive_program(p)
      print("FINAL RESULT GIVEN SPEC")
      print(result)
    print('--------------------------------')
    print('GIVEN IDEA')
    result = drive_ex(idea)
    print("FINAL RESULT GIVEN IDEA")
    print(result)
