#!/usr/bin/env python3
"""Compare current scorecard/results against baseline and emit regressions/deltas."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml


def _load(path: Path) -> dict[str, Any]:
    if path.suffix.lower() in {".yaml", ".yml"}:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True)
    parser.add_argument("--current", required=True, help="Current normalized results JSON")
    parser.add_argument("--scorecard", required=True, help="Current scorecard JSON")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    target = _load(Path(args.target))
    _ = _load(Path(args.current))
    scorecard = _load(Path(args.scorecard))

    baseline_path = Path(target.get("baseline", ""))
    if not baseline_path.exists():
        payload = {
            "baseline": str(baseline_path),
            "baseline_found": False,
            "deltas": {},
            "regressions": [],
        }
        Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"Baseline not found: {baseline_path} (non-fatal)")
        print(f"Wrote {args.out}")
        return 0

    baseline = _load(baseline_path)
    tolerance_pct = float(target.get("thresholds", {}).get("regression_tolerance_pct", 0.0))
    allowlist = set(target.get("allowlisted_regressions", []))

    current_scores = scorecard.get("category_scores", {})
    baseline_scores = baseline.get("category_scores", {})

    deltas: dict[str, float] = {}
    regressions: list[dict[str, Any]] = []

    for category, current_value in current_scores.items():
        base_value = float(baseline_scores.get(category, current_value))
        current_value = float(current_value)
        delta = round(current_value - base_value, 6)
        deltas[category] = delta

        tolerance_abs = abs(base_value) * (tolerance_pct / 100.0)
        allowed_key = f"category:{category}"
        if delta < 0 and abs(delta) > tolerance_abs and allowed_key not in allowlist:
            regressions.append(
                {
                    "id": allowed_key,
                    "baseline": base_value,
                    "current": current_value,
                    "delta": delta,
                    "tolerance_abs": round(tolerance_abs, 6),
                }
            )

    overall_baseline = float(baseline.get("overall_score", scorecard.get("overall_score", 0.0)))
    overall_current = float(scorecard.get("overall_score", 0.0))
    overall_delta = round(overall_current - overall_baseline, 6)
    overall_tol = abs(overall_baseline) * (tolerance_pct / 100.0)
    if overall_delta < 0 and abs(overall_delta) > overall_tol and "overall" not in allowlist:
        regressions.append(
            {
                "id": "overall",
                "baseline": overall_baseline,
                "current": overall_current,
                "delta": overall_delta,
                "tolerance_abs": round(overall_tol, 6),
            }
        )

    payload = {
        "baseline": str(baseline_path),
        "baseline_found": True,
        "deltas": deltas,
        "overall_delta": overall_delta,
        "regressions": regressions,
    }

    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
