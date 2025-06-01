from llm import default_generate as generate, extract_dafny_program
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
        xp = implementer(p, llm_implementer(p, todo), todo)
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

def llm_implementer(p: str, todo) -> str:
    prompt = prompt_function_implementer(p, todo['name']) if todo['type'] == 'function' else prompt_lemma_implementer(p, todo['name'])
    r = generate(prompt)
    print(r)
    x = extract_dafny_program(r)
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
    return f"You are translating an idea for a Dafny program into a specification, consisting of datatypes, function signatures (without implementation bodies) and lemmas (using the {{:axiom}} annotation after lemma keyword and without body). Here is the idea:\n{idea}\n\nPlease output the specification without using an explicit module. Omit the bodies for functions and lemmas -- Do not even include the outer braces."

def prompt_function_implementer(program: str, name: str) -> str:
    return f"You are implementing a function in a Dafny program that is specified but not fully implemented. The current program is\n{program}\n\nThe function to implement is {name}. Please just provide the body of the function (without the outer braces)."

def prompt_lemma_implementer(program: str, name: str) -> str:
    return f"You are implementing a lemma in a Dafny program that is specified but not fully implemented. The current program is\n{program}\n\nThe lemma to implement is {name}. Please just provide the body of the lemma (without the outer braces)."

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
    #result = drive_ex(idea)
    result = drive_program(spec)
    print("FINAL RESULT")
    print(result)
