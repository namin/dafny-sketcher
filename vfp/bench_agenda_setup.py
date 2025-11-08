"""
Setup agendas for benchmark using agenda-based scheduling.

Creates one agenda per lemma, ready to be executed by the scheduler.

Configuration:
    Set AGENDA_SYSTEM_PATH environment variable to point to the agenda-based
    scheduling system directory.
"""

import driver
import os
import pathlib
import sys
import asyncio

# Path to agenda system
if 'AGENDA_SYSTEM_PATH' in os.environ:
    AGENDA_SYSTEM_PATH = pathlib.Path(os.environ['AGENDA_SYSTEM_PATH'])
else:
    print("Error: AGENDA_SYSTEM_PATH environment variable not set")
    sys.exit(1)

sys.path.insert(0, str(AGENDA_SYSTEM_PATH))

from agenda import LocalAgenda, Object, Task

# Global state to share between bench_driver callbacks
SHARED_STATE = {}


async def setup_lemma_agenda(lemma, p, output_dir):
    """
    Create an agenda for a single lemma.

    Args:
        lemma: dict with lemma metadata (name, insertLine, etc.)
        p: the full program source as a string
        output_dir: Path to directory where agenda checkpoints will be created

    Returns:
        Path to the created checkpoint
    """
    name = lemma['name']
    print(f'Setting up agenda for lemma: {name}')

    # Create a version of the program with empty lemma body
    x = ""  # empty body
    xp = driver.insert_program_todo(lemma, p, x)

    # Create agenda directory for this lemma
    agenda_dir = output_dir / name
    agenda_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = agenda_dir / "checkpoint.pkl"

    # Initialize agenda
    agenda = LocalAgenda(checkpoint_path=str(checkpoint_path))

    # Create object with the Dafny program
    obj = Object(
        path=f"{name}.dfy",
        type="dafny-program",
        parents=[],
        content=xp.encode('utf-8'),
        properties={
            "description": f"Lemma {name} from VFP benchmark",
            "lemma_name": name
        }
    )
    obj_path = await agenda.create_object(obj)

    # Create a single generic lemma solving task
    # The scheduler decides which solving strategy to use
    task = Task(
        id=f"solve-{name}",
        type="lemma_solve",
        properties={
            "dfy_path": obj_path,
            "lemma_name": name
        }
    )
    await agenda.add_task(task)

    print(f'  Created agenda at: {checkpoint_path}')
    return checkpoint_path


def lemma1(lemma, p, stats):
    """
    Callback for bench_driver - sets up one lemma agenda.
    """
    # Get shared state from global (bench_driver uses stats dict)
    if 'output_dir' not in stats:
        stats['output_dir'] = SHARED_STATE['output_dir']
    if 'agendas' not in stats:
        stats['agendas'] = []

    output_dir = stats['output_dir']

    try:
        checkpoint_path = asyncio.run(setup_lemma_agenda(lemma, p, output_dir))
        stats['agendas'].append(checkpoint_path)
    except Exception as e:
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()


def print_stats(stats):
    """Print summary of created agendas."""
    agendas = stats.get('agendas', [])
    print(f'\n{"="*80}')
    print(f'SETUP COMPLETE')
    print(f'{"="*80}')
    print(f'Created {len(agendas)} agenda(s)')
    print(f'Output directory: {stats["output_dir"]}')
    print(f'\nTo run a single lemma:')
    print(f'  cd {AGENDA_SYSTEM_PATH}')
    print(f'  python scheduler.py +agenda=local \\')
    print(f'    agenda.checkpoint_path=<checkpoint_path> \\')
    print(f'    +scheduler=poetry llm=aws')
    print(f'\nTo run all lemmas:')
    print(f'  cd {AGENDA_SYSTEM_PATH}')
    print(f'  python poetry/bench_agenda_run.py {stats["output_dir"]}')
    print(f'{"="*80}\n')


if __name__ == "__main__":
    import bench_driver
    import argparse

    # Check if agenda system exists
    if not AGENDA_SYSTEM_PATH.exists():
        print(f"Error: Agenda system not found at {AGENDA_SYSTEM_PATH}")
        print("Please set AGENDA_SYSTEM_PATH environment variable or adjust the path in this script")
        sys.exit(1)

    # Parse output directory argument (in addition to bench_driver args)
    parser = argparse.ArgumentParser(description='Setup agendas for lemma solving')
    parser.add_argument('--output-dir', type=str, default='bench_agendas',
                        help='Directory to store agenda checkpoints (default: bench_agendas)')

    # Parse our args first, then let bench_driver parse the rest
    args, remaining = parser.parse_known_args()
    sys.argv = [sys.argv[0]] + remaining

    output_dir = pathlib.Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Use global to share state (bench_driver passes different dict to each call)
    SHARED_STATE['output_dir'] = output_dir

    print(f"Using agenda system at: {AGENDA_SYSTEM_PATH}")
    print(f"Output directory: {output_dir}\n")

    bench_driver.run(lemma1, print_stats)
