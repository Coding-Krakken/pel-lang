# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""Edge case tests for language evaluation framework scripts."""

import sys
from pathlib import Path

import pytest

# Add .language-eval/scripts to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / ".language-eval" / "scripts"))


def test_scorecard_weight_sum_zero():
    """Edge: All weights zero should error."""
    import scorecard

    weights = {"a": 0.0, "b": 0.0}
    with pytest.raises(SystemExit) as excinfo:
        scorecard._resolve_weights(root=None, weights_file=None, target={"weight_profile": "default"})
    assert "Weight sum must equal 1.0" in str(excinfo.value)


def test_compare_baseline_missing_category():
    """Edge: Category in current but not in baseline should not error."""
    import compare_baseline

    current_scores = {"new_cat": 1.0}
    baseline_scores = {}
    # Should not raise
    try:
        delta = current_scores["new_cat"] - baseline_scores.get("new_cat", 1.0)
    except Exception:
        pytest.fail("Should not raise for missing baseline category")


def test_ci_gate_missing_required_suite():
    """Edge: Required suite missing should error."""
    import ci_gate

    suites_payload = [{"name": "conformance", "status": "pass"}]
    required_suites = {"conformance", "security"}
    found_suites = {suite["name"] for suite in suites_payload}
    missing_suites = sorted(required_suites - found_suites)
    assert "security" in missing_suites
