import requests
import os

SERVER = os.environ['DAFNY_ANNOTATOR_SERVER']

def greedy_search(program: str):
    url = f"{SERVER}/greedy_search"
    params = {"program": program}
    response = requests.post(url, params=params)
    
    # Raise an error if the server responded with 4xx/5xx
    response.raise_for_status()
    
    return response.json()

if __name__ == "__main__":
    p = """
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
    print(greedy_search(p))