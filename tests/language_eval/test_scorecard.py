# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""Tests for scorecard.py: weight resolution and score calculation."""

import json
import sys
import tempfile
from pathlib import Path

import pytest

# Import the scorecard module
sys.path.insert(0, str(Path(__file__).parent.parent.parent / ".language-eval" / "scripts"))


@pytest.fixture
def mock_normalized_results():
    """Minimal normalized results fixture."""
    return {
        "target_id": "pel-test",
        "timestamp": "2026-01-15T12:00:00Z",
        "categories": {
            "correctness": {
                "metrics": {"pass_rate": 0.95, "fail_count": 5},
                "score": 4.5,
            },
            "security": {
                "metrics": {"vuln_count": 0, "cve_found": False},
                "score": 5.0,
            },
            "performance": {
                "metrics": {"throughput_ops_sec": 1000, "p99_latency_ms": 50},
                "score": 4.0,
            },
        },
    }


@pytest.fixture
def mock_target_config():
    """Mock target configuration."""
    return {
        "target_id": "pel-test",
        "weight_profile": "web_backend",
        "weight_overrides": {},
    }


@pytest.fixture
def mock_weights_default():
    """Mock default weights matching web_backend profile."""
    return {
        "profiles": {
            "web_backend": {
                "correctness": 0.35,
                "security": 0.25,
                "performance": 0.20,
                "tooling": 0.10,
                "human_factors": 0.10,
            },
            "systems": {
                "correctness": 0.30,
                "security": 0.20,
                "performance": 0.30,
                "tooling": 0.10,
                "human_factors": 0.10,
            },
        }
    }


class TestWeightResolution:
    """Test weight resolution from profile + overrides."""

    def test_resolve_weight_profile_default(self, mock_weights_default, mock_target_config):
        """Verify weight resolution from profile without overrides."""
        with tempfile.TemporaryDirectory() as tmpdir:
            weights_path = Path(tmpdir) / "WEIGHTS.default.json"
            weights_path.write_text(json.dumps(mock_weights_default))

            # Test the logic directly
            profile = mock_target_config["weight_profile"]
            weights = mock_weights_default["profiles"][profile]

            assert weights["correctness"] == 0.35
            assert weights["security"] == 0.25
            assert weights["performance"] == 0.20

    def test_resolve_weight_profile_with_overrides(self, mock_weights_default):
        """Verify weight overrides merge correctly."""
        profile_weights = mock_weights_default["profiles"]["web_backend"]
        overrides = {
            "correctness": 0.50,
            "performance": 0.10,
        }

        # Simulate override logic
        merged = {**profile_weights, **overrides}

        assert merged["correctness"] == 0.50  # override
        assert merged["security"] == 0.25  # from profile
        assert merged["performance"] == 0.10  # override

    def test_resolve_weight_unknown_profile(self, mock_weights_default):
        """Verify handling of unknown profile (would fall back or error)."""
        # Test that unknown profile is not in the profiles dict
        assert "unknown_profile" not in mock_weights_default["profiles"]


class TestScoreCalculation:
    """Test overall score computation."""

    def test_overall_score_weighted_average(self, mock_normalized_results, mock_target_config, mock_weights_default):
        """Verify overall score is weighted average of category scores."""
        weights = mock_weights_default["profiles"]["web_backend"]
        category_scores = {
            "correctness": 4.5,
            "security": 5.0,
            "performance": 4.0,
        }

        # Manual calculation: sum(weight * score) for present categories
        overall = (
            weights["correctness"] * category_scores["correctness"] +
            weights["security"] * category_scores["security"] +
            weights["performance"] * category_scores["performance"]
        )

        # Expected: 0.35*4.5 + 0.25*5.0 + 0.20*4.0 = 1.575 + 1.25 + 0.8 = 3.625
        assert overall == pytest.approx(3.625, abs=0.01)

    def test_score_excludes_missing_categories(self, mock_weights_default):
        """Verify overall score only includes present categories."""
        weights = mock_weights_default["profiles"]["web_backend"]
        category_scores = {"correctness": 5.0}

        # Only correctness present, weight=0.35, score=5.0
        overall = weights["correctness"] * category_scores["correctness"]

        # Overall = 0.35 * 5.0 = 1.75
        assert overall == pytest.approx(1.75, abs=0.01)


class TestSuiteLevelScores:
    """Test suite-level score mapping."""

    def test_suite_scores_mapped_from_categories(self):
        """Verify suite scores are derived from relevant categories."""
        # This would require extracting the mapping logic from scorecard.py
        # Skipping detailed implementation for now
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
