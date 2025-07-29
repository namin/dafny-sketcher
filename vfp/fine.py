import re
from typing import List, Optional, Tuple
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
    lines = p.splitlines(keepends=True)
    start_offset = driver.line_col_to_start_offset(p, lines, todo['insertLine'], todo['insertColumn'])
    end_offset = driver.line_col_to_end_offset(p, lines, todo['endLine'], todo['endColumn'])
    print(start_offset, end_offset)
    body = p[start_offset:end_offset]
    print('BODY')
    print(body)
    print('ANNOTATED BODY')
    b = annotate_body(body)
    print(b)
    ip = insert_program_todo(todo, p, b)
    print('REPLACED BODY')
    print(ip)
    print('ERRORS')
    errors = show_errors_todo(ip, todo)
    prompt = prompt_fine_implementer(todo, ip, b, errors)
    print('PROMPT')
    print(prompt)
    r = generate(prompt)
    print(r)
    ox = extract_dafny_block(r)
    if ox is None:
        return None
    (n, x) = ox
    xp = replace_block_in_program(ip, n, x)
    if xp is None:
        return None
    xp = remove_all_block_markers(xp)
    print('XP')
    print(xp)
    x_errors = show_errors_todo(xp, todo)
    print('XP ERRORS')
    print(x_errors)
    if x_errors.count('\n') > errors.count('\n'):
        return None
    return xp

def remove_all_block_markers(ip: str) -> str:
    """Remove all block markers of the form /*n*/ from the input string."""
    return re.sub(r'/\*\d+\*/', '', ip)

def replace_block_in_program(p: str, n: int, x: str) -> Optional[str]:
    """Replace the content inside a strictly formatted block like {/*n*/.../*n*/}, preserving the markers."""
    pattern = re.compile(rf'(\{{/\*{n}\*/)(.*?)(/\*{n}\*/\}})', re.DOTALL)
    match = pattern.search(p)
    if not match:
        return None
    return p[:match.start()] + match.group(1) + x + match.group(3) + p[match.end():]

def extract_dafny_block(text: str) -> Optional[Tuple[int, str]]:
    """Extract the Dafny block number and content between the markers."""
    text = driver.remove_think_blocks(text)
    pattern = r'// BEGIN DAFNY BLOCK (\d+)(.*?)// END DAFNY BLOCK \1'
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        return None
    block_num = int(match.group(1))
    block_content = match.group(2).strip()
    return (block_num, block_content)

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
    lines = (sketcher.show_errors(p) or "").splitlines()
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

Do NOT include the outer blocks of the block number you choose, only what should go between the /*n*/ markers.

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
    xp = fine_implementer(demo, todo)
    print(xp)