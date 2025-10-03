from llm import default_generate as generate
import driver
import sketcher
import annotator

def lemma1(lemma, p, stats):
    init_p = p # the offsets for insertion are based on original program
    name = lemma['name']
    print('lemma', name)
    x = ""
    xp = driver.insert_program_todo(lemma, init_p, x)
    e = sketcher.list_errors_for_method(xp, name)
    if not e:
        print("empty proof works")
        stats[name] = -1
        return
    x = sketcher.sketch_induction(xp, name)
    p = driver.insert_program_todo(lemma, init_p, x)
    e = sketcher.list_errors_for_method(p, name)
    if not e:
        print("inductive proof sketch works")
        stats[name] = 4
        return
    stats[name] = 0
    lines = init_p.splitlines(keepends=True)
    end_offset = driver.line_col_to_end_offset(p, lines, lemma['endLine'], lemma['endColumn'])
    focused_p = init_p[:end_offset+1]
    focused_p = driver.insert_program_todo(lemma, focused_p, x)
    result_p = annotator.annotate(focused_p)
    if result_p is not None:
        #e = sketcher.show_errors(result_p)
        #if e is None:
        print("annotator over inductive sketch works")
        stats[name] = 1
        return
    if stats[name] == 0:
        print("all failed :(")
        stats['failed_proof_'+name] = x

def print_summary_stats(stats):
    print('total for empty proof works:', len([v for v in stats.values() if isinstance(v, int) and v == -1]))
    print('total for inductive proof sketch works:', len([v for v in stats.values() if isinstance(v, int) and v == 4]))
    print('total for annotator over sketch works:', len([v for v in stats.values() if isinstance(v, int) and v == 1]))
    print('total for unsolved:', len([v for v in stats.values() if isinstance(v, int) and v == 0]))

def print_stats(stats):
    print('FINISHED RUNNING THE BENCH')
    print(stats)
    print_summary_stats(stats)
    print('lemmas')
    for k, v in stats.items():
        if not isinstance(v, int):
            print(k)
            print(v)
    print_summary_stats(stats)

if __name__ == "__main__":
    import bench_driver
    assertions_needed = ["dedupCorrect", "maxIsCorrect", "DequeueCorrect"]
    on_track = assertions_needed
    bench_driver.run(lemma1, print_stats, only_lemmas=on_track)
