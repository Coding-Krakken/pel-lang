#!/usr/bin/env python3
"""CI gate for language-eval artifacts, schemas, regressions, and determinism."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
from typing import Any

import yaml


def _load(path: Path) -> dict[str, Any]:
    if path.suffix.lower() in {".yaml", ".yml"}:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_with_schema(schema_path: Path, payload_path: Path) -> None:
    try:
        import jsonschema
    except ImportError as exc:
        raise SystemExit("jsonschema is required for ci_gate.py. Install with: pip install jsonschema") from exc

    schema = _load(schema_path)
    payload = _load(payload_path)
    jsonschema.validate(payload, schema)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _resolve_optional_path(path_value: str, target_path: Path, root: Path) -> Path | None:
    if not path_value:
        return None

    candidate = Path(path_value)
    if candidate.is_absolute() and candidate.exists():
        return candidate
    if candidate.exists():
        return candidate

    for base in (root, target_path.parent):
        resolved = base / candidate
        if resolved.exists():
            return resolved

    return None


def _enforce_expected_failure_expiry(expected_failures_path: Path) -> None:
    payload = _load(expected_failures_path)
    rows = payload.get("expected_failures", [])

    override_today = os.getenv("LANG_EVAL_TODAY")
    today = dt.date.fromisoformat(override_today) if override_today else dt.date.today()

    expired: list[dict[str, str]] = []
    for row in rows:
        failure_id = str(row.get("id", "<missing-id>"))
        expiry_raw = row.get("expiry")
        if not expiry_raw:
            raise SystemExit(f"Expected failure entry missing expiry: {failure_id}")

        try:
            expiry_date = dt.date.fromisoformat(str(expiry_raw))
        except ValueError as exc:
            raise SystemExit(
                f"Invalid expiry date format for expected failure '{failure_id}': {expiry_raw}"
            ) from exc

        if expiry_date < today:
            expired.append({"id": failure_id, "expiry": str(expiry_date), "today": str(today)})

    if expired:
        raise SystemExit(f"Expired expected failures detected: {json.dumps(expired, indent=2)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True)
    parser.add_argument("--report-dir", required=True)
    parser.add_argument("--compare-report-dir", help="Optional second report dir for determinism hash compare")
    parser.add_argument(
        "--determinism-only",
        action="store_true",
        help="Only run schema/artifact/hash determinism checks (skip baseline regression and score threshold checks)",
    )
    args = parser.parse_args()

    target_path = Path(args.target)
    report_dir = Path(args.report_dir)
    compare_dir = Path(args.compare_report_dir) if args.compare_report_dir else None

    target = _load(target_path)

    root = target_path.parent.parent
    schema_dir = root / "schemas"

    if not args.determinism_only:
        expected_failures_ref = str(target.get("expected_failures_file", "")).strip()
        expected_failures_path = _resolve_optional_path(expected_failures_ref, target_path, root)
        if expected_failures_ref and expected_failures_path is None:
            raise SystemExit(f"Expected failures file not found: {expected_failures_ref}")
        if expected_failures_path is not None:
            _enforce_expected_failure_expiry(expected_failures_path)

    required_artifacts = target.get("thresholds", {}).get(
        "require_artifacts",
        ["results.raw.json", "results.normalized.json", "scorecard.json", "report.json", "report.md"],
    )
    missing = [artifact for artifact in required_artifacts if not (report_dir / artifact).exists()]
    if missing:
        raise SystemExit(f"Missing required artifacts: {missing}")

    _validate_with_schema(schema_dir / "target.schema.json", target_path)
    _validate_with_schema(schema_dir / "results.schema.json", report_dir / "results.normalized.json")
    _validate_with_schema(schema_dir / "report.schema.json", report_dir / "report.json")

    normalized = _load(report_dir / "results.normalized.json")
    found_suites = {suite["name"] for suite in normalized.get("suites", [])}
    required_suites = set(target.get("required_suites", []))
    missing_suites = sorted(required_suites - found_suites)
    if missing_suites:
        raise SystemExit(f"Missing required suite outputs: {missing_suites}")

    comparison_file = report_dir / "comparison.json"
    if comparison_file.exists() and not args.determinism_only:
        comparison = _load(comparison_file)
        regressions = comparison.get("regressions", [])
        if regressions:
            raise SystemExit(f"Regressions exceed threshold: {json.dumps(regressions, indent=2)}")

    if not args.determinism_only:
        min_overall = float(target.get("thresholds", {}).get("min_overall_score", 0.0))
        overall = float(_load(report_dir / "scorecard.json").get("overall_score", 0.0))
        if overall < min_overall:
            raise SystemExit(f"Overall score {overall:.4f} below minimum {min_overall:.4f}")

    require_deterministic = bool(target.get("thresholds", {}).get("require_deterministic_report", True))
    report_hash = ""
    if require_deterministic:
        report_hash_file = report_dir / "report.sha256"
        if not report_hash_file.exists():
            raise SystemExit("Missing deterministic artifact: report.sha256")
        report_hash = report_hash_file.read_text(encoding="utf-8").strip()
        computed_hash = _sha256(report_dir / "report.json")
        if report_hash != computed_hash:
            raise SystemExit("report.sha256 mismatch with report.json")

    if compare_dir is not None:
        if not require_deterministic:
            raise SystemExit("compare-report-dir requires thresholds.require_deterministic_report=true")
        other_hash_file = compare_dir / "report.sha256"
        if not other_hash_file.exists():
            raise SystemExit("Missing report.sha256 in compare-report-dir")
        other_hash = other_hash_file.read_text(encoding="utf-8").strip()
        if report_hash != other_hash:
            raise SystemExit(
                f"Non-deterministic report generation: {report_hash} != {other_hash}"
            )

    print("CI gate passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
