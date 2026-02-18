# PEL Quick Start Demo

This demo showcases the complete PEL workflow from model writing to stakeholder reporting.

## What This Demo Does

1. **Compiles** the example SaaS subscription model
2. **Runs** both deterministic and Monte Carlo simulations
3. **Generates** professional reports (Markdown, HTML)
4. **Creates** visualizations of key metrics

## Running the Demo

```bash
# From the repository root directory
chmod +x demo/quick_start.sh
./demo/quick_start.sh
```

## Expected Output

After running, you'll have:

- `demo/model.ir.json` - Compiled PEL-IR
- `demo/results_deterministic.json` - Deterministic simulation results
- `demo/results_monte_carlo.json` - Monte Carlo simulation results (100 runs)
- `demo/report.md` - Markdown report
- `demo/report.html` - HTML report (open in browser)
- `charts/` - Visualization PNG files (if matplotlib installed)

## Viewing Results

### HTML Report (Recommended)
```bash
open demo/report.html  # macOS
xdg-open demo/report.html  # Linux
```

### Markdown Report
```bash
cat demo/report.md
```

### Raw JSON
```bash
cat demo/results_deterministic.json | jq .
```

## What You're Seeing

The demo model (`examples/simple_growth.pel`) demonstrates:

- **Economic types**: Currency, Rate with units
- **Uncertainty**: Distribution for growth rate
- **Provenance**: Full assumption tracking for all parameters
- **Time series**: Revenue and profit calculations
- **Constraints**: Profitability checks

## Next Steps

1. Try modifying parameters in `examples/simple_growth.pel`
2. Re-run the demo to see how results change
3. Explore the full-featured example: `examples/saas_subscription.pel`
4. Follow the tutorial: `docs/tutorials/your_first_model_15min.md`
5. Build your own model!

## Troubleshooting

**"matplotlib not found"** or **"Visualization requires matplotlib and seaborn"**
```bash
# Install visualization dependencies
pip install 'pel-lang[viz]'

# Or install manually
pip install matplotlib seaborn jinja2
```

**"Permission denied"**
```bash
chmod +x demo/quick_start.sh
```

**"Model doesn't compile"**
- Check that you're in the PEL project root directory
- Ensure `examples/simple_growth.pel` exists
- Try: `python3 ./pel compile examples/simple_growth.pel -v` for verbose errors
