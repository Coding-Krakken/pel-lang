# Tests

PEL uses `pytest`.

## Run

- All tests: `pytest`
- Unit tests only: `pytest -m unit`
- Integration tests only: `pytest -m integration`

## Coverage

Coverage is reported by default via `pytest-cov` (see `pyproject.toml`).

- Terminal report: `pytest`
- HTML report: open `htmlcov/index.html`
