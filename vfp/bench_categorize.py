import driver
import sketcher
from driver import line_col_to_start_offset, line_col_to_end_offset

def lemma1(lemma, p, stats):
    name = lemma['name']
    print('lemma', name)
    xp = driver.insert_program_todo(lemma, p, "")
    e = sketcher.list_errors_for_method(xp, name)
    if not e:
        print("empty proof works")
        stats["empty"] = stats.get("empty", []) + [name]
        return
    ix = sketcher.sketch_induction(xp, name)
    ip = driver.insert_program_todo(lemma, p, ix)
    e = sketcher.list_errors_for_method(ip, name)
    if not e:
        print("inductive proof sketch works")
        stats["induction"] = stats.get("induction", []) + [name]
    else:
        print("inductive proof failed")
        todo = lemma
        lines = p.splitlines(keepends=True)
        start_offset = line_col_to_start_offset(p,lines, todo['insertLine'], todo['insertColumn'])
        end_offset = line_col_to_end_offset(p, lines, todo['endLine'], todo['endColumn'])
        stats["other"] = stats.get("other", []) + [(name, p[start_offset:end_offset])]

def print_category_summary(category, names):
    print(f'### {category} proofs')
    print(f'{len(names)}: {", ".join([f"`{name}`" for name in names])}')

def print_summary_stats(stats):
    print_category_summary("empty", stats.get("empty", []))
    print_category_summary("induction", stats.get("induction", []))
    print_category_summary("other", [name for name, _ in stats.get("other", [])])

def print_stats(stats):
    print('FINISHED RUNNING THE BENCH')
    print(stats)
    print_summary_stats(stats)
    print('')
    print('# lemmas to investigate')
    for name, p in stats["other"]:
        print(f'## lemma `{name}`')
        print('```dafny')
        print(p)
        print('```')
    print('## summary')
    print_summary_stats(stats)

if __name__ == "__main__":
    import bench_driver
    bench_driver.run(lemma1, print_stats)