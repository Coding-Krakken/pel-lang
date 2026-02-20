"""Comprehensive tests for CLI and main() function to achieve 100% coverage."""

import json
import os
import tempfile
from unittest.mock import patch

import pytest

from runtime.runtime import main


class TestMainFunctionNoCommand:
    """Test main() when no command is provided."""

    @patch("sys.argv", ["pel"])
    @patch("runtime.runtime.argparse.ArgumentParser.print_help")
    def test_main_no_command_shows_help(self, mock_help):
        """Test that main() shows help when no command provided."""
        result = main()
        assert result == 0
        mock_help.assert_called_once()


class TestMainRunCommand:
    """Test main() with 'run' command."""

    def test_main_run_deterministic(self):
        """Test running a model in deterministic mode."""
        # Create a simple IR file
        ir_doc = {
            "model": {
                "name": "CLITest",
                "time_horizon": 2,
                "nodes": [{"node_type": "var", "name": "x"}],
                "equations": [],
                "constraints": [],
                "policies": [],
            }
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            ir_path = os.path.join(tmpdir, "test.ir.json")
            output_path = os.path.join(tmpdir, "output.json")

            with open(ir_path, "w") as f:
                json.dump(ir_doc, f)

            with patch("sys.argv", ["pel", "run", ir_path, "-o", output_path]):
                result = main()

            assert result == 0
            assert os.path.exists(output_path)

            with open(output_path) as f:
                output = json.load(f)
                assert output["status"] == "success"

    def test_main_run_monte_carlo(self):
        """Test running a model in Monte Carlo mode."""
        ir_doc = {
            "model": {
                "name": "MCTest",
                "time_horizon": 1,
                "nodes": [],
                "equations": [],
                "constraints": [],
                "policies": [],
            }
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            ir_path = os.path.join(tmpdir, "mc.ir.json")
            with open(ir_path, "w") as f:
                json.dump(ir_doc, f)

            with patch("sys.argv", ["pel", "run", ir_path, "--mode", "monte_carlo", "--runs", "5"]):
                with patch("sys.stdout"):
                    result = main()

            assert result == 0

    def test_main_run_with_seed(self):
        """Test running with specific random seed."""
        ir_doc = {
            "model": {
                "name": "SeedTest",
                "time_horizon": 1,
                "nodes": [],
                "equations": [],
                "constraints": [],
                "policies": [],
            }
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            ir_path = os.path.join(tmpdir, "seed.ir.json")
            with open(ir_path, "w") as f:
                json.dump(ir_doc, f)

            with patch("sys.argv", ["pel", "run", ir_path, "--seed", "42"]):
                with patch("sys.stdout"):
                    result = main()

            assert result == 0

    def test_main_run_custom_time_horizon(self):
        """Test running with custom time horizon."""
        ir_doc = {
            "model": {
                "name": "HorizonTest",
                "time_horizon": 5,
                "nodes": [],
                "equations": [],
                "constraints": [],
                "policies": [],
            }
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            ir_path = os.path.join(tmpdir, "horizon.ir.json")
            with open(ir_path, "w") as f:
                json.dump(ir_doc, f)

            with patch("sys.argv", ["pel", "run", ir_path, "--time-horizon", "10"]):
                with patch("sys.stdout"):
                    result = main()

            assert result == 0

    def test_main_run_output_to_stdout(self):
        """Test running without output file (prints to stdout)."""
        ir_doc = {
            "model": {
                "name": "StdoutTest",
                "time_horizon": 1,
                "nodes": [],
                "equations": [],
                "constraints": [],
                "policies": [],
            }
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            ir_path = os.path.join(tmpdir, "stdout.ir.json")
            with open(ir_path, "w") as f:
                json.dump(ir_doc, f)

            with patch("sys.argv", ["pel", "run", ir_path]):
                with patch("sys.stdout"):
                    result = main()

            assert result == 0


class TestMainUnknownCommand:
    """Test main() with unknown command."""

    @patch("runtime.runtime.argparse.ArgumentParser.print_help")
    def test_main_unknown_command_shows_help(self, mock_help):
        """Test that unknown command shows help."""
        with patch("sys.argv", ["pel", "unknown_command"]):
            with pytest.raises(SystemExit):
                main()


class TestCLIArgumentParsing:
    """Test CLI argument parsing edge cases."""

    def test_run_all_arguments(self):
        """Test run command with all possible arguments."""
        ir_doc = {
            "model": {
                "name": "AllArgs",
                "time_horizon": 5,
                "nodes": [],
                "equations": [],
                "constraints": [],
                "policies": [],
            }
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            ir_path = os.path.join(tmpdir, "all_args.ir.json")
            output_path = os.path.join(tmpdir, "output.json")

            with open(ir_path, "w") as f:
                json.dump(ir_doc, f)

            argv = [
                "pel",
                "run",
                ir_path,
                "--mode",
                "monte_carlo",
                "--runs",
                "10",
                "--seed",
                "123",
                "--time-horizon",
                "7",
                "-o",
                output_path,
            ]

            with patch("sys.argv", argv):
                result = main()

            assert result == 0
            assert os.path.exists(output_path)


class TestMainIntegration:
    """Integration tests for main() function."""

    def test_full_deterministic_workflow(self):
        """Test complete deterministic workflow through CLI."""
        ir_doc = {
            "model": {
                "name": "FullDeterministic",
                "time_horizon": 3,
                "nodes": [
                    {
                        "node_type": "param",
                        "name": "initial",
                        "value": {"expr_type": "Literal", "literal_value": 100},
                    },
                    {"node_type": "var", "name": "x"},
                ],
                "equations": [
                    {
                        "equation_id": "eq1",
                        "equation_type": "initial",
                        "target": {
                            "expr_type": "Indexing",
                            "expression": {"expr_type": "Variable", "variable_name": "x"},
                            "index": {"expr_type": "Literal", "literal_value": 0},
                        },
                        "value": {"expr_type": "Variable", "variable_name": "initial"},
                        "dependencies": ["initial"],
                    },
                    {
                        "equation_id": "eq2",
                        "equation_type": "recurrence",
                        "target": {
                            "expr_type": "Indexing",
                            "expression": {"expr_type": "Variable", "variable_name": "x"},
                            "index": {
                                "expr_type": "BinaryOp",
                                "operator": "+",
                                "left": {"expr_type": "Variable", "variable_name": "t"},
                                "right": {"expr_type": "Literal", "literal_value": 1},
                            },
                        },
                        "value": {
                            "expr_type": "BinaryOp",
                            "operator": "*",
                            "left": {
                                "expr_type": "Indexing",
                                "expression": {"expr_type": "Variable", "variable_name": "x"},
                                "index": {"expr_type": "Variable", "variable_name": "t"},
                            },
                            "right": {"expr_type": "Literal", "literal_value": 1.1},
                        },
                        "dependencies": ["x"],
                    },
                ],
                "constraints": [],
                "policies": [],
            }
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            ir_path = os.path.join(tmpdir, "workflow.ir.json")
            output_path = os.path.join(tmpdir, "result.json")

            with open(ir_path, "w") as f:
                json.dump(ir_doc, f)

            with patch("sys.argv", ["pel", "run", ir_path, "-o", output_path]):
                result = main()

            assert result == 0

            with open(output_path) as f:
                output = json.load(f)
                assert output["status"] == "success"
                assert "x" in output["variables"]
                assert len(output["variables"]["x"]) == 3

    def test_full_monte_carlo_workflow(self):
        """Test complete Monte Carlo workflow through CLI."""
        ir_doc = {
            "model": {
                "name": "FullMonteCarlo",
                "time_horizon": 2,
                "nodes": [
                    {
                        "node_type": "param",
                        "name": "random_param",
                        "value": {
                            "expr_type": "FunctionCall",
                            "function_name": "Normal",
                            "arguments": [
                                {"expr_type": "Literal", "literal_value": 100},
                                {"expr_type": "Literal", "literal_value": 10},
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
                        "value": {"expr_type": "Variable", "variable_name": "random_param"},
                        "dependencies": ["random_param"],
                    }
                ],
                "constraints": [],
                "policies": [],
            }
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            ir_path = os.path.join(tmpdir, "mc_workflow.ir.json")
            output_path = os.path.join(tmpdir, "mc_result.json")

            with open(ir_path, "w") as f:
                json.dump(ir_doc, f)

            with patch(
                "sys.argv",
                [
                    "pel",
                    "run",
                    ir_path,
                    "--mode",
                    "monte_carlo",
                    "--runs",
                    "20",
                    "--seed",
                    "42",
                    "-o",
                    output_path,
                ],
            ):
                result = main()

            assert result == 0

            with open(output_path) as f:
                output = json.load(f)
                assert output["status"] == "success"
                assert output["num_runs"] == 20
                assert len(output["runs"]) == 20
