from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.unit
def test_ci_gate_determinism_only_ignores_regression_checks(tmp_path: Path) -> None:
    root = tmp_path / ".language-eval"
    schema_dir = root / "schemas"
    target_dir = root / "targets"
    report_dir = tmp_path / "report_a"
    compare_dir = tmp_path / "report_b"

    schema_dir.mkdir(parents=True)
    target_dir.mkdir(parents=True)
    report_dir.mkdir(parents=True)
    compare_dir.mkdir(parents=True)

    permissive_schema = {"type": "object", "additionalProperties": True}
    (schema_dir / "target.schema.json").write_text(json.dumps(permissive_schema), encoding="utf-8")
    (schema_dir / "results.schema.json").write_text(json.dumps(permissive_schema), encoding="utf-8")
    (schema_dir / "report.schema.json").write_text(json.dumps(permissive_schema), encoding="utf-8")

    target_path = target_dir / "example-target.yaml"
    target_path.write_text(
        "\n".join(
            [
                "target_id: t1",
                "required_suites:",
                "  - conformance",
                "  - security",
                "  - tooling",
                "thresholds:",
                "  regression_tolerance_pct: 5.0",
                "  min_overall_score: 3.5",
                "  require_deterministic_report: true",
                "  require_artifacts:",
                "    - results.raw.json",
                "    - results.normalized.json",
                "    - scorecard.json",
                "    - report.json",
                "    - report.md",
                "",
            ]
        ),
        encoding="utf-8",
    )

    normalized = {
        "target_id": "t1",
        "timestamp": "stable",
        "suites": [
            {"name": "conformance", "status": "pass", "metrics": {}},
            {"name": "security", "status": "pass", "metrics": {}},
            {"name": "tooling", "status": "pass", "metrics": {}},
        ],
        "metrics": {"category_inputs": {}},
    }
    report = {"target_id": "t1", "generated_at": "stable", "overall_score": 4.2}
    scorecard = {"overall_score": 2.0}
    comparison = {"regressions": [{"id": "category:runtime_performance"}]}

    for path in (report_dir, compare_dir):
        (path / "results.raw.json").write_text("{}\n", encoding="utf-8")
        (path / "results.normalized.json").write_text(
            json.dumps(normalized) + "\n", encoding="utf-8"
        )
        (path / "scorecard.json").write_text(json.dumps(scorecard) + "\n", encoding="utf-8")
        (path / "comparison.json").write_text(json.dumps(comparison) + "\n", encoding="utf-8")
        (path / "report.md").write_text("# report\n", encoding="utf-8")
        report_path = path / "report.json"
        report_path.write_text(json.dumps(report) + "\n", encoding="utf-8")
        digest = subprocess.run(
            [sys.executable, "-c", "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())", str(report_path)],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        (path / "report.sha256").write_text(digest + "\n", encoding="utf-8")

    script = Path(".language-eval/scripts/ci_gate.py")
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--target",
            str(target_path),
            "--report-dir",
            str(report_dir),
            "--compare-report-dir",
            str(compare_dir),
            "--determinism-only",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout


@pytest.mark.unit
def test_ci_gate_enforces_regressions_without_determinism_only(tmp_path: Path) -> None:
    root = tmp_path / ".language-eval"
    schema_dir = root / "schemas"
    target_dir = root / "targets"
    report_dir = tmp_path / "report"

    schema_dir.mkdir(parents=True)
    target_dir.mkdir(parents=True)
    report_dir.mkdir(parents=True)

    permissive_schema = {"type": "object", "additionalProperties": True}
    (schema_dir / "target.schema.json").write_text(json.dumps(permissive_schema), encoding="utf-8")
    (schema_dir / "results.schema.json").write_text(json.dumps(permissive_schema), encoding="utf-8")
    (schema_dir / "report.schema.json").write_text(json.dumps(permissive_schema), encoding="utf-8")

    target_path = target_dir / "example-target.yaml"
    target_path.write_text(
        "\n".join(
            [
                "target_id: t1",
                "required_suites:",
                "  - conformance",
                "thresholds:",
                "  min_overall_score: 0.0",
                "  require_deterministic_report: true",
                "  require_artifacts:",
                "    - results.raw.json",
                "    - results.normalized.json",
                "    - scorecard.json",
                "    - report.json",
                "    - report.md",
                "",
            ]
        ),
        encoding="utf-8",
    )

    (report_dir / "results.raw.json").write_text("{}\n", encoding="utf-8")
    (report_dir / "results.normalized.json").write_text(
        json.dumps(
            {
                "suites": [{"name": "conformance", "status": "pass", "metrics": {}}],
                "metrics": {"category_inputs": {}},
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (report_dir / "scorecard.json").write_text(json.dumps({"overall_score": 4.0}) + "\n", encoding="utf-8")
    (report_dir / "report.json").write_text(json.dumps({"overall_score": 4.0}) + "\n", encoding="utf-8")
    (report_dir / "report.md").write_text("# report\n", encoding="utf-8")
    (report_dir / "comparison.json").write_text(
        json.dumps({"regressions": [{"id": "category:runtime_performance"}]}) + "\n",
        encoding="utf-8",
    )

    digest = subprocess.run(
        [
            sys.executable,
            "-c",
            "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())",
            str(report_dir / "report.json"),
        ],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    (report_dir / "report.sha256").write_text(digest + "\n", encoding="utf-8")

    script = Path(".language-eval/scripts/ci_gate.py")
    result = subprocess.run(
        [sys.executable, str(script), "--target", str(target_path), "--report-dir", str(report_dir)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "Regressions exceed threshold" in (result.stderr + result.stdout)


@pytest.mark.unit
def test_ci_gate_skips_hash_when_target_disables_determinism(tmp_path: Path) -> None:
    root = tmp_path / ".language-eval"
    schema_dir = root / "schemas"
    target_dir = root / "targets"
    report_dir = tmp_path / "report"

    schema_dir.mkdir(parents=True)
    target_dir.mkdir(parents=True)
    report_dir.mkdir(parents=True)

    permissive_schema = {"type": "object", "additionalProperties": True}
    (schema_dir / "target.schema.json").write_text(json.dumps(permissive_schema), encoding="utf-8")
    (schema_dir / "results.schema.json").write_text(json.dumps(permissive_schema), encoding="utf-8")
    (schema_dir / "report.schema.json").write_text(json.dumps(permissive_schema), encoding="utf-8")

    target_path = target_dir / "example-target.yaml"
    target_path.write_text(
        "\n".join(
            [
                "target_id: t1",
                "required_suites:",
                "  - conformance",
                "thresholds:",
                "  min_overall_score: 0.0",
                "  require_deterministic_report: false",
                "  require_artifacts:",
                "    - results.raw.json",
                "    - results.normalized.json",
                "    - scorecard.json",
                "    - report.json",
                "    - report.md",
                "",
            ]
        ),
        encoding="utf-8",
    )

    (report_dir / "results.raw.json").write_text("{}\n", encoding="utf-8")
    (report_dir / "results.normalized.json").write_text(
        json.dumps(
            {
                "suites": [{"name": "conformance", "status": "pass", "metrics": {}}],
                "metrics": {"category_inputs": {}},
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (report_dir / "scorecard.json").write_text(json.dumps({"overall_score": 4.0}) + "\n", encoding="utf-8")
    (report_dir / "report.json").write_text(json.dumps({"overall_score": 4.0}) + "\n", encoding="utf-8")
    (report_dir / "report.md").write_text("# report\n", encoding="utf-8")

    script = Path(".language-eval/scripts/ci_gate.py")
    result = subprocess.run(
        [sys.executable, str(script), "--target", str(target_path), "--report-dir", str(report_dir)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout


@pytest.mark.unit
def test_ci_gate_fails_on_expired_expected_failures(tmp_path: Path) -> None:
    root = tmp_path / ".language-eval"
    schema_dir = root / "schemas"
    target_dir = root / "targets"
    suites_dir = root / "suites" / "conformance"
    report_dir = tmp_path / "report"

    schema_dir.mkdir(parents=True)
    target_dir.mkdir(parents=True)
    suites_dir.mkdir(parents=True)
    report_dir.mkdir(parents=True)

    permissive_schema = {"type": "object", "additionalProperties": True}
    (schema_dir / "target.schema.json").write_text(json.dumps(permissive_schema), encoding="utf-8")
    (schema_dir / "results.schema.json").write_text(json.dumps(permissive_schema), encoding="utf-8")
    (schema_dir / "report.schema.json").write_text(json.dumps(permissive_schema), encoding="utf-8")

    (suites_dir / "expected_failures.yaml").write_text(
        "\n".join(
            [
                "expected_failures:",
                "  - id: expired-1",
                "    reason: old issue",
                "    owner: core",
                "    introduced: '2025-01-01'",
                "    expiry: '2025-01-02'",
                "",
            ]
        ),
        encoding="utf-8",
    )

    target_path = target_dir / "example-target.yaml"
    target_path.write_text(
        "\n".join(
            [
                "target_id: t1",
                "required_suites:",
                "  - conformance",
                "expected_failures_file: ../suites/conformance/expected_failures.yaml",
                "thresholds:",
                "  min_overall_score: 0.0",
                "  require_deterministic_report: false",
                "  require_artifacts:",
                "    - results.raw.json",
                "    - results.normalized.json",
                "    - scorecard.json",
                "    - report.json",
                "    - report.md",
                "",
            ]
        ),
        encoding="utf-8",
    )

    (report_dir / "results.raw.json").write_text("{}\n", encoding="utf-8")
    (report_dir / "results.normalized.json").write_text(
        json.dumps(
            {
                "suites": [{"name": "conformance", "status": "pass", "metrics": {}}],
                "metrics": {"category_inputs": {}},
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (report_dir / "scorecard.json").write_text(json.dumps({"overall_score": 4.0}) + "\n", encoding="utf-8")
    (report_dir / "report.json").write_text(json.dumps({"overall_score": 4.0}) + "\n", encoding="utf-8")
    (report_dir / "report.md").write_text("# report\n", encoding="utf-8")

    script = Path(".language-eval/scripts/ci_gate.py")
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--target",
            str(target_path),
            "--report-dir",
            str(report_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "LANG_EVAL_TODAY": "2026-01-01"},
    )

    assert result.returncode != 0
    assert "Expired expected failures detected" in (result.stderr + result.stdout)
