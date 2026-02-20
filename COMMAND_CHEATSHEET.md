# PEL Command Cheat Sheet

Quick reference for common PEL commands. All commands assume you're in the repository root directory.

---

## Basic Workflow

### 1. Check your model (validate syntax and types)
```bash
./pel check YOUR_MODEL.pel
```

### 2. Compile to executable IR
```bash
./pel compile YOUR_MODEL.pel -o OUTPUT.ir.json
```

### 3. Run the model
```bash
./pel run OUTPUT.ir.json --mode deterministic --seed 42 -o results.json
```

---

## Common Commands

### Validate a model without compiling
```bash
./pel check examples/simple_growth.pel
```

### Compile with custom output path
```bash
./pel compile examples/simple_growth.pel -o build/model.ir.json
```

### Run deterministic simulation (uses mean values)
```bash
./pel run model.ir.json --mode deterministic --seed 42
```

### Run Monte Carlo simulation (1000 scenarios)
```bash
./pel run model.ir.json --mode monte_carlo --runs 1000 --seed 42
```

### Run Monte Carlo with 10,000 scenarios (more accurate)
```bash
./pel run model.ir.json --mode monte_carlo --runs 10000 --seed 42
```

### Save results to a file
```bash
./pel run model.ir.json --mode deterministic --seed 42 -o my_results.json
```

### Override time horizon (run for 24 months instead of default)
```bash
./pel run model.ir.json --mode deterministic --horizon 24 --seed 42
```

---

## View Results

### View results in formatted output (beginner-friendly)
```bash
python3 beginner_examples/view_results.py results.json
```

### View raw JSON results
```bash
cat results.json
```

### Extract just the variables section
```bash
cat results.json | grep -A 50 '"variables"'
```

### Pretty-print JSON (if you have jq installed)
```bash
cat results.json | jq '.'
```

---

## Beginner Examples

### Run all beginner tutorials at once
```bash
./beginner_examples/run_all_examples.sh
```

### Coffee shop example
```bash
./pel check beginner_examples/coffee_shop.pel
./pel compile beginner_examples/coffee_shop.pel -o beginner_examples/coffee_shop.ir.json
./pel run beginner_examples/coffee_shop.ir.json --mode deterministic --seed 42
```

### SaaS business example
```bash
./pel check beginner_examples/saas_business.pel
./pel compile beginner_examples/saas_business.pel -o beginner_examples/saas_business.ir.json
./pel run beginner_examples/saas_business.ir.json --mode deterministic --seed 42
```

### SaaS with uncertainty (Monte Carlo)
```bash
./pel check beginner_examples/saas_uncertain.pel
./pel compile beginner_examples/saas_uncertain.pel -o beginner_examples/saas_uncertain.ir.json
./pel run beginner_examples/saas_uncertain.ir.json --mode monte_carlo --runs 1000 --seed 42
```

---

## Development Commands

### Run all tests
```bash
make test
```

### Run tests with coverage report
```bash
make coverage
```

### Lint and type-check code
```bash
make lint
make typecheck
```

### Full CI pipeline (lint + typecheck + security + tests)
```bash
make ci
```

### Format code
```bash
make format
```

---

## Working with Examples

### List all example models
```bash
ls examples/*.pel
```

### Compile all examples
```bash
for file in examples/*.pel; do
  ./pel compile "$file" -o "demo/$(basename $file .pel).ir.json"
done
```

### Run a specific example
```bash
./pel compile examples/saas_operations.pel -o demo/saas.ir.json
./pel run demo/saas.ir.json --mode deterministic --seed 42
```

---

## Help and Documentation

### Show PEL version
```bash
./pel --version
```

### Show help for main CLI
```bash
./pel --help
```

### Show help for compile command
```bash
./pel compile --help
```

### Show help for run command
```bash
./pel run --help
```

### Read beginner tutorial
```bash
cat BEGINNER_TUTORIAL.md
```

### Browse all tutorials
```bash
ls docs/tutorials/*.md
```

---

## Troubleshooting

### Check Python environment is activated
```bash
which python3
# Should show: /path/to/PEL/.venv/bin/python3
```

### Activate virtual environment if needed
```bash
source .venv/bin/activate
```

### Reinstall PEL in development mode
```bash
pip install -e ".[dev]"
```

### Clear compiled IR files
```bash
rm demo/*.ir.json
rm beginner_examples/*.ir.json
```

### Clear results files
```bash
rm demo/*results*.json
rm beginner_examples/*results*.json
```

---

## Quick Copy-Paste Workflows

### Full workflow: check → compile → run → view
```bash
MODEL="beginner_examples/coffee_shop"
./pel check ${MODEL}.pel && \
./pel compile ${MODEL}.pel -o ${MODEL}.ir.json && \
./pel run ${MODEL}.ir.json --mode deterministic --seed 42 -o ${MODEL}_results.json && \
python3 beginner_examples/view_results.py ${MODEL}_results.json
```

### Monte Carlo workflow: compile → run MC → view
```bash
MODEL="beginner_examples/saas_uncertain"
./pel compile ${MODEL}.pel -o ${MODEL}.ir.json && \
./pel run ${MODEL}.ir.json --mode monte_carlo --runs 1000 --seed 42 -o ${MODEL}_mc.json && \
python3 beginner_examples/view_results.py ${MODEL}_mc.json
```

### Create and run a new model
```bash
# Create your model file
nano my_model.pel

# Check, compile, run
./pel check my_model.pel && \
./pel compile my_model.pel -o my_model.ir.json && \
./pel run my_model.ir.json --mode deterministic --seed 42 -o my_results.json
```

---

## File Naming Conventions

- `.pel` - Source model files (you write these)
- `.ir.json` - Compiled intermediate representation (generated)
- `_results.json` - Execution results (generated)
- `_mc.json` - Monte Carlo results (generated)

---

## Tips

1. **Always use `--seed 42`** (or any number) for reproducible results
2. **Start with deterministic mode** to validate your model logic
3. **Use Monte Carlo** when you have uncertain parameters (`~Normal(...)`)
4. **Check before compiling** to catch errors early
5. **View results with view_results.py** for human-readable output

---

For more detailed information, see:
- [BEGINNER_TUTORIAL.md](BEGINNER_TUTORIAL.md) - Complete beginner's guide
- [README.md](README.md) - Project overview
- [docs/tutorials/](docs/tutorials/) - Advanced tutorials
- [spec/](spec/) - Language specification
