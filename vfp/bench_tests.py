import driver
import sketcher
import llm_repair

def try_llm_repair(program, sketch, lemma):
    """Call LLM to repair a failing inductive sketch."""
    repaired = llm_repair.repair(program, sketch, lemma['name'])
    xp = driver.insert_program_todo(lemma, program, repaired)  # use the real lemma dict
    e = sketcher.list_errors_for_method(xp, lemma['name'])
    if not e:
        return True, None, repaired
    else:
        return False, e, repaired

def lemma1(lemma, p, stats):
    name = lemma['name']
    print('lemma', name)
    xp = driver.insert_program_todo(lemma, p, "")
    e = sketcher.list_errors_for_method(xp, name)
    if not e:
        print("empty proof works")
        stats[name] = 0
        return
    ix = sketcher.sketch_induction(xp, name)
    ip = driver.insert_program_todo(lemma, p, ix)
    e = sketcher.list_errors_for_method(ip, name)
    if not e:
        print("inductive proof sketch works")
        stats[name] = 1
        return
    # Strategy 3: inductive sketch + LLM repair
    ok, errs, repaired = try_llm_repair(xp, ix, lemma)
    if ok:
        print("inductive + LLM repair works")
        stats[name] = 2
        
    else:
        print("all failed :(")
        stats[name] = (ix, repaired)

def print_stats(stats):
    print('STATS')
    print(stats)
    for k, v in stats.items():
        if not isinstance(v, int):
            print('--------------------------------')
            print('lemma')
            print(k)
            print('with sketch')
            print(v[0])
            print('with LLM repair')
            print(v[1])
    print('total for empty proof works:', len([v for v in stats.values() if v == 0]))
    print('total for inductive proof sketch works:', len([v for v in stats.values() if v == 1]))
    print('total for inductive + LLM repair works:', len([v for v in stats.values() if v == 2]))
    print('total for errors:', len([v for v in stats.values() if not isinstance(v, int)]))
    print({k:3 if not isinstance(v, int) else v for k,v in stats.items()})

if __name__ == "__main__":
    import bench_driver
    bench_driver.run(lemma1, print_stats)

