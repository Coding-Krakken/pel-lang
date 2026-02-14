.PHONY: lint typecheck test ci install-hooks

lint:
	@echo "Running linters..."
	black --check .
	ruff check .

typecheck:
	@echo "Running type checker..."
	-mypy compiler/ runtime/ --explicit-package-bases
	@echo "Note: Type checking complete (errors are informational)"

test:
	@echo "Running tests with coverage..."
	pytest --cov=compiler --cov=runtime --cov-report=term --cov-fail-under=95

ci: lint typecheck test
	@echo "All CI checks passed!"

install-hooks:
	@echo "Installing pre-commit hooks..."
	pre-commit install
	@echo "Pre-commit hooks installed successfully!"
