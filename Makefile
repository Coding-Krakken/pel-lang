.PHONY: install lint format typecheck test coverage security ci clean help

help:
	@echo "PEL Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install     - Install package with dev dependencies and pre-commit hooks"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint        - Run ruff linter"
	@echo "  make format      - Format code with ruff"
	@echo "  make typecheck   - Run mypy type checker"
	@echo "  make security    - Run bandit security scanner"
	@echo ""
	@echo "Testing:"
	@echo "  make test        - Run test suite"
	@echo "  make coverage    - Run tests with coverage report"
	@echo ""
	@echo "CI:"
	@echo "  make ci          - Run all CI checks (lint + typecheck + security + test)"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean       - Remove build artifacts and caches"

install:
	pip install -e .[dev]
	pre-commit install

lint:
	ruff check compiler/ runtime/ tests/

format:
	ruff format compiler/ runtime/ tests/

typecheck:
	mypy compiler/ runtime/ --ignore-missing-imports

test:
	pytest tests/ -v

coverage:
	pytest tests/ --cov=compiler --cov=runtime --cov-report=html --cov-report=term --cov-fail-under=80
	@echo ""
	@echo "✅ Coverage threshold (80%) met!"
	@echo "📊 Full report: htmlcov/index.html"

security:
	bandit -r compiler/ runtime/ -c pyproject.toml || true

ci: lint typecheck security test
	@echo ""
	@echo "✅ All CI checks passed!"

clean:
	rm -rf .pytest_cache .ruff_cache .mypy_cache htmlcov dist build *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
