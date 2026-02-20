# PEL — Programmable Economic Language

[![CI Pipeline](https://github.com/Coding-Krakken/pel-lang/actions/workflows/ci.yml/badge.svg)](https://github.com/Coding-Krakken/pel-lang/actions/workflows/ci.yml)

**Version:** 0.1.0  
**Status:** Active development (spec + reference implementation)  
**License:** AGPL-3.0-or-later OR Commercial

---

## What is PEL?

PEL is a domain-specific language for executable economic and business modeling.

Core goals:
- Economic type safety (units, scope, time semantics)
- Uncertainty as a first-class concept
- Constraint and policy execution
- Provenance-aware assumptions
- Reproducible model execution via IR + seed

---

## Quick Start

### 1) Clone and install

```bash
git clone https://github.com/Coding-Krakken/pel-lang.git
cd pel-lang
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Use the same shell session (or re-run `source .venv/bin/activate`) before `make` commands so tools like `ruff`, `mypy`, and `pytest` resolve correctly.

### 2) Compile a model

```bash
./pel compile examples/simple_growth.pel -o demo/simple_growth.ir.json
```

### 3) Run deterministic execution

```bash
./pel run demo/simple_growth.ir.json --mode deterministic --seed 42
```

### 4) Run Monte Carlo execution

```bash
./pel run demo/simple_growth.ir.json --mode monte_carlo --runs 1000 --seed 42
```

### 5) Validate model semantics only

```bash
./pel check examples/simple_growth.pel
```

---

## Repository Map

```text
compiler/      Lexer, parser, typechecker, IR generation
runtime/       Runtime execution + calibration modules
stdlib/        Standard economic modeling modules
spec/          Formal language and semantics specifications
tests/         Unit, integration, conformance, performance, language-eval tests
docs/          Tutorials, testing/CI guides, architecture and delivery docs
benchmarks/    PEL-100 benchmark data and scorer
examples/      Example .pel models and sample IR outputs
```

---

## Documentation

- [Documentation Index](docs/README.md)
- [Tutorials](docs/tutorials/README.md)
- [Testing Guide](docs/TESTING.md)
- [Migration Guide](docs/MIGRATION_GUIDE.md)
- [Language Specifications](spec/)
- [Standard Library Notes](stdlib/README.md)
- [Benchmarks](benchmarks/README.md)
- [Roadmap](ROADMAP.md)

---

## CLI Notes

- `./pel` is the repository CLI wrapper supporting `compile`, `run`, and `check`.
- `pel format`/`pel fmt` and `pel lint` are intentionally stubbed and delegate to external tooling.
- Recommended code-quality tooling for this repo:

```bash
make format
make lint
make typecheck
```

---

## Development Commands

```bash
make install      # install editable package + pre-commit
make test         # run tests
make coverage     # coverage report (htmlcov/index.html)
make ci           # lint + typecheck + security + tests
```

---

## Contributing

See:
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [SECURITY.md](SECURITY.md)
- [CLA.md](CLA.md)
- [CLA-SIGNING.md](CLA-SIGNING.md)

---

## License

PEL is dual licensed:

- Open source: AGPL-3.0-or-later ([LICENSE](LICENSE))
- Commercial: [COMMERCIAL-LICENSE.md](COMMERCIAL-LICENSE.md)

For commercial licensing, contact: `davidtraversmailbox@gmail.com`
