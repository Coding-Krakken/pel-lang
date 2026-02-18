# Tests

PEL uses `pytest` for testing. This directory contains the complete test suite organized into unit, integration, and conformance tests.

## Quick Start

### Run All Tests
```bash
pytest
```

### Run Specific Test Categories
```bash
# Unit tests only
pytest tests/unit -v

# Integration tests only
pytest tests/integration -v

# Conformance tests only
pytest tests/conformance -v
```

## Test Organization

- **`unit/`** - Unit tests for individual compiler and runtime components
- **`integration/`** - End-to-end tests for complete workflows
- **`conformance/`** - Specification compliance tests (YAML-based)
- **`benchmarks/`** - Performance and regression benchmarks

## Coverage

Coverage is reported by default via `pytest-cov` (see `pyproject.toml`).

**Generate coverage report:**
```bash
make coverage
```

**View HTML report:**
```bash
open htmlcov/index.html
```

**Coverage requirements:**
- Minimum threshold: **80%** (enforced in CI)
- Target for new code: **90%+**

## Running Tests Locally

Before pushing code, run the full CI suite:
```bash
make ci
```

This runs:
- `make lint` - Ruff linter
- `make typecheck` - Mypy type checker
- `make security` - Bandit security scanner
- `make test` - Full test suite with coverage

## Writing Tests

Follow these conventions:
1. Use descriptive test names: `test_<component>_<scenario>_<expected_outcome>`
2. Follow Arrange-Act-Assert pattern
3. Test both success and error cases
4. Keep tests isolated and deterministic
5. Use pytest fixtures for reusable setup

**Example:**
```python
def test_lexer_tokenizes_duration_literals_correctly():
    # Arrange
    source = "1mo"
    
    # Act
    tokens = lex(source)
    
    # Assert
    assert tokens[0].type == TokenType.DURATION
    assert tokens[0].value == "1mo"
```

## Conformance Tests

Conformance tests validate compliance with the PEL specification. Test cases are defined in YAML format in `spec/conformance/`.

**Run conformance tests:**
```bash
pytest tests/conformance/ -v
```

**Validate all YAML test definitions:**
```bash
python3 tests/conformance/test_runner.py --validate-all
```

## Debugging Failed Tests

**Verbose output with local variables:**
```bash
pytest tests/unit/test_parser.py::test_function -vvl
```

**Enter debugger on failure:**
```bash
pytest tests/unit/test_parser.py::test_function --pdb
```

**Show print statements:**
```bash
pytest tests/unit/test_parser.py::test_function -s
```

## CI Integration

All tests run in CI on Python 3.10, 3.11, and 3.12. CI enforces:
- All tests must pass
- Coverage ≥ 80%
- No high/medium security issues
- Code passes lint and type checks

## Additional Documentation

For comprehensive testing guidance, see:
- **[Testing Guide](../docs/TESTING.md)** - Complete testing documentation
- **[Contributing Guide](../CONTRIBUTING.md)** - Contribution guidelines and CI details
- **[Specification](../spec/)** - Language specification and conformance requirements

