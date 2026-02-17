#!/bin/bash
# PEL Quick Start Demo
# Demonstrates end-to-end workflow: compile → run → visualize → report

set -e  # Exit on error

echo "===================================="
echo "PEL Quick Start Demo"
echo "===================================="
echo ""

# Step 1: Compile example model
echo "[1/4] Compiling SaaS subscription model..."
python3 ./pel compile examples/saas_subscription.pel -o demo/model.ir.json
echo "✓ Compilation successful"
echo ""

# Step 2: Run deterministic simulation
echo "[2/4] Running deterministic simulation..."
python3 ./pel run demo/model.ir.json --mode deterministic --seed 42 -o demo/results_deterministic.json
echo "✓ Deterministic run complete"
echo ""

# Step 3: Run Monte Carlo simulation (faster with fewer runs for demo)
echo "[3/4] Running Monte Carlo simulation (100 runs)..."
python3 ./pel run demo/model.ir.json --mode monte_carlo --runs 100 --seed 42 -o demo/results_monte_carlo.json
echo "✓ Monte Carlo run complete"
echo ""

# Step 4: Generate reports
echo "[4/4] Generating reports..."

# Markdown report
python3 runtime/reporting.py demo/results_deterministic.json markdown demo/report.md
echo "✓ Markdown report: demo/report.md"

# HTML report
python3 runtime/reporting.py demo/results_deterministic.json html demo/report.html
echo "✓ HTML report: demo/report.html"

# Generate charts (if matplotlib available)
if python3 -c "import matplotlib" 2>/dev/null; then
    python3 runtime/visualization.py demo/results_deterministic.json charts/
    echo "✓ Charts generated in charts/"
else
    echo "⚠ Skipping charts (matplotlib not installed)"
fi

echo ""
echo "===================================="
echo "Demo Complete!"
echo "===================================="
echo ""
echo "Results:"
echo "  - Compiled model: demo/model.ir.json"
echo "  - Deterministic results: demo/results_deterministic.json"
echo "  - Monte Carlo results: demo/results_monte_carlo.json"
echo "  - Markdown report: demo/report.md"
echo "  - HTML report: demo/report.html"
echo ""
echo "Open demo/report.html in your browser to view results!"
echo ""
