import re
from typing import List, Optional
from llm import default_generate as generate
import sketcher
import driver

def drive_program(p: str, max_iterations: Optional[int] = None) -> str:
    i = 0
    while max_iterations is None or i < max_iterations:
        i += 1
        todos = sketcher.sketch_todo_lemmas(p)
        if not todos:
            return p
        todo = todos[0]
        xp = fine_implementer(p, todo)
        if xp is None:
            print("Didn't solve todo")
            continue
        p = xp
        print("PROGRAM")
        print(p)
    print(f'Solved in {i} iterations')
    return p

def fine_implementer(p: str, todo) -> Optional[str]:
    return None

def annotate_body(b: str) -> str:
    s = ""
    k = []
    c = 0
    for x in b:
        if x == '{':
            s += '{/*'+str(c)+'*/'
            k = k + [c]
            c += 1
        elif x == '}':
            s += '/*'+str(k.pop())+'*/}'
        else:
            s += x
    return s

def insert_program_todo(todo, p, x):
    assert todo['status'] != 'todo'
    lines = p.splitlines(keepends=True)
    start_offset = driver.line_col_to_start_offset(p,lines, todo['insertLine'], todo['insertColumn'])
    end_offset = driver.line_col_to_end_offset(p, lines, todo['endLine'], todo['endColumn'])
    xp = p[:start_offset] + x + p[end_offset:]
    print("XP")
    print(xp)
    return xp

def show_errors_todo(p, todo):
    lines = sketcher.show_errors(p).splitlines()
    name = todo['name']
    lemma_lines = [line for line in lines if line.startswith(name+":")]
    return "\n".join(lemma_lines)

def prompt_fine_implementer(todo, code, body, errors):
    return f"""
You are improvemening piecemal the implementation of lemma {todo['name']} in the following Dafny program:
{code}

Pick a block in the lemma {todo['name']}, for example block *1*, and re-implement the block with by starting with line
// BEGIN DAFNY BLOCK 1
and ending with line
// END DAFNY BLOCK 1
where you replace 1 with the block number you choose among the body of lemma {todo['name']},
which is:
{body}

Do not include the outer blocks of the block number you choose.

The errors in the work-in-progress lemma are:
{errors}
"""

if __name__ == "__main__":
    demo = None
    with open('examples/StlcDemo.dfy', 'r') as file:
        demo = file.read()
    todos = sketcher.sketch_todo_lemmas(demo)
    print(todos)
    todo = todos[0]
    lines = demo.splitlines(keepends=True)
    start_offset = driver.line_col_to_start_offset(demo, lines, todo['insertLine'], todo['insertColumn'])
    end_offset = driver.line_col_to_end_offset(demo, lines, todo['endLine'], todo['endColumn'])
    print(start_offset, end_offset)
    body = demo[start_offset:end_offset]
    print('BODY')
    print(body)
    print('ANNOTATED BODY')
    b = annotate_body(body)
    print(b)
    ip = insert_program_todo(todo, demo, b)
    print('REPLACED BODY')
    print(ip)
    print('ERRORS')
    errors = show_errors_todo(ip, todo)
    print('PROMPT')
    print(prompt_fine_implementer(todo, demo, b, errors))
