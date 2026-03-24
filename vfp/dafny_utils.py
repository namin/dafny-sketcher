import re

def line_col_to_offset(lines: list[str], line: int, col: int) -> int:
    return sum(len(l) for l in lines[:line - 1]) + (col - 1)

def line_col_to_start_offset(p: str,lines: list[str], line: int, col: int) -> int:
    return line_col_to_offset(lines, line, col)

def line_col_to_end_offset(p: str, lines: list[str], line: int, col: int) -> int:
    return line_col_to_offset(lines, line, col)+1

def insert_program_todo_helper(todo, p, x):
    if todo['status'] != 'todo':
        #print('CASE DONE')
        lines = p.splitlines(keepends=True)
        start_offset = line_col_to_start_offset(p,lines, todo['insertLine'], todo['insertColumn'])
        end_offset = line_col_to_end_offset(p, lines, todo['endLine'], todo['endColumn'])
        after_offset = end_offset
        to_skip = ''.join(p[start_offset:end_offset])
        # Hack: because sometimes skipping to the end_offset swallows lemmas coming after
        # Strip line and block comments before checking so comment-only bodies don't trigger this
        stripped = re.sub(r'//[^\n]*', '', to_skip)
        stripped = re.sub(r'/\*.*?\*/', '', stripped, flags=re.DOTALL)
        if 'lemma ' in stripped:
            after_offset = start_offset
        xp = p[:start_offset] + "{\n" + x + "\n}" + p[after_offset:]
    else:
        #print('CASE TODO')
        line = todo['insertLine']
        lines = p.splitlines(keepends=True)
        
        # Ensure the target line doesn't end with newline for clean insertion
        lines[line-1] = lines[line-1].rstrip('\n\r')
        
        # Create insertion lines as separate array elements
        insertion_lines = ["\n", "{\n", x + "\n", "}\n"]
        
        # Insert the new lines into the array after the target line
        lines[line:line] = insertion_lines
        
        if todo['type'] == 'lemma':
            line_lemma = todo['startLine']
            lines[line_lemma-1] = lines[line_lemma-1].replace('{:axiom}', '')
        xp = ''.join(lines)
    return xp


def brace_depth(lines: list[str], through_idx: int) -> int:
    """Return brace depth (opens - closes) after processing lines[0..through_idx] inclusive."""
    depth = 0
    for i in range(through_idx + 1):
        depth += lines[i].count("{") - lines[i].count("}")
    return depth


def extract_snippet_from_line(path: str, line_no: int) -> str:
    """Extract code from line_no until the matching closing brace, or just the line if no open brace."""
    try:
        with open(path, "r") as f:
            lines = f.readlines()
    except OSError as e:
        return f"[error: could not read file: {e}]"
    # Line numbers are 1-based
    if line_no < 1 or line_no > len(lines):
        return f"[error: line {line_no} out of range (file has {len(lines)} lines)]"
    start_idx = line_no - 1
    start_line = lines[start_idx]
    if "{" not in start_line:
        return start_line.rstrip()
    # Depth at start of error line; include until the block opened by "{" on this line is closed
    target_depth = brace_depth(lines, start_idx - 1) if start_idx > 0 else 0
    depth = target_depth + (start_line.count("{") - start_line.count("}"))
    close_depth = depth - 1  # one level down = block opened on this line is closed
    end_idx = start_idx
    while depth > close_depth and end_idx + 1 < len(lines):
        end_idx += 1
        depth += lines[end_idx].count("{") - lines[end_idx].count("}")
    snippet_lines = lines[start_idx : end_idx + 1]
    return "".join(snippet_lines).rstrip()