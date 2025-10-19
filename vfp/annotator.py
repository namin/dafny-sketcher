import requests
import os
import argparse

SERVER = os.environ['DAFNY_ANNOTATOR_SERVER']
DEBUG_ANNOTATOR = os.environ.get('DEBUG_ANNOTATOR', 'false').lower() != 'false'

def endpoint(path: str, program: str):
    if DEBUG_ANNOTATOR:
        print(f"Annotator request on {path}")
        print(program)
    url = f"{SERVER}/{path}"
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

def main():
    parser = argparse.ArgumentParser(description='Run greedy search on Dafny programs')
    parser.add_argument('file', nargs='?', help='Dafny file to process')
    parser.add_argument('--program', '-p', help='Dafny program as string (alternative to file)')
    parser.add_argument('--endpoint', '-e', choices=['greedy_search', 'annotate'], help='Endpoint to use', default='greedy_search')
    
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
    
    result = endpoint(args.endpoint, program)
    print(result)

if __name__ == "__main__":
    main()