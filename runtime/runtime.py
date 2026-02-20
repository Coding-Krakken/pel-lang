# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""
PEL Runtime - Execute compiled PEL-IR models
Reference implementation v0.1.0
"""

import argparse
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast


@dataclass
class RuntimeConfig:
    """Runtime execution configuration."""
    mode: str  # "deterministic" or "monte_carlo"
    seed: int = 42
    num_runs: int = 1000  # For Monte Carlo
    time_horizon: int | None = None  # Override model default


class PELRuntime:
    """
    PEL-Core conformant runtime.

    Supports:
    - Deterministic execution (distributions sampled at mean/median)
    - Constraint checking (fatal stops, warning logs)
    - Policy execution
    - Reproducible results (seeded PRNG)
    """

    def __init__(self, config: RuntimeConfig):
        self.config = config
        self.rng = random.Random(config.seed)

    def load_ir(self, ir_path: Path) -> dict[str, Any]:
        """Load PEL-IR document."""
        with open(ir_path) as f:
            return cast(dict[str, Any], json.load(f))

    def run(self, ir_document: dict[str, Any]) -> dict[str, Any]:
        """
        Execute model.

        Returns:
            Results dict with outputs, constraint violations, policy executions
        """
        if self.config.mode == "deterministic":
            return self.run_deterministic(ir_document)
        elif self.config.mode == "monte_carlo":
            return self.run_monte_carlo(ir_document)
        else:
            raise ValueError(f"Unknown mode: {self.config.mode}")

    def run_deterministic(
        self,
        ir_doc: dict[str, Any],
        deterministic: bool = True,
        sampled_params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Run single deterministic simulation.

        Distributions sampled at mean/median.
        """
        model = ir_doc["model"]
        model_name = model.get("name", "Unknown")
        state: dict[str, Any] = {}  # Variable name -> value

        # Initialize parameters (sample distributions at mean)
        assumptions = []
        sampled_params = sampled_params or {}
        for node in model["nodes"]:
            if node["node_type"] == "param":
                if node["name"] in sampled_params:
                    value = sampled_params[node["name"]]
                else:
                    value = self.evaluate_expression(node["value"], state, deterministic=deterministic)
                state[node["name"]] = value

                # Collect assumption/provenance data
                if "provenance" in node:
                    prov = node["provenance"]
                    assumptions.append({
                        "name": node["name"],
                        "value": value,
                        "source": prov.get("source", "unknown"),
                        "method": prov.get("method", "unknown"),
                        "confidence": prov.get("confidence", 0)
                    })

        # Determine time horizon
        T = self.config.time_horizon or model.get("time_horizon") or 12

        # Initialize timeseries result storage
        timeseries_results: dict[str, list[Any]] = {}
        for node in model["nodes"]:
            if node["node_type"] == "var":
                timeseries_results[node["name"]] = []
        
        constraint_violations = []
        policy_executions = []
        events = []

        # Get equations from model
        equations = model.get("equations", [])
        
        # Organize equations by type and target variable
        initial_eqs: dict[str, dict] = {}
        recurrence_eqs: dict[str, dict] = {}
        current_eqs: dict[str, dict] = {}
        
        for eq in equations:
            target_var = None
            if eq["target"]["expr_type"] == "Indexing":
                target_var = eq["target"]["expression"]["variable_name"]
            
            if eq["equation_type"] == "initial":
                initial_eqs[target_var] = eq
            elif eq["equation_type"] == "recurrence_next":
                recurrence_eqs[target_var] = eq
            elif eq["equation_type"] in ("recurrence_current", "direct"):
                current_eqs[target_var] = eq

        # Time loop
        for t in range(T):
            # Add timestep to state
            state["t"] = t
            
            # At t=0, evaluate initial conditions first
            if t == 0:
                for var_name, eq in initial_eqs.items():
                    value = self.evaluate_expression(eq["value"], state, deterministic=deterministic)
                    timeseries_results[var_name].append(value)
            
            # Update state with timeseries arrays (for indexing like customers[t])
            for var_name, results in timeseries_results.items():
                state[var_name] = results
            
            # Evaluate current timestep equations (revenue[t] = customers[t] * price)
            # May need multiple passes if there are dependencies between current equations
            max_iterations = 10
            for iteration in range(max_iterations):
                any_updated = False
                for var_name, eq in current_eqs.items():
                    # Check if this variable already has a value for this timestep
                    if t < len(timeseries_results[var_name]):
                        continue  # Already evaluated
                    
                    try:
                        value = self.evaluate_expression(eq["value"], state, deterministic=deterministic)
                        if value is not None and not (isinstance(value, float) and (value != value)):  # Check for NaN
                            timeseries_results[var_name].append(value)
                            state[var_name] = timeseries_results[var_name]
                            any_updated = True
                    except Exception:
                        # Skip if we can't evaluate yet (missing dependencies)
                        continue
                
                if not any_updated:
                    break  # All equations evaluated or can't make progress
            
            # Fill in any missing values with 0
            for var_name in timeseries_results:
                if var_name not in initial_eqs and var_name not in current_eqs and var_name not in recurrence_eqs:
                    # This is a scalar variable, not a timeseries
                    continue
                if t >= len(timeseries_results[var_name]):
                    # This shouldn't happen, but add a default value to prevent errors
                    timeseries_results[var_name].append(0)
            
            # Update state again after evaluating current equations
            for var_name, results in timeseries_results.items():
                state[var_name] = results

            # Check constraints
            ordered_constraints = sorted(
                model.get("constraints", []),
                key=lambda c: (str(c.get("name", "")), str(c.get("constraint_id", ""))),
            )
            for constraint in ordered_constraints:
                # Check if this constraint applies to this timestep
                # For now, we check all constraints at all timesteps
                # TODO: Parse constraint "for" clauses to determine when to check
                try:
                    condition_value = self.evaluate_expression(constraint["condition"], state)
                    if not condition_value:
                        # Extract diagnostic information from the constraint
                        diagnostics = self._extract_constraint_diagnostics(constraint["condition"], state)
                        
                        violation = {
                            "timestep": t,
                            "constraint": constraint["name"],
                            "severity": constraint["severity"],
                            "message": constraint.get("message", "Constraint violated")
                        }
                        
                        # Add diagnostic information to violation
                        if diagnostics:
                            violation.update(diagnostics)
                        
                        constraint_violations.append(violation)

                        if constraint["severity"] == "fatal":
                            # Stop simulation
                            return {
                                "status": "failed",
                                "model": {"name": model_name},
                                "timesteps_completed": t,
                                "constraint_violations": constraint_violations,
                                "assumptions": assumptions,
                                "reason": f"Fatal constraint '{constraint['name']}' violated at t={t}"
                            }
                except Exception:
                    # Skip constraints that can't be evaluated (e.g., out of bounds indexing)
                    pass

            # Execute policies
            for policy in model.get("policies", []):
                trigger_value = self.evaluate_expression(policy["trigger"]["condition"], state)
                if trigger_value:
                    # Execute action
                    action_result = self.execute_action(policy["action"], state)
                    policy_executions.append({
                        "timestep": t,
                        "policy": policy["name"]
                    })
                    # Collect events emitted by policy
                    if action_result and "events" in action_result:
                        events.extend(action_result["events"])
            
            # Evaluate recurrence equations for next timestep (customers[t+1] = ...)
            if t < T - 1:  # Don't compute beyond time horizon
                for var_name, eq in recurrence_eqs.items():
                    value = self.evaluate_expression(eq["value"], state, deterministic=deterministic)
                    timeseries_results[var_name].append(value)

        return {
            "status": "success",
            "model": {"name": model_name},
            "mode": "deterministic",
            "seed": self.config.seed,
            "timesteps": T,
            "variables": timeseries_results,
            "constraint_violations": constraint_violations,
            "policy_executions": policy_executions,
            "events": events,
            "assumptions": assumptions
        }

    def run_monte_carlo(self, ir_doc: dict[str, Any]) -> dict[str, Any]:
        """
        Run Monte Carlo simulation.

        Distributions sampled from full distribution with correlation.
        """
        model = ir_doc["model"]
        correlated_names, correlation_matrix = self._extract_correlation_spec(model)

        runs = []
        for i in range(self.config.num_runs):
            # Create new config with different seed
            run_config = RuntimeConfig(
                mode="deterministic",
                seed=self.config.seed + i,
                time_horizon=self.config.time_horizon
            )
            runtime = PELRuntime(run_config)

            sampled_params: dict[str, Any] = {}
            if correlated_names:
                sampled_params = runtime._sample_correlated_parameter_values(
                    model,
                    correlated_names,
                    correlation_matrix,
                )

            result = runtime.run_deterministic(
                ir_doc,
                deterministic=False,
                sampled_params=sampled_params,
            )
            runs.append(result)

        # Aggregate results
        return {
            "status": "success",
            "mode": "monte_carlo",
            "num_runs": self.config.num_runs,
            "base_seed": self.config.seed,
            "runs": runs,  # Include all runs (not just first 10)
            "aggregates": {
                "success_rate": sum(1 for r in runs if r["status"] == "success") / len(runs)
            }
        }

    def _extract_correlation_spec(self, model: dict[str, Any]) -> tuple[list[str], list[list[float]]]:
        """Extract and validate Normal-parameter correlation matrix from provenance metadata."""
        normal_params: dict[str, dict[str, Any]] = {}

        for node in model.get("nodes", []):
            if node.get("node_type") != "param":
                continue
            value = node.get("value", {})
            if not isinstance(value, dict) or value.get("expr_type") != "Distribution":
                continue
            dist_type = self._distribution_type(value)
            if dist_type in ("Normal", "normal"):
                normal_params[node["name"]] = node

        if len(normal_params) < 2:
            return [], []

        names = list(normal_params.keys())
        index = {name: i for i, name in enumerate(names)}
        size = len(names)
        matrix = [[0.0 for _ in range(size)] for _ in range(size)]
        seen_pairs: dict[tuple[str, str], float] = {}
        for i in range(size):
            matrix[i][i] = 1.0

        for name, node in normal_params.items():
            provenance = node.get("provenance") or {}
            if not isinstance(provenance, dict):
                continue
            for other_name, corr in self._parse_correlated_with(provenance.get("correlated_with")):
                if other_name not in index:
                    continue
                i = index[name]
                j = index[other_name]
                if i == j:
                    continue
                if corr < -1.0 or corr > 1.0:
                    raise ValueError(
                        f"Invalid correlation coefficient {corr} between '{name}' and '{other_name}'"
                    )
                if name <= other_name:
                    pair: tuple[str, str] = (name, other_name)
                else:
                    pair = (other_name, name)
                existing = seen_pairs.get(pair)
                if existing is not None and abs(existing - corr) > 1e-9:
                    raise ValueError(
                        f"Conflicting correlation values for '{name}' and '{other_name}'"
                    )
                seen_pairs[pair] = corr
                matrix[i][j] = corr
                matrix[j][i] = corr

        has_off_diagonal = any(
            i != j and matrix[i][j] != 0.0
            for i in range(size)
            for j in range(size)
        )
        if not has_off_diagonal:
            return [], []

        self._validate_correlation_matrix(matrix)
        return names, matrix

    def _distribution_type(self, expr: dict[str, Any]) -> str | None:
        """Read distribution type from either current or legacy IR shapes."""
        if "distribution" in expr and isinstance(expr["distribution"], dict):
            return cast(str | None, expr["distribution"].get("distribution_type"))
        return cast(str | None, expr.get("dist_type"))

    def _distribution_params(self, expr: dict[str, Any]) -> dict[str, Any]:
        """Read distribution params from either current or legacy IR shapes."""
        if "distribution" in expr and isinstance(expr["distribution"], dict):
            return cast(dict[str, Any], expr["distribution"].get("parameters", {}))
        return cast(dict[str, Any], expr.get("params", {}))

    def _parse_correlated_with(self, correlated_with: Any) -> list[tuple[str, float]]:
        """Parse provenance correlated_with metadata.

        Supported forms:
        - ["other_param", 0.4]
        - [["p1", 0.4], ["p2", -0.2]]
        """
        parsed: list[tuple[str, float]] = []

        if not isinstance(correlated_with, list):
            return parsed

        # Single pair form
        if (
            len(correlated_with) == 2
            and isinstance(correlated_with[0], str)
            and isinstance(correlated_with[1], (int, float))
        ):
            parsed.append((correlated_with[0], float(correlated_with[1])))
            return parsed

        # List of pairs
        for item in correlated_with:
            if (
                isinstance(item, list)
                and len(item) == 2
                and isinstance(item[0], str)
                and isinstance(item[1], (int, float))
            ):
                parsed.append((item[0], float(item[1])))

        return parsed

    def _validate_correlation_matrix(self, matrix: list[list[float]]) -> None:
        """Validate correlation matrix shape, symmetry, and positive semidefiniteness."""
        size = len(matrix)
        if size == 0:
            return
        for row in matrix:
            if len(row) != size:
                raise ValueError("Correlation matrix must be square")

        for i in range(size):
            if abs(matrix[i][i] - 1.0) > 1e-9:
                raise ValueError("Correlation matrix diagonal entries must be 1.0")
            for j in range(size):
                if abs(matrix[i][j] - matrix[j][i]) > 1e-9:
                    raise ValueError("Correlation matrix must be symmetric")
                if matrix[i][j] < -1.0 or matrix[i][j] > 1.0:
                    raise ValueError("Correlation coefficients must be within [-1, 1]")

        self._cholesky_decomposition(matrix)

    def _cholesky_decomposition(self, matrix: list[list[float]]) -> list[list[float]]:
        """Compute Cholesky decomposition and fail for non-PSD matrices."""
        size = len(matrix)
        lower = [[0.0 for _ in range(size)] for _ in range(size)]

        for i in range(size):
            for j in range(i + 1):
                acc = sum(lower[i][k] * lower[j][k] for k in range(j))

                if i == j:
                    diagonal = matrix[i][i] - acc
                    if diagonal < -1e-12:
                        raise ValueError("Correlation matrix must be positive semidefinite")
                    lower[i][j] = math.sqrt(max(diagonal, 0.0))
                else:
                    if abs(lower[j][j]) < 1e-12:
                        lower[i][j] = 0.0
                    else:
                        lower[i][j] = (matrix[i][j] - acc) / lower[j][j]

        return lower

    def _sample_correlated_parameter_values(
        self,
        model: dict[str, Any],
        names: list[str],
        matrix: list[list[float]],
    ) -> dict[str, float]:
        """Sample correlated Normal parameters using Cholesky transform."""
        lower = self._cholesky_decomposition(matrix)
        independent = [self.rng.gauss(0.0, 1.0) for _ in names]

        correlated_standard = []
        for i in range(len(names)):
            correlated_standard.append(sum(lower[i][k] * independent[k] for k in range(i + 1)))

        nodes_by_name = {
            node["name"]: node
            for node in model.get("nodes", [])
            if node.get("node_type") == "param"
        }
        param_state: dict[str, Any] = {}
        for node in model.get("nodes", []):
            if node.get("node_type") != "param":
                continue
            value_expr = node.get("value")
            if isinstance(value_expr, dict):
                param_state[node["name"]] = self.evaluate_expression(value_expr, param_state, deterministic=True)

        sampled: dict[str, float] = {}

        for i, name in enumerate(names):
            node = nodes_by_name.get(name)
            if not node:
                continue

            value = cast(dict[str, Any], node.get("value", {}))
            params = self._distribution_params(value)
            resolved_params: dict[str, Any] = {}
            for param_name, param_expr in params.items():
                if isinstance(param_expr, dict) and "expr_type" in param_expr:
                    resolved_params[param_name] = self.evaluate_expression(param_expr, param_state, deterministic=True)
                else:
                    resolved_params[param_name] = param_expr

            mu = float(resolved_params.get("μ", resolved_params.get("mu", 0.0)))
            sigma = float(resolved_params.get("σ", resolved_params.get("sigma", 1.0)))
            sampled[name] = mu + sigma * correlated_standard[i]

        return sampled

    def evaluate_expression(self, expr: dict[str, Any], state: dict[str, Any], deterministic: bool = True) -> Any:
        """Evaluate IR expression (stub)."""
        expr_type = expr.get("expr_type")


        if expr_type == "Literal":
            literal_value = expr["literal_value"]
            literal_type = expr.get("literal_type", "unknown")

            # Handle currency literals - parse string to number
            if literal_type == "currency" and isinstance(literal_value, str):
                # Remove $ and underscores, convert to float
                numeric_str = literal_value.replace("$", "").replace("_", "").strip()
                return float(numeric_str)

            # Handle other literals
            if isinstance(literal_value, (int, float)):
                return literal_value

            if literal_type == "string" and isinstance(literal_value, str):
                return literal_value

            # Try to convert string numbers to float
            if isinstance(literal_value, str):
                try:
                    return float(literal_value.replace("_", ""))
                except ValueError:
                    return literal_value

            return literal_value

        elif expr_type == "Variable":
            var_name = expr["variable_name"]
            return state.get(var_name, 0)

        elif expr_type == "Indexing":
            # Handle array/timeseries indexing like profit[12]
            base_expr = expr["expression"]
            index_expr = expr["index"]

            base_value = self.evaluate_expression(base_expr, state, deterministic)
            index_value = self.evaluate_expression(index_expr, state, deterministic)

            # If base is a list/array, index into it
            if isinstance(base_value, list) and isinstance(index_value, int):
                if 0 <= index_value < len(base_value):
                    return base_value[index_value]
                else:
                    return 0  # Out of bounds

            return 0

        elif expr_type == "BinaryOp":
            left = self.evaluate_expression(expr["left"], state, deterministic)
            right = self.evaluate_expression(expr["right"], state, deterministic)
            op = expr["operator"]

            if op == "+":
                return left + right
            elif op == "-":
                return left - right
            elif op == "*":
                return left * right
            elif op == "/":
                return left / right if right != 0 else float('inf')
            elif op == "%":
                return left % right if right != 0 else 0
            elif op == "==":
                return left == right
            elif op == "!=":
                return left != right
            elif op == "<":
                return left < right
            elif op == "<=":
                return left <= right
            elif op == ">":
                return left > right
            elif op == ">=":
                return left >= right
            elif op in ("&&", "and"):
                return left and right
            elif op in ("||", "or"):
                return left or right
            else:
                # Unknown operator
                return 0

        elif expr_type == "UnaryOp":
            operand = self.evaluate_expression(expr["operand"], state, deterministic)
            operator = expr.get("operator")
            if operator == "-":
                return -operand
            if operator == "+":
                return +operand
            if operator in ("!", "not"):
                return not operand

        elif expr_type == "IfThenElse":
            condition = self.evaluate_expression(expr["condition"], state, deterministic)
            if condition:
                return self.evaluate_expression(expr["then_expr"], state, deterministic)
            return self.evaluate_expression(expr["else_expr"], state, deterministic)

        elif expr_type == "ArrayLiteral":
            return [self.evaluate_expression(element, state, deterministic) for element in expr.get("elements", [])]

        elif expr_type == "FunctionCall":
            function_name = expr.get("function_name", "")
            args = [self.evaluate_expression(arg, state, deterministic) for arg in expr.get("arguments", [])]

            if function_name == "min" and args:
                return min(args)
            if function_name == "max" and args:
                return max(args)
            if function_name == "abs" and len(args) == 1:
                return abs(args[0])
            if function_name == "round" and args:
                if len(args) == 1:
                    return round(args[0])
                return round(args[0], int(args[1]))
            if function_name == "pow" and len(args) == 2:
                return args[0] ** args[1]
            if function_name == "sum" and len(args) == 1 and isinstance(args[0], list):
                return sum(args[0])
            if function_name == "len" and len(args) == 1:
                return len(args[0])

        elif expr_type == "MemberAccess":
            base = self.evaluate_expression(expr["expression"], state, deterministic)
            member = expr.get("member")
            if member == "length" and isinstance(base, list):
                return len(base)

        elif expr_type == "Distribution":
            # Support both legacy IR shape and current IR shape.
            # Legacy: expr["distribution"] = {"distribution_type": ..., "parameters": {...}}
            # Current: expr["dist_type"] and expr["params"]
            if "distribution" in expr:
                dist = expr["distribution"]
                dist_type = dist.get("distribution_type")
                params = dist.get("parameters", {})
            else:
                dist_type = expr.get("dist_type")
                params = expr.get("params", {})

            # Resolve parameters: they may be raw values or expression nodes
            resolved_params = {}
            for param_name, param_expr in params.items():
                if isinstance(param_expr, dict) and "expr_type" in param_expr:
                    resolved_params[param_name] = self.evaluate_expression(param_expr, state, deterministic)
                else:
                    resolved_params[param_name] = param_expr

            # Normalize common parameter names (allow μ/mu, σ/sigma)
            if "mu" in resolved_params and "μ" not in resolved_params:
                resolved_params["μ"] = resolved_params["mu"]
            if "sigma" in resolved_params and "σ" not in resolved_params:
                resolved_params["σ"] = resolved_params["sigma"]

            # Deterministic: return mean/median
            if deterministic:
                if dist_type in ("Normal", "normal"):
                    return resolved_params.get("μ", resolved_params.get("mu", 0))
                if dist_type in ("Beta", "beta"):
                    alpha = resolved_params.get("α", resolved_params.get("alpha", 1))
                    beta = resolved_params.get("β", resolved_params.get("beta", 1))
                    return alpha / (alpha + beta)
                if dist_type in ("LogNormal", "lognormal"):
                    return resolved_params.get("μ", resolved_params.get("mu", 0))
                if dist_type in ("Uniform", "uniform"):
                    low = resolved_params.get("low", resolved_params.get("a", 0))
                    high = resolved_params.get("high", resolved_params.get("b", low))
                    return (low + high) / 2.0
                # Triangular etc. could be added here
                # Fallback
                return 0

            # Stochastic sampling
            if dist_type in ("Normal", "normal"):
                mu = resolved_params.get("μ", resolved_params.get("mu", 0))
                sigma = resolved_params.get("σ", resolved_params.get("sigma", 1))
                return self.rng.gauss(mu, sigma)
            if dist_type in ("Beta", "beta"):
                alpha = resolved_params.get("α", resolved_params.get("alpha", 1))
                beta = resolved_params.get("β", resolved_params.get("beta", 1))
                return self.rng.betavariate(alpha, beta)
            if dist_type in ("LogNormal", "lognormal"):
                mu = resolved_params.get("μ", resolved_params.get("mu", 0))
                sigma = resolved_params.get("σ", resolved_params.get("sigma", 1))
                return self.rng.lognormvariate(mu, sigma)
            if dist_type in ("Uniform", "uniform"):
                low = resolved_params.get("low", resolved_params.get("a", 0))
                high = resolved_params.get("high", resolved_params.get("b", low))
                return self.rng.uniform(low, high)

            return 0

        elif expr_type == "PerDurationExpression":
            # Evaluate PerDurationExpression: returns value per duration unit
            # For now, evaluate the left expression and return it directly
            # Duration conversion would be handled by the type system
            left_value = self.evaluate_expression(expr["left"], state, deterministic)
            return left_value

        return 0  # Default

    def _extract_constraint_diagnostics(self, condition: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
        """Extract diagnostic information from a constraint condition for actionable error messages.
        
        For comparison operators (<=, >=, <, >, ==, !=), extract the actual values
        being compared and calculate the violation amount.
        """
        diagnostics = {}
        
        expr_type = condition.get("expr_type")
        if expr_type == "BinaryOp":
            operator = condition.get("operator")
            # Only process comparison operators
            if operator in ("<=", ">=", "<", ">", "==", "!="):
                try:
                    left_value = self.evaluate_expression(condition.get("left", {}), state)
                    right_value = self.evaluate_expression(condition.get("right", {}), state)
                    
                    diagnostics["actual_value"] = left_value
                    diagnostics["expected_value"] = right_value
                    diagnostics["operator"] = operator
                    
                    # Calculate violation amount for numeric comparisons
                    if isinstance(left_value, (int, float)) and isinstance(right_value, (int, float)):
                        if operator in ("<=", "<"):
                            # left should be <= right, but it's not
                            # violation_amount is how much left exceeds right
                            diagnostics["violation_amount"] = left_value - right_value
                        elif operator in (">=", ">"):
                            # left should be >= right, but it's not
                            # violation_amount is how much left falls short of right
                            diagnostics["violation_amount"] = right_value - left_value
                        elif operator == "==":
                            diagnostics["violation_amount"] = abs(left_value - right_value)
                
                except Exception:
                    # If we can't evaluate, skip diagnostics
                    pass
        
        return diagnostics
    
    def execute_action(self, action: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
        """Execute policy action and return any events emitted."""
        action_type = action.get("action_type")
        events = []

        if action_type == "assign":
            target = action.get("target")
            value_expr = action.get("value", {})
            if target:
                value = self.evaluate_expression(value_expr, state)
                state[target] = value
        
        elif action_type == "block":
            # Execute a block of statements sequentially
            statements = action.get("statements", [])
            for stmt in statements:
                result = self.execute_action(stmt, state)
                if result and "events" in result:
                    events.extend(result["events"])
        
        elif action_type == "emit_event":
            # Event emission - capture for reporting
            event_name = action.get("event_name", "unnamed_event")
            event_args = action.get("args", {})
            # Evaluate any expressions in event args
            evaluated_args = {}
            for key, val in event_args.items():
                if isinstance(val, dict) and "expr_type" in val:
                    evaluated_args[key] = self.evaluate_expression(val, state)
                else:
                    evaluated_args[key] = val
            events.append({
                "name": event_name,
                "args": evaluated_args,
                "timestep": state.get("t", -1)
            })
        
        return {"events": events}


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="PEL Runtime - Execute compiled PEL-IR models"
    )

    # Add subcommands
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Run command (default execution)
    run_parser = subparsers.add_parser('run', help='Execute a PEL-IR model')
    run_parser.add_argument('ir_file', type=Path, help='Compiled .ir.json file')
    run_parser.add_argument('--mode', choices=['deterministic', 'monte_carlo'], default='deterministic',
                       help='Execution mode')
    run_parser.add_argument('--seed', type=int, default=42, help='Random seed')
    run_parser.add_argument('--runs', type=int, default=1000, help='Number of Monte Carlo runs')
    run_parser.add_argument('--time-horizon', type=int, help='Override model time horizon')
    run_parser.add_argument('-o', '--output', type=Path, help='Output JSON file')

    # Calibrate command
    calibrate_parser = subparsers.add_parser('calibrate', help='Calibrate model with data')
    calibrate_parser.add_argument('config_file', type=Path, help='Calibration config YAML file')
    calibrate_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    # Handle commands
    if args.command == 'calibrate':
        # Import calibration module (optional dependency)
        try:
            from runtime.calibration import CalibrationConfig, Calibrator
        except ImportError:
            print("Error: Calibration module not available.")
            print("Install with: pip install pel-lang[calibration]")
            return 1

        # Load config and run calibration
        try:
            config = CalibrationConfig.from_yaml(args.config_file)
            calibrator = Calibrator(config)

            print("Starting calibration...")
            print(f"  Model: {config.model_path}")
            print(f"  Data: {config.csv_path}")
            print()

            result = calibrator.calibrate()

            print("Calibration completed successfully!")
            print()
            print("Fitted parameters:")
            for param_name, fit in result.parameters.items():
                print(f"  {param_name} ({fit.distribution}):")
                for pname, pvalue in fit.parameters.items():
                    ci = fit.confidence_intervals[pname]
                    print(f"    {pname}: {pvalue:.6f} (95% CI: [{ci[0]:.6f}, {ci[1]:.6f}])")

            if result.drift_reports:
                print()
                print("Drift detection:")
                for param_name, report in result.drift_reports.items():
                    print(f"  {param_name}: MAPE={report.mape:.2%}, " +
                          f"CUSUM={'detected' if report.cusum_detected else 'not detected'}")

            if config.output_path:
                print()
                print(f"Reports saved to: {config.output_path}")

            return 0

        except Exception as e:
            print(f"Error during calibration: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            return 1

    elif args.command == 'run' or args.command is None:
        # Default: run model
        if args.command is None:
            # No subcommand provided - show help and exit
            parser.print_help()
            return 0

        # Configure runtime
        config = RuntimeConfig(
            mode=args.mode,
            seed=args.seed,
            num_runs=args.runs,
            time_horizon=args.time_horizon
        )

        runtime = PELRuntime(config)

        # Load and execute
        ir_doc = runtime.load_ir(args.ir_file)
        results = runtime.run(ir_doc)

        # Output
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"Results written to {args.output}")
        else:
            print(json.dumps(results, indent=2))

        return 0

    else:
        parser.print_help()
        return 0


if __name__ == '__main__':
    main()
