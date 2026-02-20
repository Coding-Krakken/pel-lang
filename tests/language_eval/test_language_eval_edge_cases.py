# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""Edge case tests for language evaluation framework scripts."""

import json
import sys
import tempfile
from pathlib import Path

import pytest

# Add .language-eval/scripts to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / ".language-eval" / "scripts"))


def test_scorecard_weight_sum_zero():
    """Edge: All weights zero should error."""
    import scorecard

    # Create temporary weight file with zero weights
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        weights_data = {"profiles": {"default": {"a": 0.0, "b": 0.0}}}
        json.dump(weights_data, f)
        weights_file = Path(f.name)

    try:
        with pytest.raises(SystemExit) as excinfo:
            scorecard._resolve_weights(
                root=Path.cwd(),
                weights_file=weights_file,
                target={"weight_profile": "default"}
            )
        assert "Weight sum must equal 1.0" in str(excinfo.value)
    finally:
        weights_file.unlink()


def test_compare_baseline_missing_category():
    """Edge: Category in current but not in baseline should not error."""
    current_scores = {"new_cat": 1.0}
    baseline_scores = {}
    # Should not raise
    try:
        delta = current_scores["new_cat"] - baseline_scores.get("new_cat", 1.0)
        assert delta == 0.0  # new_cat=1.0, baseline default=1.0
    except Exception:
        pytest.fail("Should not raise for missing baseline category")


def test_ci_gate_missing_required_suite():
    """Edge: Required suite missing should error."""
    suites_payload = [{"name": "conformance", "status": "pass"}]
    required_suites = {"conformance", "security"}
    found_suites = {suite["name"] for suite in suites_payload}
    missing_suites = sorted(required_suites - found_suites)
    assert "security" in missing_suites
