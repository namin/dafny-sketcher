#!/usr/bin/env python3
"""Run the full top-lemma stats pipeline in one command.

Pipeline steps:
1) Collect lemma lengths from DafnyBench.
2) Parse per-lemma stats from log and attach stats to top-K longest lemmas.
3) Summarize and print aggregate outcomes.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


SOLVED_STATUSES = {"empty_seed", "skeleton_seed", "whole_proof_loop", "case_repair"}
LEMMA_LINE_RE = re.compile(r"^\s{2}([^:]+):\s+(.*)$")
MODE_RE = re.compile(r"(empty|skeleton)=\(([^,]+), iter=([^,]+), calls=([^)]+)\)")
LENGTHS_CACHE_PATH = Path(__file__).resolve().parent / "lemma_lengths.json"


def default_cli_dll() -> Path:
    return (
        Path(__file__).resolve().parent.parent / "cli/bin/Release/net8.0/DafnySketcherCli.dll"
    ).resolve()


def run_done_sketch(file_path: Path, cli_dll: Path) -> list[dict[str, Any]]:
    cmd = [
        "dotnet",
        str(cli_dll),
        "--file",
        str(file_path),
        "--sketch",
        "done",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        stdout = (result.stdout or "").strip()
        msg = stderr or stdout or f"exit code {result.returncode}"
        raise RuntimeError(msg)
    text = (result.stdout or "").strip()
    if not text:
        return []
    payload = json.loads(text)
    if not isinstance(payload, list):
        raise RuntimeError(f"Unexpected JSON payload type: {type(payload).__name__}")
    return payload


def extract_lemmas_from_cli(file_path: Path, cli_dll: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    units = run_done_sketch(file_path, cli_dll)
    for unit in units:
        if unit.get("type") != "lemma":
            continue
        name = unit.get("name")
        start_line = unit.get("startLine")
        insert_line = unit.get("insertLine")
        end_line = unit.get("endLine")
        if not isinstance(name, str):
            continue
        if (
            not isinstance(start_line, int)
            or not isinstance(insert_line, int)
            or not isinstance(end_line, int)
        ):
            continue
        if insert_line <= 0:
            length_lines = 0
        else:
            body_start_line = insert_line
            body_end_line = end_line - 1
            length_lines = max(0, body_end_line - body_start_line + 1)
        rows.append(
            {
                "file": str(file_path),
                "lemma_name": name,
                "declaration_start_line": start_line,
                "declaration_end_line": end_line,
                "length_lines": length_lines,
            }
        )
    return rows


def with_unique_names(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: dict[str, int] = {}
    out: list[dict[str, Any]] = []
    for row in rows:
        base = row["lemma_name"]
        seen[base] = seen.get(base, 0) + 1
        count = seen[base]
        unique = base if count == 1 else f"{base}__{count}"
        out.append({"unique_name": unique, "length_lines": row["length_lines"]})
    return out


def collect_lengths(bench_dir: Path, cli_dll: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    failures: list[tuple[str, str]] = []
    for dfy in sorted(bench_dir.rglob("*.dfy")):
        try:
            rows.extend(extract_lemmas_from_cli(dfy, cli_dll))
        except Exception as exc:
            failures.append((str(dfy), str(exc)))
    for file_name, error_text in failures:
        print(f"Warning: failed to process {file_name}: {error_text}", file=sys.stderr)
    return with_unique_names(rows)


def load_lengths_cache(cache_path: Path) -> list[dict[str, Any]] | None:
    if not cache_path.exists():
        return None
    try:
        payload = json.loads(cache_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"Warning: failed to parse cached lengths at {cache_path}: {exc}", file=sys.stderr)
        return None
    if not isinstance(payload, list):
        print(f"Warning: cached lengths at {cache_path} are not a list; recalculating.", file=sys.stderr)
        return None
    return payload


def _parse_int_or_none(text: str) -> int | None:
    text = text.strip()
    if text in {"None", "null", ""}:
        return None
    try:
        return int(text)
    except ValueError:
        return None


def parse_log_per_lemma_stats(log_path: Path) -> dict[str, dict[str, Any]]:
    stats: dict[str, dict[str, Any]] = {}
    in_per_lemma = False

    for raw_line in log_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.rstrip("\n")
        if line.strip() == "--- per-lemma ---":
            in_per_lemma = True
            continue
        if not in_per_lemma:
            continue
        if not line.startswith("  "):
            break

        m = LEMMA_LINE_RE.match(line)
        if not m:
            continue
        lemma_name = m.group(1).strip()
        payload = m.group(2).strip()

        if payload == "skipped":
            stats[lemma_name] = {"skipped": True}
            continue

        row: dict[str, Any] = {"skipped": False}
        for mode, status, iter_text, calls_text in MODE_RE.findall(payload):
            row[f"{mode}_status"] = status.strip()
            row[f"{mode}_iter"] = _parse_int_or_none(iter_text)
            row[f"{mode}_calls"] = _parse_int_or_none(calls_text)
        if row:
            stats[lemma_name] = row

    return stats


def build_top_k_with_stats(
    lengths: list[dict[str, Any]],
    per_lemma_stats: dict[str, dict[str, Any]],
    top_k: int,
) -> list[dict[str, Any]]:
    candidates = [item for item in lengths if item["unique_name"] in per_lemma_stats]

    # Combined pipeline behavior: always apply these two filters.
    candidates = [
        item
        for item in candidates
        if per_lemma_stats[item["unique_name"]].get("empty_iter") != 0
    ]
    candidates = [
        item
        for item in candidates
        if not per_lemma_stats[item["unique_name"]].get("skipped", False)
    ]

    top = sorted(candidates, key=lambda x: (-x["length_lines"], x["unique_name"]))[:top_k]
    out: list[dict[str, Any]] = []

    for item in top:
        name = item["unique_name"]
        row: dict[str, Any] = {
            "unique_name": name,
            "length_lines": item["length_lines"],
            "found_in_log": True,
        }
        row.update(per_lemma_stats[name])
        out.append(row)
    return out


def is_solved(status: Any) -> bool:
    return status in SOLVED_STATUSES


def summarize(rows: list[dict[str, Any]]) -> dict[str, int]:
    total = len(rows)
    skipped = sum(1 for r in rows if r.get("skipped"))
    considered = total - skipped

    empty_solved = 0
    skeleton_solved = 0
    both = 0
    only_empty = 0
    only_skeleton = 0
    neither = 0

    skeleton_faster = 0
    empty_faster = 0
    same_iterations = 0

    for row in rows:
        if row.get("skipped"):
            continue

        empty_ok = is_solved(row.get("empty_status"))
        skeleton_ok = is_solved(row.get("skeleton_status"))

        if empty_ok:
            empty_solved += 1
        if skeleton_ok:
            skeleton_solved += 1

        if empty_ok and skeleton_ok:
            both += 1
            empty_iter = row.get("empty_iter")
            skeleton_iter = row.get("skeleton_iter")
            if isinstance(empty_iter, int) and isinstance(skeleton_iter, int):
                if skeleton_iter < empty_iter:
                    skeleton_faster += 1
                elif empty_iter < skeleton_iter:
                    empty_faster += 1
                else:
                    same_iterations += 1
        elif empty_ok:
            only_empty += 1
        elif skeleton_ok:
            only_skeleton += 1
        else:
            neither += 1

    return {
        "total": total,
        "skipped": skipped,
        "considered": considered,
        "empty_solved": empty_solved,
        "skeleton_solved": skeleton_solved,
        "both_solved": both,
        "only_empty": only_empty,
        "only_skeleton": only_skeleton,
        "neither": neither,
        "skeleton_faster": skeleton_faster,
        "empty_faster": empty_faster,
        "same_iterations": same_iterations,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run collect_lemma_lengths -> top_lemma_stats_from_log -> summarize_top_lemma_stats."
    )

    # Step 1: collection options (retained from collect_lemma_lengths where applicable)
    parser.add_argument(
        "--bench-dir",
        type=Path,
        default=Path("DafnyBench"),
        help="Directory containing .dfy files (default: DafnyBench).",
    )
    parser.add_argument(
        "--cli-dll",
        type=Path,
        default=default_cli_dll(),
        help="Path to DafnySketcherCli.dll.",
    )
    # Step 2: top-lemma options (retained from top_lemma_stats_from_log)
    parser.add_argument(
        "--log-file",
        type=Path,
        default=Path("case_repair_logs/log_gemini_case_repair_paradox.txt"),
        help="Path to log_gemini_case_repair log file.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=30,
        help="Number of longest lemmas to keep.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output JSON file path for top-K lemma stats (default: top{K}_lemma_stats.json).",
    )
    return parser.parse_args()


def print_summary(summary: dict[str, int]) -> None:
    print(f"total lemmas: {summary['total']}")
    print(f"skipped (no case/if structure): {summary['skipped']}")
    print(f"considered: {summary['considered']}")
    print(f"  empty solved: {summary['empty_solved']}")
    print(f"  skeleton solved: {summary['skeleton_solved']}")
    print(f"  both solved: {summary['both_solved']}")
    print(f"  only empty: {summary['only_empty']}")
    print(f"  only skeleton: {summary['only_skeleton']}")
    print(f"  neither: {summary['neither']}")
    print("  among solved-by-both:")
    print(f"    skeleton faster: {summary['skeleton_faster']}")
    print(f"    empty faster: {summary['empty_faster']}")
    print(f"    same iterations: {summary['same_iterations']}")


def main() -> None:
    args = parse_args()
    output_path = args.output or Path(f"top{args.top_k}_lemma_stats.json")

    if not args.cli_dll.exists():
        raise SystemExit(f"CLI DLL not found: {args.cli_dll}")

    print("[stage 1/3] Collecting lemma lengths...")
    cached_lengths = load_lengths_cache(LENGTHS_CACHE_PATH)
    if cached_lengths is not None:
        lengths = cached_lengths
        print(f"Loaded lemma lengths from {LENGTHS_CACHE_PATH}")
    else:
        lengths = collect_lengths(args.bench_dir, args.cli_dll)
        LENGTHS_CACHE_PATH.write_text(json.dumps(lengths, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote lemma lengths to {LENGTHS_CACHE_PATH}")

    print("[stage 2/3] Matching top lemmas with per-lemma log stats...")
    per_lemma_stats = parse_log_per_lemma_stats(args.log_file)
    result = build_top_k_with_stats(
        lengths,
        per_lemma_stats,
        args.top_k,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(result)} top-lemma rows to {output_path}")

    print("[stage 3/3] Summarizing aggregate outcomes...")
    summary = summarize(result)
    print_summary(summary)


if __name__ == "__main__":
    main()
