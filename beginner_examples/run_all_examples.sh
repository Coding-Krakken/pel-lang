#!/bin/bash
# Quick-start script for beginner tutorial
# Runs all example models and saves results

set -e  # Exit on error

echo "=========================================="
echo "PEL Beginner Tutorial - Quick Start"
echo "=========================================="
echo ""

# Ensure we're using the virtual environment
export PATH="$PWD/.venv/bin:$PATH"

# Example 1: Coffee Shop
echo ">>> Example 1: Coffee Shop Revenue Forecast"
echo "    Scenario: Small coffee shop growth over 12 months"
echo ""
./pel check beginner_examples/coffee_shop.pel
./pel compile beginner_examples/coffee_shop.pel -o beginner_examples/coffee_shop.ir.json
./pel run beginner_examples/coffee_shop.ir.json --mode deterministic --seed 42 -o beginner_examples/coffee_results.json
echo "    ✅ Results saved to: beginner_examples/coffee_results.json"
echo ""

# Example 2: SaaS Business
echo ">>> Example 2: SaaS Subscription Business"
echo "    Scenario: Customer growth with monthly churn"
echo ""
./pel check beginner_examples/saas_business.pel
./pel compile beginner_examples/saas_business.pel -o beginner_examples/saas_business.ir.json
./pel run beginner_examples/saas_business.ir.json --mode deterministic --seed 42 -o beginner_examples/saas_results.json
echo "    ✅ Results saved to: beginner_examples/saas_results.json"
echo ""

# Example 3: SaaS with Uncertainty
echo ">>> Example 3: SaaS with Uncertainty (Monte Carlo)"
echo "    Scenario: Same as #2, but with uncertainty in customer acquisition"
echo "    (Running 1000 simulations - this may take a moment...)"
echo ""
./pel check beginner_examples/saas_uncertain.pel
./pel compile beginner_examples/saas_uncertain.pel -o beginner_examples/saas_uncertain.ir.json
./pel run beginner_examples/saas_uncertain.ir.json --mode monte_carlo --runs 1000 --seed 42 -o beginner_examples/saas_mc_results.json
echo "    ✅ Results saved to: beginner_examples/saas_mc_results.json"
echo ""

# Example 4: Hiring Plan
echo ">>> Example 4: Engineering Hiring & Salary Budget"
echo "    Scenario: Team growth and payroll planning for 12 months"
echo ""
./pel check beginner_examples/hiring_plan.pel
./pel compile beginner_examples/hiring_plan.pel -o beginner_examples/hiring_plan.ir.json
./pel run beginner_examples/hiring_plan.ir.json --mode deterministic --seed 42 -o beginner_examples/hiring_results.json
echo "    ✅ Results saved to: beginner_examples/hiring_results.json"
echo ""

echo "=========================================="
echo "All examples completed successfully! 🎉"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Open any *_results.json file to see the forecasts"
echo "  2. Read BEGINNER_TUTORIAL.md for detailed explanations"
echo "  3. Try modifying the .pel files and re-running"
echo ""
echo "Example: View coffee shop results"
echo "  cat beginner_examples/coffee_results.json | grep -A 20 variables"
echo ""
