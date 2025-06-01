import json
from pathlib import Path
from driver import spec_maker

def generate_specs():
    with open('vermcts.json', 'r') as f:
        data = json.load(f)
    for node in data['nodes']:
        if node['type'] == 'idea':
            if Path(f'specs/{node["id"]}.dfy').exists():
                print(f"Skipping {node['id']} because it already exists")
                continue
            spec = None
            for i in range(3):
                spec = spec_maker(node['content'])
            if spec is None:
                print(f"Failed to generate spec for {node['id']}")
                continue
            print(spec)
            with open(f'specs/{node["id"]}.dfy', 'w') as f:
                f.write(spec + '\n')

if __name__ == "__main__":
    generate_specs()