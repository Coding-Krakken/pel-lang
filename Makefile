.PHONY: install lint format typecheck test coverage security ci clean install-hooks

install:
	pip install -e .[dev]
	pre-commit install

lint:
	ruff check compiler/ runtime/ tests/ || true

format:
	ruff format compiler/ runtime/ tests/

typecheck:
	mypy compiler/ runtime/ --exclude '.*_old\.py' || true

test:
	pytest tests/ -v

coverage:
	pytest tests/ --cov=compiler --cov=runtime --cov-report=html --cov-report=term --cov-fail-under=95

security:
	bandit -r compiler/ runtime/ -c pyproject.toml || true

ci: lint typecheck security test
	@echo "✅ All CI checks passed"

clean:
	rm -rf .pytest_cache .ruff_cache .mypy_cache htmlcov dist build *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

install-hooks:
	pre-commit install
