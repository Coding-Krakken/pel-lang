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
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class RuntimeConfig:
    """Runtime execution configuration."""
    mode: str  # "deterministic" or "monte_carlo"
    seed: int = 42
    num_runs: int = 1000  # For Monte Carlo
    time_horizon: Optional[int] = None  # Override model default


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
        self.rng = np.random.RandomState(config.seed)  # Seeded RNG
        random.seed(config.seed)
    
    def load_ir(self, ir_path: Path) -> Dict[str, Any]:
        """Load PEL-IR document."""
        with open(ir_path, 'r') as f:
            return json.load(f)
    
    def run(self, ir_document: Dict[str, Any]) -> Dict[str, Any]:
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
    
    def run_deterministic(self, ir_doc: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run single deterministic simulation.
        
        Distributions sampled at mean/median.
        """
        model = ir_doc["model"]
        state = {}  # Variable name -> value
        
        # Initialize parameters (sample distributions at mean)
        for node in model["nodes"]:
            if node["node_type"] == "param":
                value = self.evaluate_expression(node["value"], state, deterministic=True)
                state[node["name"]] = value
        
        # Determine time horizon
        T = self.config.time_horizon or model.get("time_horizon", 12)
        
        # Time loop
        timeseries_results = {node["name"]: [] for node in model["nodes"] if node["node_type"] == "var"}
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
                            "timesteps_completed": t,
                            "constraint_violations": constraint_violations,
                            "reason": f"Fatal constraint '{constraint['name']}' violated at t={t}"
                        }
            
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
            "mode": "deterministic",
            "seed": self.config.seed,
            "timesteps": T,
            "variables": timeseries_results,
            "constraint_violations": constraint_violations,
            "policy_executions": policy_executions
        }
    
    def run_monte_carlo(self, ir_doc: Dict[str, Any]) -> Dict[str, Any]:
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
    
    def evaluate_expression(self, expr: Dict[str, Any], state: Dict[str, Any], deterministic: bool = True) -> Any:
        """Evaluate IR expression (stub)."""
        expr_type = expr.get("expr_type")
        
        if expr_type == "Literal":
            return expr["literal_value"]
        
        elif expr_type == "Variable":
            var_name = expr["variable_name"]
            return state.get(var_name, 0)
        
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
            # Sample distribution
            dist = expr["distribution"]
            dist_type = dist["distribution_type"]
            params = dist["parameters"]
            
            if deterministic:
                # Sample at mean/median
                if dist_type == "Normal":
                    return params.get("mu", 0)
                elif dist_type == "LogNormal":
                    return params.get("mu", 1)  # Simplified
                elif dist_type == "Uniform":
                    low = params.get("low", 0)
                    high = params.get("high", 1)
                    return (low + high) / 2
            else:
                # Sample from distribution
                if dist_type == "Normal":
                    mu = params.get("mu", 0)
                    sigma = params.get("sigma", 1)
                    return self.rng.normal(mu, sigma)
                elif dist_type == "Uniform":
                    low = params.get("low", 0)
                    high = params.get("high", 1)
                    return self.rng.uniform(low, high)
        
        return 0  # Default
    
    def execute_action(self, action: Dict[str, Any], state: Dict[str, Any]):
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
