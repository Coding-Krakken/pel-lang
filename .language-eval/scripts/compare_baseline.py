#!/usr/bin/env python3
# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""Compare current scorecard/results against baseline and emit regressions/deltas."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

CATEGORY_SUITE_DEPENDENCIES: dict[str, set[str]] = {
    "correctness_semantics": {"conformance"},
    "security_properties": {"security"},
    "runtime_performance": {"performance"},
    "compiler_toolchain_performance": {"performance"},
    "reliability": {"conformance", "performance"},
    "dx_productivity": {"tooling", "human_factors"},
    "tooling_static_analysis": {"tooling"},
    "interop_integration": {"tooling", "performance"},
    "portability_deployment": {"security", "performance"},
    "concurrency_model": {"performance"},
    "large_codebase_fitness": {"tooling", "performance"},
    "ecosystem_health": {"human_factors", "tooling"},
    "governance_long_term_risk": {"security", "human_factors"},
}


def _load(path: Path) -> dict[str, Any]:
    if path.suffix.lower() in {".yaml", ".yml"}:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_path(path_value: str, target_path: Path) -> Path:
    candidate = Path(path_value)
    if candidate.is_absolute() and candidate.exists():
        return candidate

    for base in (target_path.parent.parent, target_path.parent, Path.cwd()):
        resolved = (base / candidate).resolve()
        if resolved.exists():
            return resolved

    return candidate


def _evaluated_categories(executed_suites: set[str]) -> set[str]:
    evaluated: set[str] = set()
    for category, dependencies in CATEGORY_SUITE_DEPENDENCIES.items():
        if dependencies.issubset(executed_suites):
            evaluated.add(category)
    return evaluated


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True)
    parser.add_argument("--current", required=True, help="Current normalized results JSON")
    parser.add_argument("--scorecard", required=True, help="Current scorecard JSON")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    target_path = Path(args.target)
    target = _load(target_path)
    current = _load(Path(args.current))
    scorecard = _load(Path(args.scorecard))

    baseline_path = _resolve_path(str(target.get("baseline", "")), target_path)
    if not baseline_path.exists():
        raise SystemExit(f"Baseline not found: {baseline_path}")

    baseline = _load(baseline_path)
    tolerance_pct = float(target.get("thresholds", {}).get("regression_tolerance_pct", 0.0))
    allowlist = set(target.get("allowlisted_regressions", []))

    current_scores = scorecard.get("category_scores", {})
    baseline_scores = baseline.get("category_scores", {})
    executed_suites = {
        str(suite.get("name", "")).strip()
        for suite in current.get("suites", [])
        if str(suite.get("name", "")).strip()
    }
    evaluated_categories = _evaluated_categories(executed_suites)

    deltas: dict[str, float] = {}
    regressions: list[dict[str, Any]] = []

    for category, current_value in current_scores.items():
        base_value = float(baseline_scores.get(category, current_value))
        current_value = float(current_value)
        delta = round(current_value - base_value, 6)
        deltas[category] = delta

        if category not in evaluated_categories:
            continue

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
    all_categories_evaluated = set(current_scores.keys()).issubset(evaluated_categories)
    if (
        all_categories_evaluated
        and overall_delta < 0
        and abs(overall_delta) > overall_tol
        and "overall" not in allowlist
    ):
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
        "regression_scope": "full" if all_categories_evaluated else "partial",
        "evaluated_categories": sorted(evaluated_categories),
        "skipped_categories": sorted(set(current_scores.keys()) - evaluated_categories),
        "executed_suites": sorted(executed_suites),
        "deltas": deltas,
        "overall_delta": overall_delta,
        "regressions": regressions,
    }

    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
