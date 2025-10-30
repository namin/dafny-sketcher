import requests
import os
import argparse
import subprocess
import tempfile
from pathlib import Path

SERVER = os.environ.get('DAFNY_ANNOTATOR_SERVER')
SKETCH_SERVER = os.environ.get('SKETCH_DAFNY_ANNOTATOR_SERVER')
DEBUG_ANNOTATOR = os.environ.get('DEBUG_ANNOTATOR', 'false').lower() != 'false'
VFP_MODULAR = os.environ.get('VFP_MODULAR', 'false').lower() != 'false'

def axiomatize_program(program: str) -> str:
    """Axiomatize a Dafny program using dafny-tasker CLI.
    
    Args:
        program: Dafny program string (should contain CODE_HERE_MARKER)
        
    Returns:
        Axiomatized program string
    """
    # Create temporary input and output files
    with tempfile.NamedTemporaryFile(mode='w', suffix='.dfy', delete=False) as tmp_in:
        tmp_in_path = tmp_in.name
        tmp_in.write(program)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.dfy', delete=False) as tmp_out:
        tmp_out_path = tmp_out.name
    
    try:
        # Call dafny-tasker axiomatize command
        # The lemma will be inferred from CODE_HERE_MARKER location
        cmd = [
            'python', '-m', 'dafny_tasker.cli',
            'axiomatize',
            '--file', tmp_in_path,
            '--out', tmp_out_path
        ]
        
        if DEBUG_ANNOTATOR:
            print(f"Running axiomatize command: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        if DEBUG_ANNOTATOR:
            print(f"Axiomatize stdout: {result.stdout}")
            if result.stderr:
                print(f"Axiomatize stderr: {result.stderr}")
        
        # Read the axiomatized file
        with open(tmp_out_path, 'r') as f:
            axiomatized_content = f.read()
        
        return axiomatized_content
    
    except subprocess.CalledProcessError as e:
        print(f"Error axiomatizing program: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        raise
    finally:
        # Clean up temporary files
        try:
            os.unlink(tmp_in_path)
        except Exception:
            pass
        try:
            os.unlink(tmp_out_path)
        except Exception:
            pass

def endpoint(path: str, program: str, server: str = SERVER):
    # Axiomatize the program if VFP_MODULAR is set
    if VFP_MODULAR:
        if DEBUG_ANNOTATOR:
            print("VFP_MODULAR is set, axiomatizing program")
        program = axiomatize_program(program)
    
    if DEBUG_ANNOTATOR:
        print(f"Annotator request on {path}")
        print(program)
    url = f"{server}/{path}"
    params = {"program": program}
    response = requests.post(url, params=params)
    
    # Raise an error if the server responded with 4xx/5xx
    response.raise_for_status()
    r = response.json()
    if DEBUG_ANNOTATOR:
        print(f"Annotator response: {r}")
    return r

def greedy_search(program: str):
    return endpoint("greedy_search", program)

def annotate(program: str):
    return endpoint("annotate", program)

def sketch(program: str):
    return endpoint("annotate", program, server=SKETCH_SERVER)

def main():
    parser = argparse.ArgumentParser(description='Run greedy search on Dafny programs')
    parser.add_argument('file', nargs='?', help='Dafny file to process')
    parser.add_argument('--program', '-p', help='Dafny program as string (alternative to file)')
    parser.add_argument('--endpoint', '-e', choices=['greedy_search', 'annotate', 'sketch'], help='Endpoint to use', default='annotate')
    
    args = parser.parse_args()
    
    if args.file:
        import tests
        program = tests.read_file(args.file)
    elif args.program:
        program = args.program
    else:
        # Default program if no file or program specified
        program = """
    method SquareRoot(n: nat)
    returns (r: nat)
    ensures r*r <= n <= (r+1)*(r+1)
    {
        r := 0;
        while (r+1)*(r+1) <= n
        {
            r := r + 1;
        }
    }
    """
    
    point = args.endpoint
    if args.endpoint == 'sketch':
        point = 'annotate'
        server = SKETCH_SERVER
    else:
        server = SERVER
    result = endpoint(point, program, server)
    if isinstance(result, list):
        for x in result:
            print(x)
            print('-' * 40)
    else:
        print(result)

if __name__ == "__main__":
    main()
