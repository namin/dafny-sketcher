import driver
import sketcher
import tests
import llm_repair


def try_llm_generate(program, lemma):
    """Call LLM to generate a full proof from scratch."""
    generated = llm_repair.generate_proof(program, lemma)
    xp = driver.insert_program_todo(lemma, program, generated)
    e = sketcher.list_errors_for_method(xp, lemma['name'])
    if not e:
        return True, None, generated
    else:
        return False, e, generated


def lemma1(lemma, program, stats):
    name = lemma['name']
    print(f"lemma {name}")

    ok, errs, proof = try_llm_generate(program, lemma)
    if ok:
        print(":) :) :) LLM generation works")
        stats[name] = {"status": "success", "proof": proof}
    else:
        print(":( :( :( LLM generation failed")
        stats[name] = {"status": "error", "errors": errs, "proof": proof}


def print_stats(stats):
    # Summary
    total_ok = sum(1 for v in stats.values() if v["status"] == "success")
    total_err = sum(1 for v in stats.values() if v["status"] == "error")

    print("\n=== Summary ===")
    print("total lemmas:", len(stats))
    print("successful proofs:", total_ok)
    print("failed proofs:", total_err)

    # Print failing cases
    for name, result in stats.items():
        if result["status"] == "error":
            print(f"\nLemma {name} failed:")
            print("Generated proof:")
            print(result["proof"])
            print("Errors:")
            print(result["errors"])
    
    # end on summary repeat
    print("\n=== Summary ===")
    print("total lemmas:", len(stats))
    print("successful proofs:", total_ok)
    print("failed proofs:", total_err)


if __name__ == "__main__":
    import bench_driver
    bench_driver.run(lemma1, print_stats)
