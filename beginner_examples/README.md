# Beginner Examples

These models accompany the [BEGINNER_TUTORIAL.md](../BEGINNER_TUTORIAL.md) - a complete guide for users with zero programming experience.

## Models Included

1. **coffee_shop.pel** - Simple revenue and profit forecast for a coffee shop
2. **saas_business.pel** - Subscription business with customer growth and churn
3. **saas_uncertain.pel** - Same as above, but with uncertainty distributions
4. **hiring_plan.pel** - Engineering team hiring and salary budget planning

## Quick Start - Run All Examples

```bash
./beginner_examples/run_all_examples.sh
```

This automatically runs all four examples and saves results to JSON files.

## Quick Start - Individual Examples

From the repository root, run any of these examples:

```bash
# Coffee shop example
./pel check beginner_examples/coffee_shop.pel
./pel compile beginner_examples/coffee_shop.pel -o beginner_examples/coffee_shop.ir.json
./pel run beginner_examples/coffee_shop.ir.json --mode deterministic --seed 42

# SaaS business example
./pel check beginner_examples/saas_business.pel
./pel compile beginner_examples/saas_business.pel -o beginner_examples/saas_business.ir.json
./pel run beginner_examples/saas_business.ir.json --mode deterministic --seed 42

# SaaS with uncertainty (Monte Carlo)
./pel check beginner_examples/saas_uncertain.pel
./pel compile beginner_examples/saas_uncertain.pel -o beginner_examples/saas_uncertain.ir.json
./pel run beginner_examples/saas_uncertain.ir.json --mode monte_carlo --runs 1000 --seed 42

# Hiring plan example
./pel check beginner_examples/hiring_plan.pel
./pel compile beginner_examples/hiring_plan.pel -o beginner_examples/hiring_plan.ir.json
./pel run beginner_examples/hiring_plan.ir.json --mode deterministic --seed 42
```

## View Results in Human-Readable Format

After running a model, use the results viewer to see formatted output:

```bash
python3 beginner_examples/view_results.py beginner_examples/coffee_results.json
```

This shows:
- ✅ Model status and parameters
- 📊 Results over time with growth percentages  
- ⚠️ Any constraint violations
- 💡 Helpful tips for next steps

Or view the raw JSON:
```bash
cat beginner_examples/coffee_results.json
```

## Learning Path

Follow the tutorial in order:
1. Part 1: Coffee Shop (basic model structure)
2. Part 2: SaaS Business (customer counts and rates)
3. Part 3: Uncertainty (Monte Carlo simulation)
4. Part 4: Hiring Plan (complex calculations)

Each part builds on concepts from previous parts.

## Next Steps

After completing these examples, continue with:
- [Your First Model in 15 Minutes](../docs/tutorials/your_first_model_15min.md)
- [Economic Types Tutorial](../docs/tutorials/02_economic_types.md)
- [Uncertainty & Distributions](../docs/tutorials/03_uncertainty_distributions.md)
