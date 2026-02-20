#!/usr/bin/env python3
# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""Normalize suite-specific outputs into canonical results schema."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

SUITE_GLOB = "suite.*.json"


def _load_target(path: Path) -> dict[str, Any]:
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


def _clamp_score(value: float) -> float:
    return max(0.0, min(5.0, round(value, 4)))


def _suite_to_category_inputs(suite_results: list[dict[str, Any]]) -> dict[str, float]:
    category = {
        "correctness_semantics": 2.5,
        "security_properties": 2.5,
        "runtime_performance": 2.5,
        "compiler_toolchain_performance": 2.5,
        "reliability": 2.5,
        "dx_productivity": 2.5,
        "tooling_static_analysis": 2.5,
        "interop_integration": 2.5,
        "portability_deployment": 2.5,
        "concurrency_model": 2.5,
        "large_codebase_fitness": 2.5,
        "ecosystem_health": 2.5,
        "governance_long_term_risk": 2.5,
    }

    by_name = {entry.get("suite"): entry for entry in suite_results}

    conformance = by_name.get("conformance", {}).get("metrics", {})
    if "pass_rate" in conformance:
        category["correctness_semantics"] = _clamp_score(float(conformance["pass_rate"]) * 5.0)
        category["reliability"] = _clamp_score(float(conformance["pass_rate"]) * 4.8)

    security = by_name.get("security", {}).get("metrics", {})
    if "policy_pass_rate" in security:
        base = float(security["policy_pass_rate"]) * 5.0
        penalty = float(security.get("critical_findings", 0)) * 1.0 + float(
            security.get("high_findings", 0)
        ) * 0.2
        category["security_properties"] = _clamp_score(base - penalty)

    performance = by_name.get("performance", {}).get("metrics", {})
    if "throughput_ops_per_sec" in performance:
        throughput = float(performance["throughput_ops_per_sec"])
        p95 = float(performance.get("latency_ms", {}).get("p95", 200.0))
        rss = float(performance.get("rss_mb", 1024.0))
        perf_score = min(5.0, 1.5 + (throughput / 2000.0) * 2.0 + max(0.0, (120.0 - p95) / 120.0))
        footprint_penalty = max(0.0, (rss - 256.0) / 256.0)
        category["runtime_performance"] = _clamp_score(perf_score - footprint_penalty)
        category["compiler_toolchain_performance"] = _clamp_score(perf_score - 0.4)

    tooling = by_name.get("tooling", {}).get("metrics", {})
    if tooling:
        idem = float(tooling.get("formatter_idempotence_rate", 0.0))
        lsp_p95 = float(tooling.get("lsp_p95_ms", 300.0))
        lsp_ok = float(tooling.get("lsp_correctness_rate", 0.0))
        lint_fp = float(tooling.get("linter_false_positive_rate", 1.0))
        tooling_score = idem * 2.0 + lsp_ok * 2.0 + max(0.0, (250.0 - lsp_p95) / 250.0) - lint_fp
        category["tooling_static_analysis"] = _clamp_score(tooling_score)
        category["dx_productivity"] = _clamp_score((idem * 5.0 + lsp_ok * 5.0) / 2.0)

    human = by_name.get("human_factors", {}).get("metrics", {})
    if human:
        coverage = float(human.get("checklist_coverage", 0.0))
        category["dx_productivity"] = _clamp_score((category["dx_productivity"] + coverage * 5.0) / 2.0)

    category["interop_integration"] = _clamp_score((category["tooling_static_analysis"] + 2.7) / 2.0)
    category["portability_deployment"] = _clamp_score((category["security_properties"] + 2.6) / 2.0)
    category["concurrency_model"] = _clamp_score((category["runtime_performance"] + 2.4) / 2.0)
    category["large_codebase_fitness"] = _clamp_score(
        (category["compiler_toolchain_performance"] + category["tooling_static_analysis"]) / 2.0
    )
    category["ecosystem_health"] = _clamp_score((category["dx_productivity"] + 2.8) / 2.0)
    category["governance_long_term_risk"] = _clamp_score((category["security_properties"] + 2.9) / 2.0)

    return category


def build_normalized(target: dict[str, Any], suite_results: list[dict[str, Any]], timestamp: str) -> dict[str, Any]:
    category_inputs = _suite_to_category_inputs(suite_results)
    suites = []
    for suite in sorted(suite_results, key=lambda entry: entry.get("suite", "")):
        suites.append(
            {
                "name": suite.get("suite"),
                "status": suite.get("status", "fail"),
                "metrics": suite.get("metrics", {}),
                "artifacts": suite.get("artifacts", {}),
            }
        )
    return {
        "target_id": target.get("target_id", "unknown"),
        "timestamp": timestamp,
        "suites": suites,
        "metrics": {
            "category_inputs": category_inputs,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, help="Path to target yaml/json")
    parser.add_argument("--suite-dir", required=True, help="Directory containing suite.*.json")
    parser.add_argument("--raw-out", required=True, help="Output path for raw aggregate JSON")
    parser.add_argument("--normalized-out", required=True, help="Output path for normalized JSON")
    args = parser.parse_args()

    target_path = Path(args.target)
    suite_dir = Path(args.suite_dir)
    raw_out = Path(args.raw_out)
    norm_out = Path(args.normalized_out)

    target = _load_target(target_path)
    suite_paths = sorted(suite_dir.glob(SUITE_GLOB))
    if not suite_paths:
        raise SystemExit(f"No suite outputs found in {suite_dir}")

    suite_results = [json.loads(path.read_text(encoding="utf-8")) for path in suite_paths]
    timestamp = str(target.get("metadata", {}).get("fixed_timestamp", "stable"))

    raw_payload = {
        "target_id": target.get("target_id", "unknown"),
        "suite_outputs": suite_results,
    }
    normalized = build_normalized(target, suite_results, timestamp)

    raw_out.write_text(json.dumps(raw_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    norm_out.write_text(json.dumps(normalized, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"Wrote {raw_out}")
    print(f"Wrote {norm_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
