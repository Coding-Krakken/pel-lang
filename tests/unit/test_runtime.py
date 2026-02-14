import pytest

from runtime.runtime import PELRuntime, RuntimeConfig


@pytest.mark.unit
def test_runtime_evaluate_expression_literal_and_variable() -> None:
    runtime = PELRuntime(RuntimeConfig(mode="deterministic", seed=42))
    state = {"x": 123}

    assert runtime.evaluate_expression({"expr_type": "Literal", "literal_value": 5}, state) == 5
    assert runtime.evaluate_expression({"expr_type": "Variable", "variable_name": "x"}, state) == 123


@pytest.mark.unit
def test_runtime_evaluate_expression_binary_op_div_by_zero_is_inf() -> None:
    runtime = PELRuntime(RuntimeConfig(mode="deterministic", seed=42))
    expr = {
        "expr_type": "BinaryOp",
        "operator": "/",
        "left": {"expr_type": "Literal", "literal_value": 1},
        "right": {"expr_type": "Literal", "literal_value": 0},
    }
    assert runtime.evaluate_expression(expr, {}) == float("inf")


@pytest.mark.unit
def test_runtime_run_deterministic_stops_on_fatal_constraint() -> None:
    runtime = PELRuntime(RuntimeConfig(mode="deterministic", seed=42, time_horizon=3))
    ir_doc = {
        "model": {
            "name": "m",
            "time_horizon": 3,
            "time_unit": "Month",
            "nodes": [
                {
                    "node_type": "var",
                    "name": "v",
                }
            ],
            "constraints": [
                {
                    "name": "always_false",
                    "severity": "fatal",
                    "condition": {"expr_type": "Literal", "literal_value": False},
                    "message": "nope",
                }
            ],
        }
    }

    result = runtime.run_deterministic(ir_doc)
    assert result["status"] == "failed"
    assert "Fatal constraint" in result["reason"]


@pytest.mark.unit
def test_runtime_run_dispatches_by_mode_and_rejects_unknown_mode() -> None:
    ir_doc = {"model": {"name": "m", "time_horizon": 1, "time_unit": "Month", "nodes": []}}

    runtime = PELRuntime(RuntimeConfig(mode="deterministic", seed=1, time_horizon=1))
    result = runtime.run(ir_doc)
    assert result["status"] in {"success", "failed"}

    runtime = PELRuntime(RuntimeConfig(mode="monte_carlo", seed=1, num_runs=1, time_horizon=1))
    result = runtime.run(ir_doc)
    assert result["status"] == "success"
    assert result["mode"] == "monte_carlo"

    runtime = PELRuntime(RuntimeConfig(mode="nope", seed=1))
    with pytest.raises(ValueError):
        runtime.run(ir_doc)


@pytest.mark.unit
def test_runtime_run_deterministic_records_warning_constraint_and_continues() -> None:
    runtime = PELRuntime(RuntimeConfig(mode="deterministic", seed=42, time_horizon=2))
    ir_doc = {
        "model": {
            "name": "m",
            "time_horizon": 2,
            "time_unit": "Month",
            "nodes": [
                {"node_type": "var", "name": "v"},
            ],
            "constraints": [
                {
                    "name": "always_false_warn",
                    "severity": "warning",
                    "condition": {"expr_type": "Literal", "literal_value": False},
                    "message": "warn",
                }
            ],
        }
    }

    result = runtime.run_deterministic(ir_doc)
    assert result["status"] == "success"
    assert result["timesteps"] == 2
    assert len(result["constraint_violations"]) == 2
    assert {v["severity"] for v in result["constraint_violations"]} == {"warning"}


@pytest.mark.unit
def test_runtime_policies_execute_assign_action() -> None:
    runtime = PELRuntime(RuntimeConfig(mode="deterministic", seed=42, time_horizon=1))
    ir_doc = {
        "model": {
            "name": "m",
            "time_horizon": 1,
            "time_unit": "Month",
            "nodes": [
                {"node_type": "var", "name": "v"},
            ],
            "policies": [
                {
                    "name": "set_x",
                    "trigger": {"condition": {"expr_type": "Literal", "literal_value": True}},
                    "action": {
                        "action_type": "assign",
                        "target": "x",
                        "value": {"expr_type": "Literal", "literal_value": 7},
                    },
                }
            ],
        }
    }

    result = runtime.run_deterministic(ir_doc)
    assert result["status"] == "success"
    assert result["policy_executions"] == [{"timestep": 0, "policy": "set_x"}]


@pytest.mark.unit
def test_runtime_distribution_sampling_deterministic_and_stochastic_paths() -> None:
    expr = {
        "expr_type": "Distribution",
        "distribution": {
            "distribution_type": "Normal",
            "parameters": {"mu": 3.0, "sigma": 2.0},
        },
    }

    runtime = PELRuntime(RuntimeConfig(mode="deterministic", seed=123))
    assert runtime.evaluate_expression(expr, {}, deterministic=True) == 3.0

    runtime1 = PELRuntime(RuntimeConfig(mode="deterministic", seed=123))
    runtime2 = PELRuntime(RuntimeConfig(mode="deterministic", seed=123))
    v1 = runtime1.evaluate_expression(expr, {}, deterministic=False)
    v2 = runtime2.evaluate_expression(expr, {}, deterministic=False)
    assert v1 == v2


@pytest.mark.unit
def test_runtime_run_monte_carlo_success_rate_and_run_list_truncation() -> None:
    ir_doc = {"model": {"name": "m", "time_horizon": 1, "time_unit": "Month", "nodes": []}}
    runtime = PELRuntime(RuntimeConfig(mode="monte_carlo", seed=1, num_runs=3, time_horizon=1))
    result = runtime.run_monte_carlo(ir_doc)

    assert result["status"] == "success"
    assert result["mode"] == "monte_carlo"
    assert result["num_runs"] == 3
    assert result["aggregates"]["success_rate"] == 1.0
    assert len(result["runs"]) == 3
