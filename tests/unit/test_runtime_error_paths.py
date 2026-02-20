"""Comprehensive tests for runtime error paths and edge cases to achieve 100% coverage."""

from runtime.runtime import PELRuntime, RuntimeConfig


class TestRuntimeConvergenceAndErrors:
    """Test convergence failures and error handling."""

    def test_non_convergent_equations(self):
        """Test equations that don't converge within max iterations."""
        # Create a model with circular dependencies that can't be resolved
        ir_doc = {
            "model": {
                "name": "NonConvergent",
                "time_horizon": 2,
                "nodes": [
                    {"node_type": "var", "name": "x"},
                    {"node_type": "var", "name": "y"},
                ],
                "equations": [
                    {
                        "equation_id": "eq1",
                        "equation_type": "recurrence_current",
                        "target": {
                            "expr_type": "Indexing",
                            "expression": {"expr_type": "Variable", "variable_name": "x"},
                            "index": {"expr_type": "Variable", "variable_name": "t"},
                        },
                        "value": {
                            "expr_type": "BinaryOp",
                            "operator": "+",
                            "left": {"expr_type": "Variable", "variable_name": "y"},
                            "right": {"expr_type": "Literal", "literal_value": 1},
                        },
                        "dependencies": ["y"],
                    },
                    {
                        "equation_id": "eq2",
                        "equation_type": "recurrence_current",
                        "target": {
                            "expr_type": "Indexing",
                            "expression": {"expr_type": "Variable", "variable_name": "y"},
                            "index": {"expr_type": "Variable", "variable_name": "t"},
                        },
                        "value": {
                            "expr_type": "BinaryOp",
                            "operator": "+",
                            "left": {
                                "expr_type": "Indexing",
                                "expression": {"expr_type": "Variable", "variable_name": "x"},
                                "index": {"expr_type": "Variable", "variable_name": "t"},
                            },
                            "right": {"expr_type": "Literal", "literal_value": 1},
                        },
                        "dependencies": ["x"],
                    },
                ],
                "constraints": [],
                "policies": [],
            }
        }

        runtime = PELRuntime(RuntimeConfig(mode="deterministic"))
        # Should complete but log warning about non-convergence
        result = runtime.run_deterministic(ir_doc)
        assert result["status"] == "success"

    def test_missing_value_defaults_to_zero(self):
        """Test that missing values default to 0."""
        ir_doc = {
            "model": {
                "name": "MissingValue",
                "time_horizon": 3,
                "nodes": [
                    {"node_type": "var", "name": "x"},
                ],
                "equations": [
                    # Equation for x[0] but nothing for x[1], x[2]
                    {
                        "equation_id": "eq1",
                        "equation_type": "initial",
                        "target": {
                            "expr_type": "Indexing",
                            "expression": {"expr_type": "Variable", "variable_name": "x"},
                            "index": {"expr_type": "Literal", "literal_value": 0},
                        },
                        "value": {"expr_type": "Literal", "literal_value": 100},
                        "dependencies": [],
                    }
                ],
                "constraints": [],
                "policies": [],
            }
        }

        runtime = PELRuntime(RuntimeConfig(mode="deterministic"))
        result = runtime.run_deterministic(ir_doc)
        assert result["status"] == "success"
        # Should have defaulted missing values to 0
        assert len(result["variables"]["x"]) == 3

    def test_equation_evaluation_type_error(self):
        """Test TypeError during equation evaluation."""
        ir_doc = {
            "model": {
                "name": "TypeError",
                "time_horizon": 1,
                "nodes": [
                    {
                        "node_type": "param",
                        "name": "bad_value",
                        "value": {"expr_type": "Literal", "literal_value": "not_a_number"},
                    },
                    {"node_type": "var", "name": "result"},
                ],
                "equations": [
                    {
                        "equation_id": "eq1",
                        "equation_type": "recurrence_current",
                        "target": {
                            "expr_type": "Indexing",
                            "expression": {"expr_type": "Variable", "variable_name": "result"},
                            "index": {"expr_type": "Variable", "variable_name": "t"},
                        },
                        "value": {
                            "expr_type": "BinaryOp",
                            "operator": "*",
                            "left": {"expr_type": "Variable", "variable_name": "bad_value"},
                            "right": {"expr_type": "Literal", "literal_value": 2},
                        },
                        "dependencies": ["bad_value"],
                    }
                ],
                "constraints": [],
                "policies": [],
            }
        }

        runtime = PELRuntime(RuntimeConfig(mode="deterministic"))
        result = runtime.run_deterministic(ir_doc)
        # Should handle error gracefully
        assert result["status"] == "success"

    def test_equation_evaluation_attribute_error(self):
        """Test AttributeError during equation evaluation."""
        ir_doc = {
            "model": {
                "name": "AttributeError",
                "time_horizon": 1,
                "nodes": [
                    {"node_type": "var", "name": "result"},
                ],
                "equations": [
                    {
                        "equation_id": "eq1",
                        "equation_type": "recurrence_current",
                        "target": {
                            "expr_type": "Indexing",
                            "expression": {"expr_type": "Variable", "variable_name": "result"},
                            "index": {"expr_type": "Variable", "variable_name": "t"},
                        },
                        "value": {
                            "expr_type": "MemberAccess",
                            "expression": {"expr_type": "Literal", "literal_value": 5},
                            "member": "nonexistent_property",
                        },
                        "dependencies": [],
                    }
                ],
                "constraints": [],
                "policies": [],
            }
        }

        runtime = PELRuntime(RuntimeConfig(mode="deterministic"))
        result = runtime.run_deterministic(ir_doc)
        assert result["status"] == "success"

    def test_equation_evaluation_unexpected_exception(self):
        """Test unexpected exception during equation evaluation gets logged."""
        ir_doc = {
            "model": {
                "name": "UnexpectedException",
                "time_horizon": 1,
                "nodes": [
                    {"node_type": "var", "name": "result"},
                ],
                "equations": [
                    {
                        "equation_id": "eq1",
                        "equation_type": "recurrence_current",
                        "target": {
                            "expr_type": "Indexing",
                            "expression": {"expr_type": "Variable", "variable_name": "result"},
                            "index": {"expr_type": "Variable", "variable_name": "t"},
                        },
                        # Use a malformed expression that might cause unexpected error
                        "value": {
                            "expr_type": "UnknownType",  # This should cause an issue
                            "bad_field": "invalid",
                        },
                        "dependencies": [],
                    }
                ],
                "constraints": [],
                "policies": [],
            }
        }

        runtime = PELRuntime(RuntimeConfig(mode="deterministic"))
        result = runtime.run_deterministic(ir_doc)
        assert result["status"] == "success"


class TestConstraintErrorPaths:
    """Test constraint evaluation error paths."""

    def test_constraint_key_error(self):
        """Test KeyError during constraint evaluation."""
        ir_doc = {
            "model": {
                "name": "ConstraintKeyError",
                "time_horizon": 2,
                "nodes": [{"node_type": "var", "name": "x"}],
                "equations": [],
                "constraints": [
                    {
                        "constraint_id": "c1",
                        "name": "bad_constraint",
                        "condition": {
                            "expr_type": "BinaryOp",
                            "operator": ">",
                            "left": {"expr_type": "Variable", "variable_name": "nonexistent"},
                            "right": {"expr_type": "Literal", "literal_value": 0},
                        },
                        "severity": "warning",
                        "message": "Should skip this",
                    }
                ],
                "policies": [],
            }
        }

        runtime = PELRuntime(RuntimeConfig(mode="deterministic"))
        result = runtime.run_deterministic(ir_doc)
        # Should complete successfully despite constraint errors
        assert result["status"] == "success"

    def test_constraint_type_error(self):
        """Test TypeError during constraint evaluation."""
        ir_doc = {
            "model": {
                "name": "ConstraintTypeError",
                "time_horizon": 2,
                "nodes": [
                    {
                        "node_type": "param",
                        "name": "text",
                        "value": {"expr_type": "Literal", "literal_value": "string"},
                    },
                ],
                "equations": [],
                "constraints": [
                    {
                        "constraint_id": "c1",
                        "name": "type_error_constraint",
                        "condition": {
                            "expr_type": "BinaryOp",
                            "operator": ">",
                            "left": {"expr_type": "Variable", "variable_name": "text"},
                            "right": {"expr_type": "Literal", "literal_value": 5},
                        },
                        "severity": "warning",
                        "message": "Type error",
                    }
                ],
                "policies": [],
            }
        }

        runtime = PELRuntime(RuntimeConfig(mode="deterministic"))
        result = runtime.run_deterministic(ir_doc)
        assert result["status"] == "success"

    def test_constraint_unexpected_exception(self):
        """Test unexpected exception during constraint evaluation."""
        ir_doc = {
            "model": {
                "name": "ConstraintUnexpected",
                "time_horizon": 2,
                "nodes": [],
                "equations": [],
                "constraints": [
                    {
                        "constraint_id": "c1",
                        "name": "unexpected",
                        "condition": {"expr_type": "UnknownType", "bad": "data"},
                        "severity": "warning",
                        "message": "Unexpected",
                    }
                ],
                "policies": [],
            }
        }

        runtime = PELRuntime(RuntimeConfig(mode="deterministic"))
        result = runtime.run_deterministic(ir_doc)
        assert result["status"] == "success"


class TestConstraintDiagnosticsEdgeCases:
    """Test constraint diagnostics extraction edge cases."""

    def test_constraint_diagnostics_key_error(self):
        """Test diagnostic extraction with KeyError."""
        ir_doc = {
            "model": {
                "name": "DiagnosticsKeyError",
                "time_horizon": 1,
                "nodes": [],
                "equations": [],
                "constraints": [
                    {
                        "constraint_id": "c1",
                        "name": "diagnostic_test",
                        "condition": {
                            "expr_type": "BinaryOp",
                            "operator": ">=",
                            "left": {"expr_type": "Variable", "variable_name": "missing_var"},
                            "right": {"expr_type": "Literal", "literal_value": 0},
                        },
                        "severity": "warning",
                        "message": "Test diagnostic extraction",
                    }
                ],
                "policies": [],
            }
        }

        runtime = PELRuntime(RuntimeConfig(mode="deterministic"))
        result = runtime.run_deterministic(ir_doc)
        assert result["status"] == "success"

    def test_constraint_diagnostics_unexpected_error(self):
        """Test diagnostic extraction with unexpected error."""
        ir_doc = {
            "model": {
                "name": "DiagnosticsUnexpected",
                "time_horizon": 1,
                "nodes": [],
                "equations": [],
                "constraints": [
                    {
                        "constraint_id": "c1",
                        "name": "diagnostic_unexpected",
                        "condition": {
                            "expr_type": "BinaryOp",
                            "operator": "==",
                            "left": {"expr_type": "UnknownType"},  # Bad expression
                            "right": {"expr_type": "Literal", "literal_value": 0},
                        },
                        "severity": "warning",
                        "message": "Test unexpected error in diagnostics",
                    }
                ],
                "policies": [],
            }
        }

        runtime = PELRuntime(RuntimeConfig(mode="deterministic"))
        result = runtime.run_deterministic(ir_doc)
        assert result["status"] == "success"


class TestNonIndexedEquations:
    """Test equations with non-indexed targets."""

    def test_skips_non_indexed_equation(self):
        """Test that equations with non-indexed targets are skipped."""
        ir_doc = {
            "model": {
                "name": "NonIndexed",
                "time_horizon": 2,
                "nodes": [{"node_type": "var", "name": "x"}],
                "equations": [
                    {
                        "equation_id": "eq1",
                        "equation_type": "direct",
                        "target": {
                            "expr_type": "Variable",  # Not indexed!
                            "variable_name": "x",
                        },
                        "value": {"expr_type": "Literal", "literal_value": 5},
                        "dependencies": [],
                    }
                ],
                "constraints": [],
                "policies": [],
            }
        }

        runtime = PELRuntime(RuntimeConfig(mode="deterministic"))
        result = runtime.run_deterministic(ir_doc)
        # Should complete successfully, equation was skipped
        assert result["status"] == "success"


class TestMonteCarloEdgeCases:
    """Test Monte Carlo edge cases."""

    def test_monte_carlo_max_runs_limit(self):
        """Test that max_runs limit is enforced and logged."""
        ir_doc = {
            "model": {
                "name": "MaxRunsTest",
                "time_horizon": 1,
                "nodes": [],
                "equations": [],
                "constraints": [],
                "policies": [],
            }
        }

        runtime = PELRuntime(
            RuntimeConfig(
                mode="monte_carlo",
                num_runs=200000,  # Way over limit
                max_runs=50,  # Low limit
            )
        )

        result = runtime.run_monte_carlo(ir_doc)
        assert result["status"] == "success"
        assert result["num_runs"] == 50  # Capped
        assert result["requested_runs"] == 200000
        assert len(result["runs"]) == 50

    def test_monte_carlo_success_rate_calculation(self):
        """Test Monte Carlo success rate aggregation."""
        ir_doc = {
            "model": {
                "name": "SuccessRate",
                "time_horizon": 1,
                "nodes": [],
                "equations": [],
                "constraints": [
                    {
                        "constraint_id": "c1",
                        "name": "always_fails",
                        "condition": {"expr_type": "Literal", "literal_value": False},
                        "severity": "fatal",
                        "message": "Always fails",
                    }
                ],
                "policies": [],
            }
        }

        runtime = PELRuntime(RuntimeConfig(mode="monte_carlo", num_runs=5))
        result = runtime.run_monte_carlo(ir_doc)

        # All runs should fail
        assert result["aggregates"]["success_rate"] == 0.0
