from pathlib import Path
from driver import drive_program

def main(solver):
    for file in sorted(Path('specs').glob('*.dfy')):
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
        print(f"Solved {file}")
        program_file = 'programs/' + file.name
        with open(program_file, 'w') as f:
            f.write(program)

if __name__ == "__main__":
    solver(lambda spec: drive_program(spec, 10))
