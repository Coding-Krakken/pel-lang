#!/bin/bash
# Tag release v0.6.0 after PR-22 is merged
# Run this script from the main branch after the merge

set -e

echo "🏷️  Tagging release v0.6.0 - 6 of 9 stdlib modules complete"
echo ""

# Verify we're on main and up to date
if [ "$(git branch --show-current)" != "main" ]; then
    echo "❌ Error: Not on main branch. Please checkout main and pull latest changes."
    exit 1
fi

echo "📥 Pulling latest changes from main..."
git pull origin main

echo ""
echo "📝 Creating annotated tag v0.6.0..."
git tag -a v0.6.0 -m "Release v0.6.0: Capacity and Hiring Stdlib Modules

This release completes 6 of 9 planned stdlib modules (67% complete).

## New Modules

### Capacity Module (16 functions)
- Utilization calculations and monitoring
- Multi-product resource allocation
- Scaling and expansion planning
- Performance metrics (Welford's algorithm)

### Hiring Module (21 functions)
- Hiring funnel modeling
- Workforce planning and attrition
- Ramp curves (linear, exponential, s-curve)
- Team capacity and cost modeling

## Completed Stdlib Modules (6/9)
✅ funnel/ - Conversion funnels
✅ unit_econ/ - Unit economics (LTV, CAC, payback)
✅ cashflow/ - Cash flow waterfall
✅ retention/ - Retention and churn
✅ capacity/ - Capacity planning (NEW)
✅ hiring/ - Hiring and headcount (NEW)

## Implementation Highlights
- 1,065 lines of production-quality PEL code
- 114 tests with 100% pass rate (4:1 test-to-code ratio)
- 3 complete example models
- Comprehensive input validation
- Numerically stable algorithms
- Production-grade documentation

## Type System Enhancement
- Dimensionless multiplication shortcut (Fraction/Int/Count × dimensioned types)
- Enables clean expressions: efficiency * capacity → Rate

## Next Milestones
🔜 v0.7.0 - Demand forecasting module
🔜 v0.8.0 - Pricing models module
🔜 v0.9.0 - Scenario library module
🎯 v1.0.0 - Complete stdlib (9/9 modules)

See PR-22 for full details: https://github.com/Coding-Krakken/pel-lang/pull/22"

echo ""
echo "✅ Tag v0.6.0 created successfully!"
echo ""
echo "📤 Pushing tag to remote..."
git push origin v0.6.0

echo ""
echo "🎉 Release v0.6.0 tagged and pushed!"
echo ""
echo "Next steps:"
echo "  1. Create GitHub release from tag: https://github.com/Coding-Krakken/pel-lang/releases/new?tag=v0.6.0"
echo "  2. Update ROADMAP.md with next module (demand or pricing)"
echo "  3. Consider updating project version in pyproject.toml"
