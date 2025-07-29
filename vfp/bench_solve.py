from pathlib import Path
from driver import drive_program
import mcts
import sketcher

def custom_sorted(fs):
    order = [6, 9, 2, 5, 8, 4]
    order_map = {num: idx for idx, num in enumerate(order)}

    def key(file):
        stem = file.stem  # e.g., "idea-5"
        try:
            num_str = stem.rsplit('-', 1)[1]  # get part after last '-'
            num = int(num_str)
        except (IndexError, ValueError):
            num = None

        return order_map.get(num, float('inf'))  # if not in `order`, go to the end

    return sorted(fs, key=key)

def main(solver):
    for file in custom_sorted(Path('specs').glob('*.dfy')):
        if Path('programs/' + file.name).exists():
            print(f"Skipping {file} because solution already exists")
            continue
        print(f"Solving {file}")
        with open(file, 'r') as f:
            spec = f.read()
        program = solver(spec)
        if program is None:
            print(f"Failed to solve {file}")
            continue
        todo = sketcher.sketch_next_todo(program)
        if todo is not None:
            print(f"Gave up on {file}")
            print(program)
            continue
        print(f"Solved {file}")
        program_file = 'programs/' + file.name
        with open(program_file, 'w') as f:
            f.write(program)

if __name__ == "__main__":
    #main(lambda spec: drive_program(spec, 10))
    main(lambda spec: mcts.main(spec))
