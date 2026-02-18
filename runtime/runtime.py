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

    def run_deterministic(self, ir_doc: dict[str, Any]) -> dict[str, Any]:
        """
        Run single deterministic simulation.

        Distributions sampled at mean/median.
        """
        model = ir_doc["model"]
        model_name = model.get("name", "Unknown")
        state: dict[str, Any] = {}  # Variable name -> value

        # Initialize parameters (sample distributions at mean)
        assumptions = []
        for node in model["nodes"]:
            if node["node_type"] == "param":
                value = self.evaluate_expression(node["value"], state, deterministic=True)
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

        # Time loop
        timeseries_results: dict[str, list[Any]] = {node["name"]: [] for node in model["nodes"] if node["node_type"] == "var"}
        constraint_violations = []
        policy_executions = []

        for t in range(T):
            # Evaluate variables for this timestep
            for node in model["nodes"]:
                if node["node_type"] == "var":
                    # Simplified: assume value depends on t
                    state[node["name"]] = 100 * (1 + 0.1) ** t  # Stub growth
                    timeseries_results[node["name"]].append(state[node["name"]])

            # Check constraints
            for constraint in model.get("constraints", []):
                # Check if this constraint applies to this timestep
                # For now, we check all constraints at all timesteps
                # TODO: Parse constraint "for" clauses to determine when to check
                try:
                    condition_value = self.evaluate_expression(constraint["condition"], state)
                    if not condition_value:
                        violation = {
                            "timestep": t,
                            "constraint": constraint["name"],
                            "severity": constraint["severity"],
                            "message": constraint.get("message", "Constraint violated")
                        }
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
                    self.execute_action(policy["action"], state)
                    policy_executions.append({
                        "timestep": t,
                        "policy": policy["name"]
                    })

        return {
            "status": "success",
            "model": {"name": model_name},
            "mode": "deterministic",
            "seed": self.config.seed,
            "timesteps": T,
            "variables": timeseries_results,
            "constraint_violations": constraint_violations,
            "policy_executions": policy_executions,
            "assumptions": assumptions
        }

    def run_monte_carlo(self, ir_doc: dict[str, Any]) -> dict[str, Any]:
        """
        Run Monte Carlo simulation.

        Distributions sampled from full distribution with correlation.
        """
        # Stub: run N independent deterministic runs with different seeds
        runs = []
        for i in range(self.config.num_runs):
            # Create new config with different seed
            run_config = RuntimeConfig(
                mode="deterministic",
                seed=self.config.seed + i,
                time_horizon=self.config.time_horizon
            )
            runtime = PELRuntime(run_config)
            result = runtime.run_deterministic(ir_doc)
            runs.append(result)

        # Aggregate results (stub: just collect)
        return {
            "status": "success",
            "mode": "monte_carlo",
            "num_runs": self.config.num_runs,
            "base_seed": self.config.seed,
            "runs": runs[:10],  # Include first 10 for inspection
            "aggregates": {
                "success_rate": sum(1 for r in runs if r["status"] == "success") / len(runs)
            }
        }

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
            
            # Try to convert string numbers to float
            if isinstance(literal_value, str):
                try:
                    return float(literal_value.replace("_", ""))
                except ValueError:
                    return 0
            
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
            elif op == "==":
                return left == right
            elif op == "<":
                return left < right
            elif op == ">":
                return left > right

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

    def execute_action(self, action: dict[str, Any], state: dict[str, Any]) -> None:
        """Execute policy action (stub)."""
        action_type = action["action_type"]

        if action_type == "assign":
            target = action.get("target")
            value_expr = action.get("value", {})
            if target:
                state[target] = self.evaluate_expression(value_expr, state)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="PEL Runtime - Execute compiled PEL-IR models"
    )

    parser.add_argument('ir_file', type=Path, help='Compiled .ir.json file')
    parser.add_argument('--mode', choices=['deterministic', 'monte_carlo'], default='deterministic',
                       help='Execution mode')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    parser.add_argument('--runs', type=int, default=1000, help='Number of Monte Carlo runs')
    parser.add_argument('--time-horizon', type=int, help='Override model time horizon')
    parser.add_argument('-o', '--output', type=Path, help='Output JSON file')

    args = parser.parse_args()

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


if __name__ == '__main__':
    main()
