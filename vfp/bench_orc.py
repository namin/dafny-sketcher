import driver
import sketcher
import orc


def bench_orc(lemma, p, stats):
    name = lemma["name"]
    print("lemma", name)

    # Insert the lemma into the program
    xp = driver.insert_program_todo(lemma, p, "")

    # Check if the empty proof works
    e = sketcher.list_errors_for_method(xp, name)
    if not e:
        print("empty proof works")
        stats[name] = 0
        return

    # Try the ORC solver
    sol = orc.main(xp, max_attempts=50)

    if sol is not None:
        stats[name] = sol
    else:
        stats[name] = -1


def print_summary_stats(stats):
    print("total for empty proof works:", len([v for v in stats.values() if v == 0]))
    print("total for ORC works:", len([v for v in stats.values() if not isinstance(v, int)]))
    print("total for failure:", len([v for v in stats.values() if v == -1]))


def print_stats(stats):
    print_summary_stats(stats)
    for k, v in stats.items():
        if not isinstance(v, int):
            print("ORC solution for", k)
            # Note: prints entire solution, not just lemma
            print(v)
    for k, v in stats.items():
        if v == -1:
            print("ORC solution failed for", k)
    print_summary_stats(stats)


if __name__ == "__main__":
    import bench_driver
    bench_driver.run(bench_orc, print_stats)
