# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""Tests for normalize_results.py: category inference and suite-to-category mapping."""

import json
import sys
from pathlib import Path

import pytest

# Import the normalize_results module
sys.path.insert(0, str(Path(__file__).parent.parent.parent / ".language-eval" / "scripts"))
import normalize_results


@pytest.fixture
def mock_conformance_suite():
    """Mock conformance suite output."""
    return {
        "suite": "conformance",
        "metrics": {
            "pass_rate": 0.95,
            "total_tests": 100,
            "passed": 95,
            "failed": 5,
        },
    }


@pytest.fixture
def mock_security_suite():
    """Mock security suite output."""
    return {
        "suite": "security",
        "metrics": {
            "policy_pass_rate": 1.0,
            "critical_findings": 0,
            "high_findings": 0,
            "medium_findings": 2,
        },
    }


@pytest.fixture
def mock_performance_suite():
    """Mock performance suite output."""
    return {
        "suite": "performance",
        "metrics": {
            "throughput_ops_per_sec": 2000,
            "latency_ms": {
                "p50": 10.0,
                "p95": 80.0,
                "p99": 150.0,
            },
            "rss_mb": 200.0,
        },
    }


class TestCategoryInference:
    """Test category score inference from suite metrics."""

    def test_conformance_to_correctness_semantics(self, mock_conformance_suite):
        """Verify conformance pass_rate maps to correctness_semantics."""
        category_inputs = normalize_results._suite_to_category_inputs([mock_conformance_suite])
        
        # pass_rate=0.95 -> score = 0.95 * 5.0 = 4.75
        assert category_inputs["correctness_semantics"] == pytest.approx(4.75, abs=0.01)

    def test_conformance_to_reliability(self, mock_conformance_suite):
        """Verify conformance pass_rate maps to reliability."""
        category_inputs = normalize_results._suite_to_category_inputs([mock_conformance_suite])
        
        # pass_rate=0.95 -> score = 0.95 * 4.8 = 4.56
        assert category_inputs["reliability"] == pytest.approx(4.56, abs=0.01)

    def test_security_base_score(self, mock_security_suite):
        """Verify security policy_pass_rate maps correctly."""
        category_inputs = normalize_results._suite_to_category_inputs([mock_security_suite])
        
        # policy_pass_rate=1.0 -> base = 1.0 * 5.0 = 5.0, no penalties
        assert category_inputs["security_properties"] == pytest.approx(5.0, abs=0.01)

    def test_security_with_critical_findings(self):
        """Verify critical findings apply penalty."""
        security_suite = {
            "suite": "security",
            "metrics": {
                "policy_pass_rate": 1.0,
                "critical_findings": 2,
                "high_findings": 0,
            },
        }
        
        category_inputs = normalize_results._suite_to_category_inputs([security_suite])
        
        # base = 5.0, penalty = 2*1.0 = 2.0, final = 3.0
        assert category_inputs["security_properties"] == pytest.approx(3.0, abs=0.01)

    def test_performance_runtime_score(self, mock_performance_suite):
        """Verify performance metrics map to runtime_performance."""
        category_inputs = normalize_results._suite_to_category_inputs([mock_performance_suite])
        
        # throughput=2000, p95=80, rss=200
        # perf_score = 1.5 + (2000/2000)*2.0 + max(0, (120-80)/120) = 1.5 + 2.0 + 0.333 = 3.833
        # footprint_penalty = max(0, (200-256)/256) = 0 (no penalty)
        # final = min(5.0, 3.833 - 0) = 3.833
        assert category_inputs["runtime_performance"] >= 3.5
        assert category_inputs["runtime_performance"] <= 4.5

    def test_clamp_score_bounds(self):
        """Verify _clamp_score enforces 0.0-5.0 bounds."""
        assert normalize_results._clamp_score(-1.0) == 0.0
        assert normalize_results._clamp_score(6.0) == 5.0
        assert normalize_results._clamp_score(3.5) == 3.5


class TestMultiSuiteIntegration:
    """Test category inference from multiple suites."""

    def test_combined_suites_all_categories_computed(
        self, mock_conformance_suite, mock_security_suite, mock_performance_suite
    ):
        """Verify all categories are computed when multiple suites present."""
        suites = [mock_conformance_suite, mock_security_suite, mock_performance_suite]
        category_inputs = normalize_results._suite_to_category_inputs(suites)
        
        # All 13 categories should be present
        assert len(category_inputs) == 13
        
        # Derived categories should have non-default values
        assert "correctness_semantics" in category_inputs
        assert "security_properties" in category_inputs
        assert "runtime_performance" in category_inputs
        assert "dx_productivity" in category_inputs
        assert "ecosystem_health" in category_inputs


class TestDefaultFallbacks:
    """Test default category values when suites are missing."""

    def test_empty_suite_list_returns_defaults(self):
        """Verify derived categories have baseline values when no suites present."""
        category_inputs = normalize_results._suite_to_category_inputs([])
        
        # Primary categories should default to 2.5
        assert category_inputs["correctness_semantics"] == 2.5
        assert category_inputs["security_properties"] == 2.5
        assert category_inputs["runtime_performance"] == 2.5
        
        # Derived categories will have calculated values from the defaults
        assert "interop_integration" in category_inputs
        assert "ecosystem_health" in category_inputs


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
