from llm import default_generate as generate
import driver
import sketcher
import os
from fine import format_errors
from driver import prompt_begin_dafny, extract_dafny_program

def prompt_lemma_implementer(program: str, name: str, x: str, e: list[str]) -> str:
    return f'You are implementing a lemma in a Dafny program that is specified but not fully implemented. The current program is\n{program}\n\nThe lemma to implement is {name}. The lemma has an inductive sketch\n{x}\n\nThe inductive sketch is correct, except for missing assertions and helper lemmas. {prompt_begin_dafny("lemma")}\nThe errors in the work-in-progress lemma are:\n{format_errors(e)}\nProvide a the full body of the lemmas, which should be the original inductive sketch plus `assert` and helper lemma calls.'

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
        stats[name] = 0
        return
    prompt = prompt_lemma_implementer(p, name, x, e)
    r = generate(prompt)
    x = extract_dafny_program(r)
    if x is not None:
        p = driver.insert_program_todo(lemma, init_p, x)
        e = sketcher._list_errors_for_method_core(p, name) # no need to use the cached version
        if not e:
            print("LLM repair loop works")
            stats[name] = 1
            stats['proof_'+name] = x
            return
    print("all failed :(")
    stats[name] = 2
    stats['failed_proof_'+name] = x

def print_summary_stats(stats):
    print('total for empty proof works:', len([v for v in stats.values() if isinstance(v, int) and v == -1]))
    print('total for inductive proof sketch works:', len([v for v in stats.values() if isinstance(v, int) and v == 0]))
    print('total for LLM repair loop works:', len([v for v in stats.values() if isinstance(v, int) and v == 1]))
    print('total for unsolved:', len([v for v in stats.values() if isinstance(v, int) and v == 2]))

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
    helper_calls_needed = ["flattenCorrect", "HeapHeightBound", "reverseAppend", "ReverseAppend", "reverse_involutes"]
    both_assertions_and_helper_calls_needed = ["sumDistributive", "reverseReverse", "ReverseReverse", "reverse_append"]
    on_track = assertions_needed + helper_calls_needed + both_assertions_and_helper_calls_needed
    bench_driver.run(lemma1, print_stats, only_lemmas=on_track)
