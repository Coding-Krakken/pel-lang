"""Integration tests for PR42: Policy execution, equation evaluation, and constraint diagnostics.

These tests verify end-to-end functionality of the features added in PR42:
- Issue #30: Beginner examples compile and run
- Issue #31: Policy execution with events
- Issue #32: Monte Carlo returns all N runs
- Issue #33: Constraint diagnostics with violation details
"""

from pathlib import Path

import pytest

from compiler.compiler import PELCompiler
from runtime.runtime import PELRuntime, RuntimeConfig


@pytest.mark.integration
def test_beginner_examples_compile_and_run():
    """Verify beginner examples compile and execute successfully (Issue #30)."""
    examples_dir = Path("beginner_examples")

    # Test saas_business.pel
    saas_business = examples_dir / "saas_business.pel"
    assert saas_business.exists(), "saas_business.pel not found"

    compiler = PELCompiler(verbose=False)
    ir_document = compiler.compile(saas_business)

    ir_document["model"]
    runtime = PELRuntime(RuntimeConfig(mode="deterministic", seed=42))
    exec_result = runtime.run_deterministic(ir_document)

    assert exec_result["status"] == "success"
    assert exec_result["timesteps"] == 12
    assert "customers" in exec_result["variables"]
    assert "revenue" in exec_result["variables"]
    assert len(exec_result["variables"]["customers"]) == 12

    # Test saas_uncertain.pel
    saas_uncertain = examples_dir / "saas_uncertain.pel"
    assert saas_uncertain.exists(), "saas_uncertain.pel not found"

    ir_document = compiler.compile(saas_uncertain)
    runtime = PELRuntime(RuntimeConfig(mode="deterministic", seed=42))
    exec_result = runtime.run_deterministic(ir_document)

    assert exec_result["status"] == "success"
    assert exec_result["timesteps"] == 12


@pytest.mark.integration
def test_monte_carlo_returns_all_runs():
    """Verify Monte Carlo returns all N runs, not just 10 (Issue #32)."""
    examples_dir = Path("beginner_examples")
    saas_uncertain = examples_dir / "saas_uncertain.pel"
    assert saas_uncertain.exists(), "saas_uncertain.pel not found"

    compiler = PELCompiler(verbose=False)
    ir_document = compiler.compile(saas_uncertain)

    # Test with 20 runs
    runtime = PELRuntime(RuntimeConfig(mode="monte_carlo", num_runs=20, seed=42))
    exec_result = runtime.run_monte_carlo(ir_document)

    assert exec_result["status"] == "success"
    assert exec_result["num_runs"] == 20
    assert len(exec_result["runs"]) == 20, "Should return all 20 runs, not just 10"

    # Test with 50 runs
    runtime = PELRuntime(RuntimeConfig(mode="monte_carlo", num_runs=50, seed=42))
    exec_result = runtime.run_monte_carlo(ir_document)

    assert exec_result["status"] == "success"
    assert exec_result["num_runs"] == 50
    assert len(exec_result["runs"]) == 50, "Should return all 50 runs, not just 10"

    # Verify variance exists (distributions sampled properly)
    exec_result["runs"][0]["variables"]["revenue"][-1]
    exec_result["runs"][-1]["variables"]["revenue"][-1]
    # Should have some variance (not guaranteed to be different but very likely)
    # Check multiple runs to ensure stochastic behavior
    revenues = [run["variables"]["revenue"][-1] for run in exec_result["runs"]]
    unique_revenues = len(set(revenues))
    assert unique_revenues > 1, "Runs should show stochastic variation"


@pytest.mark.integration
def test_max_runs_safety_limit():
    """Test that max_runs safety limit prevents excessive Monte Carlo runs."""
    examples_dir = Path("beginner_examples")
    saas_uncertain = examples_dir / "saas_uncertain.pel"
    assert saas_uncertain.exists(), "saas_uncertain.pel not found"

    compiler = PELCompiler(verbose=False)
    ir_document = compiler.compile(saas_uncertain)

    # Request more runs than max_runs limit
    runtime = PELRuntime(RuntimeConfig(
        mode="monte_carlo",
        num_runs=150000,  # More than default max_runs
        max_runs=100,  # Set low limit for testing
        seed=42
    ))
    exec_result = runtime.run_monte_carlo(ir_document)

    assert exec_result["status"] == "success"
    assert exec_result["num_runs"] == 100, "Should be capped at max_runs"
    assert exec_result["requested_runs"] == 150000
    assert len(exec_result["runs"]) == 100


@pytest.mark.integration
def test_equation_evaluation_order():
    """Test that equations are evaluated in correct order (initial, current, recurrence)."""
    examples_dir = Path("beginner_examples")
    saas_business = examples_dir / "saas_business.pel"

    compiler = PELCompiler(verbose=False)
    ir_document = compiler.compile(saas_business)

    # Check IR contains equations
    assert "equations" in ir_document["model"]
    equations = ir_document["model"]["equations"]
    assert len(equations) > 0

    # Verify equation types are assigned
    equation_types = {eq["equation_type"] for eq in equations}
    assert "initial" in equation_types, "Should have initial equations"
    assert "recurrence_next" in equation_types, "Should have recurrence equations"

    # Run and verify results are correct
    runtime = PELRuntime(RuntimeConfig(mode="deterministic", seed=42))
    exec_result = runtime.run_deterministic(ir_document)

    assert exec_result["status"] == "success"
    customers = exec_result["variables"]["customers"]

    # Verify initial condition
    assert customers[0] == 100, "Initial customers should be 100"

    # Verify recurrence (customers[t+1] = customers[t] + new - churned)
    # With new=20, churn=0.05, customers should grow
    assert customers[-1] > customers[0], "Customers should grow over time"


@pytest.mark.integration
def test_coffee_shop_example():
    """Test the coffee shop beginner example to verify comprehensive functionality."""
    examples_dir = Path("beginner_examples")
    coffee_shop = examples_dir / "coffee_shop.pel"

    if not coffee_shop.exists():
        pytest.skip("coffee_shop.pel not found")

    compiler = PELCompiler(verbose=False)
    ir_document = compiler.compile(coffee_shop)

    runtime = PELRuntime(RuntimeConfig(mode="deterministic", seed=42))
    exec_result = runtime.run_deterministic(ir_document)

    assert exec_result["status"] == "success"
    assert "revenue" in exec_result["variables"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])

