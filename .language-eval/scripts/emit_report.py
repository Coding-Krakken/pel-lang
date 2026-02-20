#!/usr/bin/env python3
# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""Render report.json/report.md/summary.md from normalized + scorecard + comparison."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
from pathlib import Path
from typing import Any

import yaml


def _load(path: Path) -> dict[str, Any]:
    if path.suffix.lower() in {".yaml", ".yml"}:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    return json.loads(path.read_text(encoding="utf-8"))


def _write_md_report(
    out_path: Path,
    target: dict[str, Any],
    scorecard: dict[str, Any],
    comparison: dict[str, Any],
    suites: list[dict[str, Any]],
) -> None:
    lines = [
        "# Language Evaluation Report",
        "",
        f"- Target: {target.get('target_id', 'unknown')}",
        f"- Language: {target.get('language', {}).get('name', 'unknown')} {target.get('language', {}).get('version', '')}",
        f"- Overall score: {scorecard.get('overall_score', 0.0):.3f}/5.0",
        "",
        "## Category Scores",
    ]

    for category, value in sorted(scorecard.get("category_scores", {}).items()):
        lines.append(f"- {category}: {value:.3f}")

    lines.extend(["", "## Suite Status"])
    for suite in suites:
        lines.append(f"- {suite['name']}: {suite['status']}")

    regressions = comparison.get("regressions", [])
    lines.extend(["", "## Baseline Comparison"])
    if regressions:
        lines.append("- Regressions detected:")
        for reg in regressions:
            lines.append(
                f"  - {reg['id']}: baseline={reg['baseline']:.4f}, current={reg['current']:.4f}, delta={reg['delta']:.4f}"
            )
    else:
        lines.append("- No regressions above threshold.")

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_summary(summary_path: Path, scorecard: dict[str, Any], comparison: dict[str, Any]) -> None:
    regressions = comparison.get("regressions", [])
    status = "✅ PASS" if not regressions else "❌ FAIL"
    lines = [
        "# Language Eval Summary",
        "",
        f"- Gate status: {status}",
        f"- Overall score: {scorecard.get('overall_score', 0.0):.3f}/5.0",
        f"- Regression count: {len(regressions)}",
    ]
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _environment_fingerprint(
    target: dict[str, Any],
    normalized_path: Path,
    scorecard_path: Path,
    comparison_path: Path,
) -> dict[str, Any]:
    return {
        "os": platform.system().lower(),
        "arch": platform.machine().lower(),
        "python": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "target_platform": target.get("platform", {}),
        "input_hashes": {
            "normalized": _sha256(normalized_path),
            "scorecard": _sha256(scorecard_path),
            "comparison": _sha256(comparison_path),
        },
        "deterministic_timestamp": os.getenv("LANG_EVAL_TIMESTAMP") is not None,
        "lang_eval_timestamp_env": os.getenv("LANG_EVAL_TIMESTAMP", ""),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True)
    parser.add_argument("--normalized", required=True)
    parser.add_argument("--scorecard", required=True)
    parser.add_argument("--comparison", required=True)
    parser.add_argument("--outdir", required=True)
    args = parser.parse_args()

    target = _load(Path(args.target))
    normalized = _load(Path(args.normalized))
    scorecard = _load(Path(args.scorecard))
    comparison = _load(Path(args.comparison))

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    report_md = outdir / "report.md"
    summary_md = outdir / "summary.md"
    report_json = outdir / "report.json"

    _write_md_report(report_md, target, scorecard, comparison, normalized.get("suites", []))
    _write_summary(summary_md, scorecard, comparison)

    report_payload = {
        "target_id": scorecard.get("target_id", target.get("target_id", "unknown")),
        "generated_at": normalized.get("timestamp", "stable"),
        "generated_by": {
            "script": "emit_report.py",
            "python": sys.version.split()[0],
        },
        "environment": _environment_fingerprint(
            target,
            Path(args.normalized),
            Path(args.scorecard),
            Path(args.comparison),
        ),
        "overall_score": scorecard.get("overall_score", 0.0),
        "category_scores": scorecard.get("category_scores", {}),
        "suite_scores": scorecard.get("suite_scores", {}),
        "comparisons": comparison,
        "artifacts": {
            "results_raw": "results.raw.json",
            "results_normalized": "results.normalized.json",
            "scorecard": "scorecard.json",
            "report_md": "report.md",
            "summary_md": "summary.md",
        },
    }

    report_json.write_text(json.dumps(report_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    digest = _sha256(report_json)
    (outdir / "report.sha256").write_text(digest + "\n", encoding="utf-8")

    print(f"Wrote {report_json}")
    print(f"Wrote {report_md}")
    print(f"Wrote {summary_md}")
    print(f"Wrote {outdir / 'report.sha256'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
