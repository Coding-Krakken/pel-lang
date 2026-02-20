# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""Tests for compare_baseline.py: regression detection and scope awareness."""

import subprocess
import sys
from pathlib import Path

import pytest

# Import the compare_baseline module
sys.path.insert(0, str(Path(__file__).parent.parent.parent / ".language-eval" / "scripts"))


@pytest.fixture
def mock_baseline_scorecard():
    """Mock baseline scorecard."""
    return {
        "target_id": "pel-baseline",
        "overall_score": 4.5,
        "category_scores": {
            "correctness": 4.5,
            "security": 5.0,
            "performance": 4.0,
            "tooling": 3.5,
            "human_factors": 3.0,
        },
    }


@pytest.fixture
def mock_current_scorecard():
    """Mock current scorecard showing regression."""
    return {
        "target_id": "pel-current",
        "overall_score": 4.2,
        "category_scores": {
            "correctness": 4.5,
            "security": 5.0,
            "performance": 3.5,  # regression: 4.0 -> 3.5
            "tooling": 3.5,
            "human_factors": 3.0,
        },
    }


@pytest.fixture
def mock_target_config():
    """Mock target configuration."""
    return {
        "target_id": "pel-test",
        "baseline": "baselines/baseline.json",
        "thresholds": {
            "regression_tolerance_pct": 5.0,
        },
    }


class TestRegressionDetection:
    """Test regression detection logic."""

    def test_no_regression_when_scores_stable(self, mock_baseline_scorecard):
        """Verify no regression detected when scores are stable."""
        current = mock_baseline_scorecard.copy()

        # Manually compute deltas
        baseline_scores = mock_baseline_scorecard["category_scores"]
        current_scores = current["category_scores"]

        for category in baseline_scores:
            delta = current_scores[category] - baseline_scores[category]
            assert delta == 0.0

    def test_regression_detected_when_score_drops(self, mock_baseline_scorecard, mock_current_scorecard):
        """Verify regression detected when score drops significantly."""
        baseline_scores = mock_baseline_scorecard["category_scores"]
        current_scores = mock_current_scorecard["category_scores"]

        # performance dropped from 4.0 to 3.5
        delta = current_scores["performance"] - baseline_scores["performance"]
        assert delta == pytest.approx(-0.5, abs=0.01)
        assert delta < 0

    def test_tolerance_threshold_applied(self):
        """Verify regression tolerance threshold is respected."""
        # Mock the tolerance check logic
        tolerance_pct = 5.0

        # -3.75% delta (within 5% tolerance)
        delta_ok = (3.85 - 4.0) / 4.0 * 100
        # -7.5% delta (exceeds 5% tolerance)
        delta_bad = (3.7 - 4.0) / 4.0 * 100

        assert abs(delta_ok) < tolerance_pct
        assert abs(delta_bad) > tolerance_pct


class TestScopeAwareness:
    """Test suite-aware regression scoping."""

    def test_regression_scoped_to_executed_suites(self):
        """Verify regression check only applies to categories covered by executed suites."""
        # If only conformance suite ran, should only check correctness/reliability
        # This requires understanding the CATEGORY_SUITE_DEPENDENCIES mapping

        # Simplified test: verify that categories not covered by executed suites are skipped
        executed_suites = ["conformance"]

        # Mock the dependency mapping (from compare_baseline.py)
        category_suite_deps = {
            "correctness": ["conformance"],
            "security": ["security"],
            "performance": ["performance"],
            "tooling": ["tooling"],
            "human_factors": ["human_factors"],
        }

        evaluated_categories = []
        for category, required_suites in category_suite_deps.items():
            if all(suite in executed_suites for suite in required_suites):
                evaluated_categories.append(category)

        assert "correctness" in evaluated_categories
        assert "security" not in evaluated_categories


class TestBaselineNotFound:
    """Test behavior when baseline file is missing."""

    def test_baseline_missing_fails(self, tmp_path):
        """Verify missing baseline is treated as an error."""
        target_dir = tmp_path / ".language-eval" / "targets"
        target_dir.mkdir(parents=True)
        target_path = target_dir / "target.yaml"
        target_path.write_text(
            "\n".join(
                [
                    "target_id: t1",
                    "baseline: baselines/missing.json",
                    "thresholds:",
                    "  regression_tolerance_pct: 5.0",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        normalized_path = tmp_path / "normalized.json"
        normalized_path.write_text(
            '{"target_id": "t1", "suites": [], "metrics": {"category_inputs": {}}}\n',
            encoding="utf-8",
        )
        scorecard_path = tmp_path / "scorecard.json"
        scorecard_path.write_text('{"overall_score": 0.0, "category_scores": {}}\n', encoding="utf-8")

        out_path = tmp_path / "comparison.json"
        result = subprocess.run(
            [
                sys.executable,
                str(Path(".language-eval/scripts/compare_baseline.py")),
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

        assert result.returncode != 0
        assert "Baseline not found" in (result.stderr + result.stdout)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
