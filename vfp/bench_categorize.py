import driver
import sketcher
from driver import line_col_to_start_offset, line_col_to_end_offset

def find_closest_lemma_before_offset(p, start_offset):
    # Search backwards from start_offset for "lemma"
    search_text = p[:start_offset]
    
    # Find the last occurrence of "lemma"
    pos = search_text.rfind("lemma")
    
    # Optionally, verify it's a whole word
    if pos != -1:
        if (pos == 0 or not search_text[pos-1].isalnum()) and \
           (pos + 5 >= len(search_text) or not search_text[pos+5].isalnum()):
            return pos
    
    return -1  # No lemma found

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
        lemma_start = find_closest_lemma_before_offset(p, start_offset)
        stats["other"] = stats.get("other", []) + [(name, p[lemma_start:end_offset], ix, e)]

def print_category_summary(category, names):
    print(f'### {category} proofs')
    print(f'{len(names)}: {", ".join([f"`{name}`" for name in names])}')

def print_summary_stats(stats):
    print_category_summary("empty", stats.get("empty", []))
    print_category_summary("induction", stats.get("induction", []))
    print_category_summary("other", [name for name, _, _, _ in stats.get("other", [])])

def print_stats(stats):
    print('FINISHED RUNNING THE BENCH')
    print(stats)
    print_summary_stats(stats)
    print('')
    print('# lemmas to investigate')
    for name, p, ix, e in stats["other"]:
        print(f'## lemma `{name}`')
        print('### working solution')
        print('```dafny')
        print(p)
        print('```')
        print('### failed inductive sketch')
        print('```dafny')
        print(ix)
        print('```')
        print('#### errors')
        for err in e:
            print(f'* {err[2]} -- `{err[3]}`')

    print('## summary')
    print_summary_stats(stats)

if __name__ == "__main__":
    import bench_driver
    bench_driver.run(lemma1, print_stats)