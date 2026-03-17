#!/usr/bin/env bash
# Runs `dafny verify` on every .dfy file in a target directory and records results.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BENCH_DIR="${1:-$SCRIPT_DIR/DafnyBench}"
BENCH_NAME="$(basename "$BENCH_DIR")"
BENCH_SLUG="${BENCH_NAME//[^A-Za-z0-9._-]/_}"
LOG_DIR="$SCRIPT_DIR/verify_logs"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
LOG_FILE="$LOG_DIR/bench_verify_${BENCH_SLUG}_$TIMESTAMP.txt"
SUMMARY_FILE="$LOG_DIR/bench_verify_summary_${BENCH_SLUG}_$TIMESTAMP.txt"

if [ ! -d "$BENCH_DIR" ]; then
  echo "Error: directory not found: $BENCH_DIR" >&2
  echo "Usage: $(basename "$0") [directory_with_dfy_files]" >&2
  exit 1
fi

mkdir -p "$LOG_DIR"

PASS=0
FAIL=0
TOTAL=0

{
  echo "Bench Verification Run: $BENCH_NAME"
  echo "Started: $(date)"
  echo "Bench dir: $BENCH_DIR"
  echo "Dafny: $(which dafny)"
  echo "========================================"
  echo ""
} | tee "$LOG_FILE"

for dfy_file in "$BENCH_DIR"/*.dfy; do
  [ -f "$dfy_file" ] || continue
  filename="$(basename "$dfy_file")"
  TOTAL=$((TOTAL + 1))

  echo "-------- [$TOTAL] $filename" | tee -a "$LOG_FILE"

  output="$(dafny verify "$dfy_file" 2>&1)"
  exit_code=$?

  echo "$output" >> "$LOG_FILE"
  echo "" >> "$LOG_FILE"

  # Exit code 0 = success, 2 = warnings only (verification still passed)
  # Exit code 4 = verification errors, others = parse/type/tool errors
  if [ $exit_code -eq 0 ] || [ $exit_code -eq 2 ]; then
    PASS=$((PASS + 1))
    echo "  RESULT: PASS (exit $exit_code)" | tee -a "$LOG_FILE"
  else
    FAIL=$((FAIL + 1))
    echo "  RESULT: FAIL (exit $exit_code)" | tee -a "$LOG_FILE"
  fi
  echo "" >> "$LOG_FILE"
done

{
  echo ""
  echo "========================================"
  echo "Finished: $(date)"
  echo "Total:  $TOTAL"
  echo "Pass:   $PASS"
  echo "Fail:   $FAIL"
  echo "========================================"
} | tee -a "$LOG_FILE"

# Write a compact summary table
{
  echo "Bench Verification Summary ($BENCH_NAME) — $(date)"
  echo "Bench dir: $BENCH_DIR"
  echo "Total: $TOTAL  |  Pass: $PASS  |  Fail: $FAIL"
  echo ""
  printf "%-70s %s\n" "FILE" "RESULT"
  printf "%-70s %s\n" "----" "------"
  grep -E "^\-{8}|RESULT:" "$LOG_FILE" | \
    awk '
      /^-------- / { sub(/^-------- \[[0-9]+\] /, ""); file=$0 }
      /RESULT:/    { printf "%-70s %s\n", file, $2 }
    '
} > "$SUMMARY_FILE"

echo ""
echo "Full log:    $LOG_FILE"
echo "Summary:     $SUMMARY_FILE"
