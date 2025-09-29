from llm import default_generate as generate
import driver
import sketcher
import os
from fine import format_errors
from driver import prompt_begin_dafny, extract_dafny_program

USE_SKETCHERS = os.environ.get('USE_SKETCHERS', 'true').lower() != 'false'

def prompt_lemma_implementer(program: str, name: str, e: list[str]) -> str:
    return f'You are implementing a lemma in a Dafny program that is specified but not fully implemented. The current program is\n{program}\n\nThe lemma to implement is {name}. {prompt_begin_dafny("lemma")}\nThe errors in the work-in-progress lemma are:\n{format_errors(e)}'

def lemma1(lemma, p, stats):
    name = lemma['name']
    print('lemma', name)
    x = ""
    init_p = driver.insert_program_todo(lemma, p, x)
    xp = init_p
    e = sketcher.list_errors_for_method(xp, name)
    if not e:
        print("empty proof works")
        stats[name] = -1
        return
    if USE_SKETCHERS:
        ix = sketcher.sketch_induction(xp, name)
        p = driver.insert_program_todo(lemma, init_p, ix)
        e = sketcher.list_errors_for_method(p, name)
        if not e:
            print("inductive proof sketch works")
            stats[name] = 0
            return
    else:
        print('Not using sketchers!')
    for i in range(3):
        prompt = prompt_lemma_implementer(p, name, e)
        r = generate(prompt)
        x = extract_dafny_program(r)
        if x is None:
            continue
        # TODO: maybe consider starting from initial point if program can be judged too bad
        p = driver.insert_program_todo(lemma, init_p, x)
        e = sketcher.list_errors_for_method(p, name)
        if not e:
            print("LLM repair loop works " + str(i))
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
    bench_driver.run(lemma1, print_stats)