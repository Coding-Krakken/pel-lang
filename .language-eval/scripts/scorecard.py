#!/usr/bin/env python3
# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""Compute weighted category and overall scorecard from normalized results."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml


def _load(path: Path) -> dict[str, Any]:
    try:
        if path.suffix.lower() in {".yaml", ".yml"}:
            return yaml.safe_load(path.read_text(encoding="utf-8"))
        return json.loads(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise SystemExit(f"Invalid YAML in {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc
    except FileNotFoundError as exc:
        raise SystemExit(f"File not found: {path}") from exc


def _resolve_weights(root: Path, weights_file: Path, target: dict[str, Any]) -> dict[str, float]:
    weight_profile = target.get("weight_profile", "default")
    default_data = _load(weights_file)

    if weight_profile == "default":
        selected = default_data["profiles"]["default"]
    else:
        references = default_data.get("profile_references", {})
        profile_path = references.get(weight_profile)
        if not profile_path:
            raise SystemExit(f"Unknown weight profile: {weight_profile}")
        selected = _load(root / profile_path)["weights"]

    overrides = target.get("weight_overrides", {})
    resolved = {**selected, **overrides}

    total = sum(float(value) for value in resolved.values())
    if abs(total - 1.0) > 1e-6:
        raise SystemExit(f"Weight sum must equal 1.0 (got {total:.6f})")

    return {key: float(value) for key, value in resolved.items()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True)
    parser.add_argument("--normalized", required=True)
    parser.add_argument("--weights", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    target_path = Path(args.target)
    normalized_path = Path(args.normalized)
    weights_path = Path(args.weights)
    out_path = Path(args.out)
    root = weights_path.parent

    target = _load(target_path)
    normalized = _load(normalized_path)

    weights = _resolve_weights(root, weights_path, target)
    category_inputs = normalized["metrics"]["category_inputs"]

    category_scores: dict[str, float] = {}
    for category, _weight in weights.items():
        score = float(category_inputs.get(category, 0.0))
        category_scores[category] = round(score, 4)

    overall = 0.0
    for category, weight in weights.items():
        overall += category_scores[category] * weight

    suite_scores: dict[str, float] = {}
    for suite in normalized.get("suites", []):
        metrics = suite.get("metrics", {})
        if suite["name"] == "conformance":
            suite_scores["conformance"] = round(float(metrics.get("pass_rate", 0.0)) * 5.0, 4)
        elif suite["name"] == "security":
            suite_scores["security"] = round(float(metrics.get("policy_pass_rate", 0.0)) * 5.0, 4)
        elif suite["name"] == "performance":
            p95 = float(metrics.get("latency_ms", {}).get("p95", 500.0))
            suite_scores["performance"] = round(max(0.0, min(5.0, 5.0 - p95 / 60.0)), 4)
        elif suite["name"] == "tooling":
            idem = float(metrics.get("formatter_idempotence_rate", 0.0))
            lsp_ok = float(metrics.get("lsp_correctness_rate", 0.0))
            suite_scores["tooling"] = round((idem + lsp_ok) * 2.5, 4)
        elif suite["name"] == "human_factors":
            suite_scores["human_factors"] = round(
                float(metrics.get("checklist_coverage", 0.0)) * 5.0, 4
            )

    payload = {
        "target_id": normalized.get("target_id", target.get("target_id", "unknown")),
        "overall_score": round(overall, 4),
        "weights": weights,
        "category_scores": category_scores,
        "suite_scores": suite_scores,
    }

    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
