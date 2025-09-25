import mcts_without_sketchers
import driver
import sketcher

def lemma1(lemma, p, stats):
    name = lemma['name']
    print('lemma', name)
    xp = driver.insert_program_todo(lemma, p, "")
    e = sketcher.list_errors_for_method(xp, name)
    if not e:
        print("empty proof works")
        stats[name] = 0
        return
    sol = mcts_without_sketchers.main(xp, expansion_count=7)
    if sol is not None:
        stats[name] = sol
    else:
        stats[name] = -1

def print_summary_stats(stats):
    print('total for empty proof works:', len([v for v in stats.values() if v == 0]))
    print('total for MCTS works (without sketchers):', len([v for v in stats.values() if not isinstance(v, int)]))
    print('total for failure:', len([v for v in stats.values() if v == -1]))

def print_stats(stats):
    print_summary_stats(stats)
    for k, v in stats.items():
        if not isinstance(v, int):
            print('MCTS solution for', k)
            # Note: this prints the entire solution, not just the lemma
            print(v)
    for k, v in stats.items():
        if v == -1:
            print('MCTS solution failed for', k)
    print_summary_stats(stats)

if __name__ == "__main__":
    import bench_driver
    bench_driver.run(lemma1, print_stats)


