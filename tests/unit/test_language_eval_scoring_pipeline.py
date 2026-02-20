from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml


@pytest.mark.unit
def test_compare_baseline_partial_scope_skips_non_executed_suite_regressions(tmp_path: Path) -> None:
    root = tmp_path / ".language-eval"
    target_dir = root / "targets"
    baseline_dir = root / "baselines"
    target_dir.mkdir(parents=True)
    baseline_dir.mkdir(parents=True)

    target = {
        "target_id": "t-partial",
        "baseline": "baselines/base.json",
        "allowlisted_regressions": [],
        "thresholds": {"regression_tolerance_pct": 5.0},
    }
    target_path = target_dir / "target.yaml"
    target_path.write_text(yaml.safe_dump(target), encoding="utf-8")

    baseline = {
        "overall_score": 3.2,
        "category_scores": {
            "correctness_semantics": 4.0,
            "security_properties": 3.8,
            "runtime_performance": 3.5,
            "compiler_toolchain_performance": 3.4,
            "concurrency_model": 3.3,
            "tooling_static_analysis": 3.6,
        },
    }
    (baseline_dir / "base.json").write_text(json.dumps(baseline), encoding="utf-8")

    normalized = {
        "target_id": "t-partial",
        "timestamp": "stable",
        "suites": [
            {"name": "conformance", "status": "pass", "metrics": {}},
            {"name": "security", "status": "pass", "metrics": {}},
            {"name": "tooling", "status": "pass", "metrics": {}},
        ],
        "metrics": {"category_inputs": {}},
    }
    normalized_path = tmp_path / "normalized.json"
    normalized_path.write_text(json.dumps(normalized), encoding="utf-8")

    scorecard = {
        "overall_score": 2.8,
        "category_scores": {
            "correctness_semantics": 3.9,
            "security_properties": 3.7,
            "runtime_performance": 2.0,
            "compiler_toolchain_performance": 2.1,
            "concurrency_model": 2.2,
            "tooling_static_analysis": 3.5,
        },
    }
    scorecard_path = tmp_path / "scorecard.json"
    scorecard_path.write_text(json.dumps(scorecard), encoding="utf-8")

    out_path = tmp_path / "comparison.json"
    script = Path(".language-eval/scripts/compare_baseline.py")
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--target",
            str(target_path),
            "--current",
            str(normalized_path),
            "--scorecard",
            str(scorecard_path),
            "--out",
            str(out_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    payload = json.loads(out_path.read_text(encoding="utf-8"))
    regression_ids = {entry["id"] for entry in payload["regressions"]}

    assert payload["regression_scope"] == "partial"
    assert "category:runtime_performance" not in regression_ids
    assert "category:compiler_toolchain_performance" not in regression_ids
    assert "category:concurrency_model" not in regression_ids
    assert "runtime_performance" in payload["skipped_categories"]


@pytest.mark.unit
def test_compare_baseline_full_scope_reports_regression_for_executed_suite(tmp_path: Path) -> None:
    root = tmp_path / ".language-eval"
    target_dir = root / "targets"
    baseline_dir = root / "baselines"
    target_dir.mkdir(parents=True)
    baseline_dir.mkdir(parents=True)

    target = {
        "target_id": "t-full",
        "baseline": "baselines/base.json",
        "allowlisted_regressions": [],
        "thresholds": {"regression_tolerance_pct": 5.0},
    }
    target_path = target_dir / "target.yaml"
    target_path.write_text(yaml.safe_dump(target), encoding="utf-8")

    baseline = {
        "overall_score": 3.6,
        "category_scores": {
            "runtime_performance": 4.0,
        },
    }
    (baseline_dir / "base.json").write_text(json.dumps(baseline), encoding="utf-8")

    normalized = {
        "target_id": "t-full",
        "timestamp": "stable",
        "suites": [
            {"name": "performance", "status": "pass", "metrics": {}},
        ],
        "metrics": {"category_inputs": {}},
    }
    normalized_path = tmp_path / "normalized.json"
    normalized_path.write_text(json.dumps(normalized), encoding="utf-8")

    scorecard = {
        "overall_score": 3.1,
        "category_scores": {
            "runtime_performance": 2.0,
        },
    }
    scorecard_path = tmp_path / "scorecard.json"
    scorecard_path.write_text(json.dumps(scorecard), encoding="utf-8")

    out_path = tmp_path / "comparison.json"
    script = Path(".language-eval/scripts/compare_baseline.py")
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--target",
            str(target_path),
            "--current",
            str(normalized_path),
            "--scorecard",
            str(scorecard_path),
            "--out",
            str(out_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    payload = json.loads(out_path.read_text(encoding="utf-8"))
    regression_ids = {entry["id"] for entry in payload["regressions"]}

    assert "category:runtime_performance" in regression_ids


@pytest.mark.unit
def test_scorecard_applies_profile_and_override_weights(tmp_path: Path) -> None:
    target = {
        "target_id": "t-score",
        "weight_profile": "default",
        "weight_overrides": {
            "correctness_semantics": 0.7,
            "security_properties": 0.3,
        },
    }
    target_path = tmp_path / "target.yaml"
    target_path.write_text(yaml.safe_dump(target), encoding="utf-8")

    normalized = {
        "target_id": "t-score",
        "metrics": {
            "category_inputs": {
                "correctness_semantics": 5.0,
                "security_properties": 1.0,
            }
        },
        "suites": [
            {"name": "conformance", "metrics": {"pass_rate": 1.0}},
            {"name": "security", "metrics": {"policy_pass_rate": 1.0}},
        ],
    }
    normalized_path = tmp_path / "normalized.json"
    normalized_path.write_text(json.dumps(normalized), encoding="utf-8")

    weights = {
        "profiles": {
            "default": {
                "correctness_semantics": 0.5,
                "security_properties": 0.5,
            }
        },
        "profile_references": {},
    }
    weights_path = tmp_path / "weights.json"
    weights_path.write_text(json.dumps(weights), encoding="utf-8")

    out_path = tmp_path / "scorecard.json"
    script = Path(".language-eval/scripts/scorecard.py")
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--target",
            str(target_path),
            "--normalized",
            str(normalized_path),
            "--weights",
            str(weights_path),
            "--out",
            str(out_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    payload = json.loads(out_path.read_text(encoding="utf-8"))

    assert payload["weights"]["correctness_semantics"] == pytest.approx(0.7)
    assert payload["weights"]["security_properties"] == pytest.approx(0.3)
    assert payload["overall_score"] == pytest.approx(3.8)


@pytest.mark.unit
def test_normalize_results_generates_expected_category_inputs(tmp_path: Path) -> None:
    target_path = tmp_path / "target.yaml"
    target_path.write_text(
        yaml.safe_dump(
            {
                "target_id": "t-normalize",
                "metadata": {"fixed_timestamp": "stable"},
            }
        ),
        encoding="utf-8",
    )

    suite_dir = tmp_path / "suites"
    suite_dir.mkdir(parents=True)
    (suite_dir / "suite.conformance.json").write_text(
        json.dumps({"suite": "conformance", "status": "pass", "metrics": {"pass_rate": 0.98}}),
        encoding="utf-8",
    )
    (suite_dir / "suite.security.json").write_text(
        json.dumps(
            {
                "suite": "security",
                "status": "pass",
                "metrics": {"policy_pass_rate": 0.95, "critical_findings": 0, "high_findings": 1},
            }
        ),
        encoding="utf-8",
    )
    (suite_dir / "suite.tooling.json").write_text(
        json.dumps(
            {
                "suite": "tooling",
                "status": "pass",
                "metrics": {
                    "formatter_idempotence_rate": 1.0,
                    "lsp_correctness_rate": 0.95,
                    "lsp_p95_ms": 120.0,
                    "linter_false_positive_rate": 0.02,
                },
            }
        ),
        encoding="utf-8",
    )

    raw_out = tmp_path / "results.raw.json"
    normalized_out = tmp_path / "results.normalized.json"
    script = Path(".language-eval/scripts/normalize_results.py")

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--target",
            str(target_path),
            "--suite-dir",
            str(suite_dir),
            "--raw-out",
            str(raw_out),
            "--normalized-out",
            str(normalized_out),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr or result.stdout

    normalized = json.loads(normalized_out.read_text(encoding="utf-8"))
    category_inputs = normalized["metrics"]["category_inputs"]
    assert normalized["target_id"] == "t-normalize"
    assert normalized["timestamp"] == "stable"
    assert category_inputs["correctness_semantics"] == pytest.approx(4.9)
    assert category_inputs["security_properties"] == pytest.approx(4.55)
    assert category_inputs["tooling_static_analysis"] > 4.0
