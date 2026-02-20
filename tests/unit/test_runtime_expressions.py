"""Additional runtime expression evaluation coverage tests."""

from runtime.runtime import PELRuntime, RuntimeConfig


class TestRuntimeExpressionEvaluation:
    """Test all expression evaluation code paths."""

    def test_unary_op_negation(self):
        """Test unary negation operator."""
        ir_doc = {
            "model": {
                "name": "UnaryNeg",
                "time_horizon": 1,
                "nodes": [
                    {
                        "node_type": "param",
                        "name": "x",
                        "value": {"expr_type": "Literal", "literal_value": 10},
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
                            "expr_type": "UnaryOp",
                            "operator": "-",
                            "operand": {"expr_type": "Variable", "variable_name": "x"},
                        },
                        "dependencies": ["x"],
                    }
                ],
                "constraints": [],
                "policies": [],
            }
        }

        runtime = PELRuntime(RuntimeConfig(mode="deterministic"))
        result = runtime.run_deterministic(ir_doc)
        assert result["status"] == "success"
        assert result["variables"]["result"][0] == -10

    def test_binary_op_power(self):
        """Test power operator."""
        ir_doc = {
            "model": {
                "name": "Power",
                "time_horizon": 1,
                "nodes": [{"node_type": "var", "name": "result"}],
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
                            "operator": "^",
                            "left": {"expr_type": "Literal", "literal_value": 2},
                            "right": {"expr_type": "Literal", "literal_value": 3},
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
        assert result["variables"]["result"][0] == 8

    def test_binary_op_modulo(self):
        """Test modulo operator."""
        ir_doc = {
            "model": {
                "name": "Modulo",
                "time_horizon": 1,
                "nodes": [{"node_type": "var", "name": "result"}],
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
                            "operator": "%",
                            "left": {"expr_type": "Literal", "literal_value": 10},
                            "right": {"expr_type": "Literal", "literal_value": 3},
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
        assert result["variables"]["result"][0] == 1

    def test_comparison_operators(self):
        """Test various comparison operators."""
        for op, expected in [
            ("==", True),
            ("!=", False),
            ("<", False),
            (">", False),
            ("<=", True),
            (">=", True),
        ]:
            ir_doc = {
                "model": {
                    "name": f"Compare{op}",
                    "time_horizon": 1,
                    "nodes": [{"node_type": "var", "name": "result"}],
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
                                "operator": op,
                                "left": {"expr_type": "Literal", "literal_value": 5},
                                "right": {"expr_type": "Literal", "literal_value": 5},
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
            assert result["variables"]["result"][0] == expected

    def test_logical_and_operator(self):
        """Test logical AND operator."""
        ir_doc = {
            "model": {
                "name": "LogicalAnd",
                "time_horizon": 1,
                "nodes": [{"node_type": "var", "name": "result"}],
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
                            "operator": "and",
                            "left": {"expr_type": "Literal", "literal_value": True},
                            "right": {"expr_type": "Literal", "literal_value": False},
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
        assert result["variables"]["result"][0] is False

    def test_logical_or_operator(self):
        """Test logical OR operator."""
        ir_doc = {
            "model": {
                "name": "LogicalOr",
                "time_horizon": 1,
                "nodes": [{"node_type": "var", "name": "result"}],
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
                            "operator": "or",
                            "left": {"expr_type": "Literal", "literal_value": False},
                            "right": {"expr_type": "Literal", "literal_value": True},
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
        assert result["variables"]["result"][0] is True

    def test_ternary_expression(self):
        """Test ternary conditional expression."""
        ir_doc = {
            "model": {
                "name": "Ternary",
                "time_horizon": 1,
                "nodes": [{"node_type": "var", "name": "result"}],
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
                            "expr_type": "Ternary",
                            "condition": {"expr_type": "Literal", "literal_value": True},
                            "true_value": {"expr_type": "Literal", "literal_value": 100},
                            "false_value": {"expr_type": "Literal", "literal_value": 0},
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
        assert result["variables"]["result"][0] == 100

    def test_ternary_false_branch(self):
        """Test ternary false branch."""
        ir_doc = {
            "model": {
                "name": "TernaryFalse",
                "time_horizon": 1,
                "nodes": [{"node_type": "var", "name": "result"}],
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
                            "expr_type": "Ternary",
                            "condition": {"expr_type": "Literal", "literal_value": False},
                            "true_value": {"expr_type": "Literal", "literal_value": 100},
                            "false_value": {"expr_type": "Literal", "literal_value": 0},
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
        assert result["variables"]["result"][0] == 0

    def test_function_call_max(self):
        """Test Max function call."""
        ir_doc = {
            "model": {
                "name": "MaxFunc",
                "time_horizon": 1,
                "nodes": [{"node_type": "var", "name": "result"}],
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
                            "expr_type": "FunctionCall",
                            "function_name": "Max",
                            "arguments": [
                                {"expr_type": "Literal", "literal_value": 10},
                                {"expr_type": "Literal", "literal_value": 20},
                            ],
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
        assert result["variables"]["result"][0] == 20

    def test_function_call_min(self):
        """Test Min function call."""
        ir_doc = {
            "model": {
                "name": "MinFunc",
                "time_horizon": 1,
                "nodes": [{"node_type": "var", "name": "result"}],
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
                            "expr_type": "FunctionCall",
                            "function_name": "Min",
                            "arguments": [
                                {"expr_type": "Literal", "literal_value": 10},
                                {"expr_type": "Literal", "literal_value": 20},
                            ],
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
        assert result["variables"]["result"][0] == 10

    def test_function_call_abs(self):
        """Test Abs function call."""
        ir_doc = {
            "model": {
                "name": "AbsFunc",
                "time_horizon": 1,
                "nodes": [{"node_type": "var", "name": "result"}],
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
                            "expr_type": "FunctionCall",
                            "function_name": "Abs",
                            "arguments": [{"expr_type": "Literal", "literal_value": -15}],
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
        assert result["variables"]["result"][0] == 15

    def test_function_call_sqrt(self):
        """Test Sqrt function call."""
        ir_doc = {
            "model": {
                "name": "SqrtFunc",
                "time_horizon": 1,
                "nodes": [{"node_type": "var", "name": "result"}],
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
                            "expr_type": "FunctionCall",
                            "function_name": "Sqrt",
                            "arguments": [{"expr_type": "Literal", "literal_value": 16}],
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
        assert result["variables"]["result"][0] == 4

    def test_list_comprehension_expression(self):
        """Test list comprehension evaluation."""
        ir_doc = {
            "model": {
                "name": "ListComp",
                "time_horizon": 3,
                "nodes": [
                    {
                        "node_type": "param",
                        "name": "data",
                        "value": {
                            "expr_type": "List",
                            "elements": [
                                {"expr_type": "Literal", "literal_value": 1},
                                {"expr_type": "Literal", "literal_value": 2},
                                {"expr_type": "Literal", "literal_value": 3},
                            ],
                        },
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
                            "expr_type": "FunctionCall",
                            "function_name": "Sum",
                            "arguments": [{"expr_type": "Variable", "variable_name": "data"}],
                        },
                        "dependencies": ["data"],
                    }
                ],
                "constraints": [],
                "policies": [],
            }
        }

        runtime = PELRuntime(RuntimeConfig(mode="deterministic"))
        result = runtime.run_deterministic(ir_doc)
        assert result["status"] == "success"
