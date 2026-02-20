# Testing Guide

This guide documents the current testing workflow for PEL.

---

## Quick Start

```bash
make test
```

With coverage:

```bash
make coverage
```

Coverage HTML report is generated at `htmlcov/index.html`.

---

## Test Layout

- `tests/unit/` — fast, isolated component tests
- `tests/integration/` — end-to-end and subsystem integration tests
- `tests/conformance/` — spec-focused conformance tests
- `tests/performance/` — performance checks
- `tests/language_eval/` — language-evaluation framework tests
- top-level `tests/test_*.py` — targeted regression/integration modules

---

## Useful Commands

Run full suite:

```bash
pytest tests/ -v
```

Run by marker:

```bash
pytest -m unit
pytest -m integration
pytest -m performance
pytest -m slow
pytest -m "not slow"
```

Run a specific test:

```bash
pytest tests/test_parser.py -v
pytest tests/test_parser.py::test_basic_model_parses -v
```

Debug failures:

```bash
pytest tests/test_parser.py -vv --pdb -s -l
```

---

## CI-Equivalent Local Run

Use this before opening PRs:

```bash
make ci
```

This runs:

1. `make lint`
2. `make typecheck`
3. `make security`
4. `make test`

---

## Writing Tests

Guidelines:

- Follow arrange/act/assert structure
- Keep test names explicit and behavior-oriented
- Cover both happy-path and failure-path behavior
- Prefer small fixtures and deterministic seeds where relevant
- Add regression tests for bug fixes

---

## Troubleshooting

### Import/path issues

- Activate your virtual environment
- Reinstall editable package: `pip install -e ".[dev]"`

### Marker errors

- Ensure marker name is declared in `pyproject.toml`
- Use `pytest --markers` to inspect available markers

### Slow runs

- Run targeted files first
- Exclude slow tests with `-m "not slow"`

---

## Help

- Issues: https://github.com/Coding-Krakken/pel-lang/issues
- Discussions: https://github.com/Coding-Krakken/pel-lang/discussions
