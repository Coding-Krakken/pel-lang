#!/usr/bin/env bash
# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

set -euo pipefail

usage() {
  cat <<'EOF'
Usage: run_all.sh --target <target.yaml> [--outdir <dir>] [--repeat N] [--warmup N] [--timeout N] [--jobs N] [--fast]

Runs all enabled suites for a target, normalizes results, computes scorecard,
and emits markdown/json reports under .language-eval/reports/<timestamp>/.

Options:
  --target   Path to target config YAML/JSON
  --outdir   Explicit output directory (default: .language-eval/reports/<timestamp>)
  --repeat   Repetitions for performance-like suites (default: 5)
  --warmup   Warmup iterations (default: 1)
  --timeout  Per-suite timeout in seconds (default: 600, 0 = no timeout)
  --jobs     Number of parallel suite jobs (default: 1 = sequential)
  --fast     Run fast subset only (conformance, security, tooling)
  -h, --help Show this help
EOF
}

TARGET=""
OUTDIR=""
REPEAT=5
WARMUP=1
TIMEOUT=600
JOBS=1
FAST=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target)
      TARGET="$2"; shift 2 ;;
    --outdir)
      OUTDIR="$2"; shift 2 ;;
    --repeat)
      REPEAT="$2"; shift 2 ;;
    --warmup)
      WARMUP="$2"; shift 2 ;;
    --timeout)
      TIMEOUT="$2"; shift 2 ;;
    --jobs)
      JOBS="$2"; shift 2 ;;
    --fast)
      FAST=1; shift ;;
    -h|--help)
      usage; exit 0 ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 2 ;;
  esac
done

if [[ -z "$TARGET" ]]; then
  echo "Missing required --target argument." >&2
  usage
  exit 2
fi

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TIMESTAMP="${LANG_EVAL_TIMESTAMP:-$(date -u +%Y%m%dT%H%M%SZ)}"

if [[ -z "$OUTDIR" ]]; then
  OUTDIR="$ROOT/reports/$TIMESTAMP"
fi
mkdir -p "$OUTDIR"

SUITES=$(python - "$TARGET" "$FAST" <<'PY'
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError as exc:
    raise SystemExit("PyYAML is required to parse target config") from exc

target = Path(sys.argv[1])
fast = sys.argv[2] == "1"
if target.suffix.lower() in {".yaml", ".yml"}:
    data = yaml.safe_load(target.read_text(encoding="utf-8"))
else:
    data = json.loads(target.read_text(encoding="utf-8"))

enabled = data.get("enabled_suites", [])
if fast:
    fast_set = {"conformance", "security", "tooling"}
    enabled = [suite for suite in enabled if suite in fast_set]
print("\n".join(enabled))
PY
)

# Normalize suite list (remove carriage returns that might come from Windows)
SUITES=$(echo "$SUITES" | tr -d '\r')

if [[ -z "$SUITES" ]]; then
  echo "No suites selected for execution." >&2
  exit 3
fi

echo "Running suites into: $OUTDIR"
echo "Configuration: repeat=$REPEAT, warmup=$WARMUP, timeout=${TIMEOUT}s, jobs=$JOBS"

# Run suites in parallel if jobs > 1
pids=()
active_jobs=0

for suite in $SUITES; do
  # Wait if we've hit the parallel job limit
  while [[ $active_jobs -ge $JOBS ]]; do
    # Wait for any job to complete
    wait -n 2>/dev/null || true
    active_jobs=$((active_jobs - 1))
  done
  
  # Launch suite in background if parallel, foreground if sequential
  if [[ $JOBS -gt 1 ]]; then
    "$ROOT/scripts/run_suite.sh" \
      --target "$TARGET" \
      --suite "$suite" \
      --outdir "$OUTDIR" \
      --repeat "$REPEAT" \
      --warmup "$WARMUP" \
      --timeout "$TIMEOUT" &
    pids+=($!)
    active_jobs=$((active_jobs + 1))
  else
    "$ROOT/scripts/run_suite.sh" \
      --target "$TARGET" \
      --suite "$suite" \
      --outdir "$OUTDIR" \
      --repeat "$REPEAT" \
      --warmup "$WARMUP" \
      --timeout "$TIMEOUT"
  fi
done

# Wait for all background jobs to complete
if [[ ${#pids[@]} -gt 0 ]]; then
  wait "${pids[@]}"
fi

python "$ROOT/scripts/normalize_results.py" \
  --target "$TARGET" \
  --suite-dir "$OUTDIR" \
  --raw-out "$OUTDIR/results.raw.json" \
  --normalized-out "$OUTDIR/results.normalized.json"

python "$ROOT/scripts/scorecard.py" \
  --target "$TARGET" \
  --normalized "$OUTDIR/results.normalized.json" \
  --weights "$ROOT/WEIGHTS.default.json" \
  --out "$OUTDIR/scorecard.json"

python "$ROOT/scripts/compare_baseline.py" \
  --target "$TARGET" \
  --current "$OUTDIR/results.normalized.json" \
  --scorecard "$OUTDIR/scorecard.json" \
  --out "$OUTDIR/comparison.json"

python "$ROOT/scripts/emit_report.py" \
  --target "$TARGET" \
  --normalized "$OUTDIR/results.normalized.json" \
  --scorecard "$OUTDIR/scorecard.json" \
  --comparison "$OUTDIR/comparison.json" \
  --outdir "$OUTDIR"

echo "Completed language evaluation. Artifacts in: $OUTDIR"
