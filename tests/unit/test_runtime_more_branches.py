from __future__ import annotations

import pytest

from runtime.runtime import PELRuntime, RuntimeConfig


@pytest.mark.unit
def test_runtime_evaluate_expression_binary_op_comparisons() -> None:
    runtime = PELRuntime(RuntimeConfig(mode="deterministic", seed=1))
    state = {}

    def eval_bin(op: str, left: int, right: int):
        return runtime.evaluate_expression(
            {
                "expr_type": "BinaryOp",
                "operator": op,
                "left": {"expr_type": "Literal", "literal_value": left},
                "right": {"expr_type": "Literal", "literal_value": right},
            },
            state,
        )

    assert eval_bin("==", 2, 2) is True
    assert eval_bin("<", 1, 2) is True
    assert eval_bin(">", 3, 2) is True


@pytest.mark.unit
def test_runtime_distribution_lognormal_and_uniform_deterministic_paths() -> None:
    runtime = PELRuntime(RuntimeConfig(mode="deterministic", seed=1))

    lognormal = {
        "expr_type": "Distribution",
        "distribution": {"distribution_type": "LogNormal", "parameters": {"mu": 7.0, "sigma": 2.0}},
    }
    assert runtime.evaluate_expression(lognormal, {}, deterministic=True) == 7.0

    uniform = {
        "expr_type": "Distribution",
        "distribution": {"distribution_type": "Uniform", "parameters": {"low": 10.0, "high": 14.0}},
    }
    assert runtime.evaluate_expression(uniform, {}, deterministic=True) == 12.0


@pytest.mark.unit
def test_runtime_distribution_uniform_stochastic_is_seeded() -> None:
    expr = {
        "expr_type": "Distribution",
        "distribution": {"distribution_type": "Uniform", "parameters": {"low": 0.0, "high": 1.0}},
    }

    r1 = PELRuntime(RuntimeConfig(mode="deterministic", seed=123))
    r2 = PELRuntime(RuntimeConfig(mode="deterministic", seed=123))

    v1 = r1.evaluate_expression(expr, {}, deterministic=False)
    v2 = r2.evaluate_expression(expr, {}, deterministic=False)

    assert v1 == v2
    assert 0.0 <= v1 <= 1.0


@pytest.mark.unit
def test_runtime_evaluate_expression_binary_op_sub_and_mul() -> None:
    runtime = PELRuntime(RuntimeConfig(mode="deterministic", seed=1))

    add = {
        "expr_type": "BinaryOp",
        "operator": "+",
        "left": {"expr_type": "Literal", "literal_value": 2},
        "right": {"expr_type": "Literal", "literal_value": 5},
    }
    assert runtime.evaluate_expression(add, {}) == 7

    sub = {
        "expr_type": "BinaryOp",
        "operator": "-",
        "left": {"expr_type": "Literal", "literal_value": 10},
        "right": {"expr_type": "Literal", "literal_value": 3},
    }
    assert runtime.evaluate_expression(sub, {}) == 7

    mul = {
        "expr_type": "BinaryOp",
        "operator": "*",
        "left": {"expr_type": "Literal", "literal_value": 6},
        "right": {"expr_type": "Literal", "literal_value": 7},
    }
    assert runtime.evaluate_expression(mul, {}) == 42


@pytest.mark.unit
def test_runtime_evaluate_expression_string_literal_preserved() -> None:
    runtime = PELRuntime(RuntimeConfig(mode="deterministic", seed=1))
    expr = {"expr_type": "Literal", "literal_value": "SMB", "literal_type": "string"}

    assert runtime.evaluate_expression(expr, {}) == "SMB"


@pytest.mark.unit
def test_runtime_evaluate_expression_string_equality_false_for_distinct_values() -> None:
    runtime = PELRuntime(RuntimeConfig(mode="deterministic", seed=1))
    expr = {
        "expr_type": "BinaryOp",
        "operator": "==",
        "left": {"expr_type": "Literal", "literal_value": "A", "literal_type": "string"},
        "right": {"expr_type": "Literal", "literal_value": "B", "literal_type": "string"},
    }

    assert runtime.evaluate_expression(expr, {}) is False


@pytest.mark.unit
def test_runtime_evaluate_expression_string_equality_true_for_same_values() -> None:
    runtime = PELRuntime(RuntimeConfig(mode="deterministic", seed=1))
    expr = {
        "expr_type": "BinaryOp",
        "operator": "==",
        "left": {"expr_type": "Literal", "literal_value": "A", "literal_type": "string"},
        "right": {"expr_type": "Literal", "literal_value": "A", "literal_type": "string"},
    }

    assert runtime.evaluate_expression(expr, {}) is True


@pytest.mark.unit
def test_runtime_evaluate_expression_unknown_expr_type_returns_zero() -> None:
    runtime = PELRuntime(RuntimeConfig(mode="deterministic", seed=1))
    assert runtime.evaluate_expression({"expr_type": "Nope"}, {}) == 0


@pytest.mark.unit
def test_runtime_evaluate_expression_binary_op_unknown_operator_falls_back_to_zero() -> None:
    runtime = PELRuntime(RuntimeConfig(mode="deterministic", seed=1))
    expr = {
        "expr_type": "BinaryOp",
        "operator": "@@",  # truly unknown operator
        "left": {"expr_type": "Literal", "literal_value": 1},
        "right": {"expr_type": "Literal", "literal_value": 2},
    }
    assert runtime.evaluate_expression(expr, {}) == 0


@pytest.mark.unit
def test_runtime_run_deterministic_initializes_params_into_state() -> None:
    runtime = PELRuntime(RuntimeConfig(mode="deterministic", seed=1, time_horizon=1))
    ir_doc = {
        "model": {
            "name": "m",
            "time_horizon": 1,
            "time_unit": "Month",
            "nodes": [
                {
                    "node_type": "param",
                    "name": "p",
                    "value": {"expr_type": "Literal", "literal_value": 1},
                },
                {"node_type": "var", "name": "v"},
            ],
            "constraints": [
                {
                    "name": "p_is_one",
                    "severity": "fatal",
                    "condition": {
                        "expr_type": "BinaryOp",
                        "operator": "==",
                        "left": {"expr_type": "Variable", "variable_name": "p"},
                        "right": {"expr_type": "Literal", "literal_value": 1},
                    },
                }
            ],
        }
    }

    result = runtime.run_deterministic(ir_doc)
    assert result["status"] == "success"
    assert result["constraint_violations"] == []


@pytest.mark.unit
def test_runtime_run_monte_carlo_samples_distribution_params_per_run() -> None:
    runtime = PELRuntime(RuntimeConfig(mode="monte_carlo", seed=123, num_runs=3, time_horizon=1))
    ir_doc = {
        "model": {
            "name": "mc",
            "time_horizon": 1,
            "time_unit": "Month",
            "nodes": [
                {
                    "node_type": "param",
                    "name": "d",
                    "value": {
                        "expr_type": "Distribution",
                        "dist_type": "Normal",
                        "params": {"mu": 10.0, "sigma": 1.0},
                    },
                    "provenance": {"source": "test", "method": "fitted", "confidence": 1.0},
                },
                {"node_type": "var", "name": "v"},
            ],
        }
    }

    result = runtime.run_monte_carlo(ir_doc)
    sampled_values = [run["assumptions"][0]["value"] for run in result["runs"]]

    assert result["status"] == "success"
    assert len(set(sampled_values)) > 1


@pytest.mark.unit
def test_runtime_run_monte_carlo_raises_for_invalid_correlation_coefficient() -> None:
    runtime = PELRuntime(RuntimeConfig(mode="monte_carlo", seed=123, num_runs=1, time_horizon=1))
    ir_doc = {
        "model": {
            "name": "mc",
            "time_horizon": 1,
            "time_unit": "Month",
            "nodes": [
                {
                    "node_type": "param",
                    "name": "a",
                    "value": {
                        "expr_type": "Distribution",
                        "dist_type": "Normal",
                        "params": {"mu": 0.0, "sigma": 1.0},
                    },
                    "provenance": {"correlated_with": ["b", 1.5]},
                },
                {
                    "node_type": "param",
                    "name": "b",
                    "value": {
                        "expr_type": "Distribution",
                        "dist_type": "Normal",
                        "params": {"mu": 0.0, "sigma": 1.0},
                    },
                },
                {"node_type": "var", "name": "v"},
            ],
        }
    }

    with pytest.raises(ValueError, match="Invalid correlation coefficient"):
        runtime.run_monte_carlo(ir_doc)


@pytest.mark.unit
def test_runtime_run_monte_carlo_raises_for_conflicting_correlation_values() -> None:
    runtime = PELRuntime(RuntimeConfig(mode="monte_carlo", seed=123, num_runs=1, time_horizon=1))
    ir_doc = {
        "model": {
            "name": "mc",
            "time_horizon": 1,
            "time_unit": "Month",
            "nodes": [
                {
                    "node_type": "param",
                    "name": "a",
                    "value": {
                        "expr_type": "Distribution",
                        "dist_type": "Normal",
                        "params": {"mu": 0.0, "sigma": 1.0},
                    },
                    "provenance": {"correlated_with": ["b", 0.0]},
                },
                {
                    "node_type": "param",
                    "name": "b",
                    "value": {
                        "expr_type": "Distribution",
                        "dist_type": "Normal",
                        "params": {"mu": 0.0, "sigma": 1.0},
                    },
                    "provenance": {"correlated_with": ["a", 0.2]},
                },
                {"node_type": "var", "name": "v"},
            ],
        }
    }

    with pytest.raises(ValueError, match="Conflicting correlation values"):
        runtime.run_monte_carlo(ir_doc)


@pytest.mark.unit
def test_runtime_run_monte_carlo_correlated_sampling_resolves_param_expressions() -> None:
    runtime = PELRuntime(RuntimeConfig(mode="monte_carlo", seed=123, num_runs=1, time_horizon=1))
    ir_doc = {
        "model": {
            "name": "mc",
            "time_horizon": 1,
            "time_unit": "Month",
            "nodes": [
                {
                    "node_type": "param",
                    "name": "base",
                    "value": {"expr_type": "Literal", "literal_value": 10.0},
                    "provenance": {"source": "test", "method": "given", "confidence": 1.0},
                },
                {
                    "node_type": "param",
                    "name": "a",
                    "value": {
                        "expr_type": "Distribution",
                        "dist_type": "Normal",
                        "params": {
                            "mu": {"expr_type": "Variable", "variable_name": "base"},
                            "sigma": 1.0,
                        },
                    },
                    "provenance": {
                        "source": "test",
                        "method": "fitted",
                        "confidence": 1.0,
                        "correlated_with": ["b", 0.5],
                    },
                },
                {
                    "node_type": "param",
                    "name": "b",
                    "value": {
                        "expr_type": "Distribution",
                        "dist_type": "Normal",
                        "params": {
                            "mu": {"expr_type": "Variable", "variable_name": "base"},
                            "sigma": 1.0,
                        },
                    },
                    "provenance": {"source": "test", "method": "fitted", "confidence": 1.0},
                },
                {"node_type": "var", "name": "v"},
            ],
        }
    }

    result = runtime.run_monte_carlo(ir_doc)
    assumptions = {item["name"]: item["value"] for item in result["runs"][0]["assumptions"]}

    assert result["status"] == "success"
    assert assumptions["base"] == 10.0
    assert assumptions["a"] > 5.0
    assert assumptions["b"] > 5.0
