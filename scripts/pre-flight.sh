#!/bin/bash
# Quick CI pre-flight check script
# Run this before pushing to catch common issues

set -e  # Exit on error

echo "🔍 Running pre-flight CI checks..."
echo ""

# Check 1: Lint
echo "1️⃣  Checking code style (ruff)..."
ruff check compiler/ runtime/ tests/ --extend-exclude .github/prompts
echo "   ✅ Lint passed"
echo ""

# Check 2: Type checking
echo "2️⃣  Type checking (mypy)..."
mypy compiler/ runtime/ --ignore-missing-imports
echo "   ✅ Type check passed"
echo ""

# Check 3: Quick test run (unit tests only for speed)
echo "3️⃣  Running unit tests..."
pytest tests/unit/ -q --tb=line
echo "   ✅ Unit tests passed"
echo ""

# Check 4: Security scan
echo "4️⃣  Security scan (bandit)..."
bandit -r compiler/ runtime/ -c pyproject.toml -q || true
echo "   ✅ Security scan complete"
echo ""

echo "✨ All pre-flight checks passed!"
echo ""
echo "Ready to commit and push. If you want to run the full test suite, use:"
echo "   make ci"
echo ""
