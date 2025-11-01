# Testing Annotator Recall

The `test_annotator.py` script tests recall on a training set by checking if the expected output appears in the top N completions from the annotator server.

## Prerequisites

Set up the annotation server environment variables:

```bash
export DAFNY_ANNOTATOR_SERVER="http://localhost:8000"
# Optional: for sketch endpoint
export SKETCH_DAFNY_ANNOTATOR_SERVER="http://localhost:8001"
```

Optionally enable modular mode (axiomatize programs before sending to server):

```bash
export VFP_MODULAR="true"
```

## Usage

```bash
# Basic recall@1 test
python test_annotator.py ../../dafny-tasker/vfp_minimized.json

# Recall@5 - check if expected output is in top 5 completions
python test_annotator.py ../../dafny-tasker/vfp_minimized.json --top-n 5

# Recall@10 with verbose output
python test_annotator.py ../../dafny-tasker/vfp_minimized.json --top-n 10 --verbose

# Use different endpoint
python test_annotator.py ../../dafny-tasker/vfp_minimized.json --endpoint greedy_search

# Save detailed report
python test_annotator.py ../../dafny-tasker/vfp_minimized.json --report results.json

# Combine options
python test_annotator.py ../../dafny-tasker/vfp_minimized.json \
  --endpoint annotate \
  --top-n 5 \
  --verbose \
  --report recall_report.json
```

## Options

- `--endpoint`: Server endpoint to use (`annotate`, `greedy_search`, `sketch`) - default: `annotate`
- `--top-n N`: Check if expected output appears in top N completions - default: `1`
- `--verbose`, `-v`: Print detailed results for each task
- `--report FILE`: Write detailed report with failed tasks to JSON file

## Output

```
RECALL@5 TEST RESULTS
==================================================
Total tasks:      150
Correct:          135
Incorrect:        12
Errors:           3
Recall@5:         90.00%
==================================================
```

The detailed report (when `--report` is used) includes:
- Total, correct, incorrect, and error counts
- Overall recall@N percentage
- List of failed tasks with expected output and top N completions from the server

## Input Format

The script accepts JSON or JSONL files with tasks in the following format:

```json
[
  {
    "id": "task_id_1",
    "type": "lemma-call",
    "program": "lemma foo() { /*[CODE HERE]*/ }",
    "output": "bar();"
  },
  ...
]
```

Each task must have:
- `id`: Unique identifier for the task
- `program`: Dafny program with `/*[CODE HERE]*/` marker
- `output`: Expected completion/output
