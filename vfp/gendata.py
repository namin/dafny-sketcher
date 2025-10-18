import json
from llm import default_generate as generate
import sketcher
import driver

def lemma1(lemma, p, stats):
    name = lemma['name']
    stats["out"] = stats.get("out", [])
    lines = sketcher.sketch_proof_lines(p, name)
    for i, line in enumerate(lines):
        stats["out"].append(to_example(name, line, i, p))
    print("Added", len(lines), "proof lines for", name)

def to_example(name, line, i, p):
    lines = p.splitlines(keepends=True)
    start = driver.line_col_to_start_offset(p, lines, line['startLine'], line['startColumn'])
    end = driver.line_col_to_end_offset(p, lines, line['endLine'], line['endColumn'])
    proof_line = p[start:end]
    print("Proof line:", proof_line)
    proof_prompt = "/*[CODE HERE]*/"
    start_line = start
    while start_line > 0 and p[start_line] != '\n':
        if p[start_line].isspace():
            start_line -= 1
        else:
            proof_prompt = '\n' + proof_prompt
            break
    end_line = end
    while end_line < len(p) and p[end_line] != '\n':
        if p[end_line].isspace():
            end_line += 1
        else:
            proof_prompt = proof_prompt + '\n'
            break
    program_prompt = p[:start_line] + proof_prompt + p[end_line:]
    return {
        "id": "example_" + name + "_" + str(i),
        "type": line["type"],
        "program": program_prompt,
        "output": proof_line
    }

def print_stats(stats):
    print(stats)
    with open('data.json', 'w') as f:
        json.dump(stats.get("out", []), f)

if __name__ == "__main__":
    import bench_driver
    bench_driver.run(lemma1, print_stats)
