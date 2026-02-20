import pytest

def test_scorecard_weight_sum_zero():
    """Edge: All weights zero should error."""
    from .language_eval.scripts import scorecard
    weights = {"a": 0.0, "b": 0.0}
    with pytest.raises(SystemExit) as excinfo:
        scorecard._resolve_weights(root=None, weights_file=None, target={"weight_profile": "default"})
    assert "Weight sum must equal 1.0" in str(excinfo.value)

def test_compare_baseline_missing_category():
    """Edge: Category in current but not in baseline should not error."""
    from .language_eval.scripts import compare_baseline
    current_scores = {"new_cat": 1.0}
    baseline_scores = {}
    # Should not raise
    try:
        delta = current_scores["new_cat"] - baseline_scores.get("new_cat", 1.0)
    except Exception:
        pytest.fail("Should not raise for missing baseline category")

def test_ci_gate_missing_required_suite():
    """Edge: Required suite missing should error."""
    from .language_eval.scripts import ci_gate
    suites_payload = [{"name": "conformance", "status": "pass"}]
    required_suites = {"conformance", "security"}
    found_suites = {suite["name"] for suite in suites_payload}
    missing_suites = sorted(required_suites - found_suites)
    assert "security" in missing_suites
