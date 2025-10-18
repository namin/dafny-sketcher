from llm import default_generate as generate
import sketcher

def lemma1(lemma, p, stats):
    name = lemma['name']
    stats[name] = []
    lines = sketcher.sketch_proof_lines(p, name)
    for line in lines:
        stats[name].append(line)
    print("Added", len(lines), "proof lines for", name)

def print_stats(stats):
    print(stats)

if __name__ == "__main__":
    import bench_driver
    bench_driver.run(lemma1, print_stats)
