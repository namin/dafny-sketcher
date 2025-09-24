import driver
import sketcher


def bench_orc(lemma, p, stats, max_attempts: int = 3):
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

    # Try dispatch_implementer a few times
    sol = None
    
    for attempt in range(1, max_attempts + 1):
        print(f"attempt {attempt} for {name}")
        sol = driver.dispatch_implementer(p, lemma, done=[])
        if sol is not None:
            print("driver produced a solution:")
            print(sol)  # print the actual solution text
            stats[name] = sol
            return

    # If all attempts fail
    print("all attempts failed")
    stats[name] = -1


def print_summary_stats(stats):
    print("total for empty proof works:", len([v for v in stats.values() if v == 0]))
    print("total for driver works:", len([v for v in stats.values() if not isinstance(v, int)]))
    print("total for failure:", len([v for v in stats.values() if v == -1]))


def print_stats(stats):
    print_summary_stats(stats)
    for k, v in stats.items():
        if not isinstance(v, int):
            print("driver solution for", k)
            # Note: prints entire solution, not just lemma
            print(v)
    for k, v in stats.items():
        if v == -1:
            print("driver solution failed for", k)
    print_summary_stats(stats)


if __name__ == "__main__":
    import bench_driver
    bench_driver.run(bench_orc, print_stats)
