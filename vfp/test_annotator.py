#!/usr/bin/env python3
"""Test recall on a training set using the annotator server."""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any
from tqdm import tqdm
import annotator


def load_tasks(input_path: Path) -> List[Dict[str, Any]]:
    """Load tasks from JSON or JSONL file."""
    with input_path.open('r', encoding='utf-8') as f:
        content = f.read()
        try:
            # Try JSON list first
            tasks = json.loads(content)
        except json.JSONDecodeError:
            # Try JSONL
            tasks = []
            for line in content.splitlines():
                if line.strip():
                    tasks.append(json.loads(line))
    return tasks


def normalize_output(output: str) -> str:
    """Normalize output for comparison (strip whitespace, etc.)."""
    return output.strip()


def check_in_top_n(expected: str, completions: List[str], n: int) -> bool:
    """Check if expected output appears in the top N completions."""
    expected_norm = normalize_output(expected)

    for i, completion in enumerate(completions[:n]):
        if expected_norm == normalize_output(completion):
            return True

    return False


def test_recall(
    tasks: List[Dict[str, Any]],
    endpoint_name: str = "annotate",
    top_n: int = 1,
    verbose: bool = False
) -> Dict[str, Any]:
    """
    Test recall on a set of tasks.

    Args:
        tasks: List of task dictionaries with 'program' and 'output' fields
        endpoint_name: Endpoint to use ('annotate', 'greedy_search', 'sketch')
        top_n: Check if expected output is in top N completions
        verbose: Print detailed results for each task

    Returns:
        Dictionary with recall metrics
    """
    results = {
        "total": len(tasks),
        "correct": 0,
        "incorrect": 0,
        "errors": 0,
        "recall": 0.0,
        "top_n": top_n,
        "failed_tasks": []
    }

    for task in tqdm(tasks, desc=f"Testing recall@{top_n}", unit="task"):
        task_id = task.get('id', 'unknown')
        program = task.get('program', '')
        expected_output = task.get('output', '')

        if not program:
            tqdm.write(f"[warn] task {task_id} has no program, skipping")
            results["errors"] += 1
            continue

        try:
            # Query the server
            if endpoint_name == "annotate":
                response = annotator.annotate(program)
            elif endpoint_name == "greedy_search":
                response = annotator.greedy_search(program)
            elif endpoint_name == "sketch":
                response = annotator.sketch(program)
            else:
                raise ValueError(f"Unknown endpoint: {endpoint_name}")

            # Convert response to list of completions
            if isinstance(response, list):
                completions = [str(item) for item in response]
            else:
                completions = [str(response)]

            # Check if expected output is in top N
            found = check_in_top_n(expected_output, completions, top_n)

            if found:
                results["correct"] += 1
                if verbose:
                    tqdm.write(f"[✓] {task_id}")
            else:
                results["incorrect"] += 1
                results["failed_tasks"].append({
                    "id": task_id,
                    "expected": expected_output,
                    "top_completions": completions[:top_n]
                })
                if verbose:
                    tqdm.write(f"[✗] {task_id}")
                    tqdm.write(f"    Expected: {expected_output}")
                    tqdm.write(f"    Top {top_n}: {completions[:top_n]}")

        except Exception as e:
            results["errors"] += 1
            results["failed_tasks"].append({
                "id": task_id,
                "error": str(e)
            })
            if verbose:
                tqdm.write(f"[ERROR] {task_id}: {e}")

    # Calculate recall
    if results["total"] > 0:
        results["recall"] = results["correct"] / results["total"]

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Test recall on a training set using the annotator server"
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Input JSON/JSONL file with tasks"
    )
    parser.add_argument(
        "--endpoint",
        type=str,
        default="annotate",
        choices=["annotate", "greedy_search", "sketch"],
        help="Endpoint to use (default: annotate)"
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=1,
        help="Check if expected output is in top N completions (default: 1)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print detailed results for each task"
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="Write detailed report to JSON file"
    )

    args = parser.parse_args()

    # Load tasks
    if not args.input.exists():
        print(f"error: input file not found: {args.input}", file=sys.stderr)
        return 2

    print(f"Loading tasks from {args.input}...")
    tasks = load_tasks(args.input)
    print(f"Loaded {len(tasks)} tasks")

    # Test recall
    print(f"Testing recall@{args.top_n} using endpoint: {args.endpoint}")
    results = test_recall(
        tasks,
        endpoint_name=args.endpoint,
        top_n=args.top_n,
        verbose=args.verbose
    )

    # Print summary
    print("\n" + "="*60)
    print(f"RECALL@{args.top_n} TEST RESULTS")
    print("="*60)
    print(f"Total tasks:      {results['total']}")
    print(f"Correct:          {results['correct']}")
    print(f"Incorrect:        {results['incorrect']}")
    print(f"Errors:           {results['errors']}")
    print(f"Recall@{args.top_n}:        {results['recall']:.2%}")
    print("="*60)

    # Write report if requested
    if args.report:
        with args.report.open('w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\nDetailed report written to {args.report}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
