# Testing Guide

This guide provides comprehensive information about testing in the PEL project.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Test Organization](#test-organization)
3. [Running Tests](#running-tests)
4. [Writing Tests](#writing-tests)
5. [Coverage Requirements](#coverage-requirements)
6. [CI Pipeline](#ci-pipeline)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Run All Tests

```bash
# Using pytest directly
pytest

# Using Make
make test
```

### Run Tests with Coverage

```bash
# Generate coverage report
make coverage

# View HTML report
open htmlcov/index.html
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest tests/unit -v

# Integration tests only
pytest tests/integration -v

# Conformance tests only
pytest tests/conformance -v

# Specific test file
pytest tests/unit/test_lexer.py -v

# Specific test function
pytest tests/unit/test_lexer.py::TestLexer::test_duration_literals -v
```

---

## Test Organization

The PEL test suite is organized into three main categories:

### Unit Tests (`tests/unit/`)

Test individual components in isolation:
- **Compiler components**: lexer, parser, type checker, IR generator
- **Runtime components**: execution engine, dimension system, reporting
- **Focus**: Fast, isolated, comprehensive branch coverage

**Examples:**
- `test_lexer.py` - Lexer tokenization and edge cases
- `test_parser.py` - Parser AST generation and error handling
- `test_typechecker.py` - Type checking rules and constraint validation
- `test_runtime.py` - Runtime evaluation and Monte Carlo simulation

### Integration Tests (`tests/integration/`)

Test end-to-end workflows and component interactions:
- **Full compilation pipelines**: `.pel` → IR → execution → results
- **Example validation**: Ensure shipped examples compile and run
- **Cross-module integration**: Compiler + runtime interaction
- **Focus**: Real-world usage patterns and regression prevention

**Examples:**
- `test_end_to_end_demo.py` - Full demo workflow execution
- `test_examples_compile.py` - Example model compilation and validation

### Conformance Tests (`tests/conformance/`)

Verify compliance with the PEL specification:
- **Specification test cases**: YAML-defined test suites from `spec/`
- **Standardized validation**: Ensures consistency across implementations
- **Language semantics**: Lexical, parsing, type checking, runtime behavior
- **Focus**: Formal correctness and specification adherence

**Examples:**
- `test_lexical.py` - Lexical conformance (tokenization rules)
- `test_parsing.py` - Parsing conformance (syntax and AST structure)
- `test_typechecking.py` - Type system conformance
- `test_runtime.py` - Runtime semantics conformance
- `test_provenance.py` - Provenance metadata requirements

**Conformance test format (YAML):**
```yaml
test_cases:
  - name: "rate_literal_parsing"
    description: "Verify rate literals parse correctly"
    input: "let x: Rate = 5% / yr"
    expected_output: "PASS"
    expected_ast_type: "VariableDeclaration"
```

---

## Running Tests

### Local Development

**Before committing code:**
```bash
# Run full CI suite locally
make ci

# This runs:
# - make lint        (ruff linter)
# - make typecheck   (mypy type checker)
# - make security    (bandit security scan)
# - make test        (full test suite)
```

**Faster iteration during development:**
```bash
# Run only tests related to your changes
pytest tests/unit/test_parser.py -v

# Run with verbose output and stop on first failure
pytest tests/unit/test_parser.py -vsx

# Run with Python debugger on failure
pytest tests/unit/test_parser.py --pdb
```

### Test Markers

PEL uses pytest markers to categorize tests:

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only slow tests
pytest -m slow

# Run everything except slow tests
pytest -m "not slow"
```

**Apply markers in test code:**
```python
import pytest

@pytest.mark.unit
def test_lexer_tokenizes_numbers():
    # ...

@pytest.mark.integration
def test_full_compilation_pipeline():
    # ...

@pytest.mark.slow
def test_monte_carlo_10k_iterations():
    # ...
```

### Debugging Failed Tests

**Verbose output:**
```bash
pytest tests/unit/test_parser.py::test_function -vv
```

**Show local variables on failure:**
```bash
pytest tests/unit/test_parser.py::test_function -l
```

**Enter debugger on failure:**
```bash
pytest tests/unit/test_parser.py::test_function --pdb
```

**Show print statements:**
```bash
pytest tests/unit/test_parser.py::test_function -s
```

**Combine options:**
```bash
pytest tests/unit/test_parser.py::test_function -vvs --pdb -l
```

---

## Writing Tests

### Test Structure

Follow the **Arrange-Act-Assert** pattern:

```python
def test_parser_handles_variable_declaration():
    # Arrange: Set up test data
    source = "let revenue: Currency = 1000 USD"
    
    # Act: Execute the functionality
    result = parse(source)
    
    # Assert: Verify expected outcome
    assert isinstance(result, VariableDeclaration)
    assert result.name == "revenue"
    assert result.type_annotation == "Currency"
```

### Test Naming

Use descriptive names that explain **what** is tested and **expected outcome**:

✅ **Good:**
```python
def test_lexer_tokenizes_duration_literals_correctly():
def test_parser_raises_error_on_missing_semicolon():
def test_typechecker_rejects_currency_addition_without_same_unit():
```

❌ **Avoid:**
```python
def test_lexer():
def test_parser_1():
def test_error():
```

### Testing Error Cases

Always test both success and failure paths:

```python
def test_typechecker_rejects_incompatible_types():
    source = """
    let count: Count = 100
    let currency: Currency = 50 USD
    let result = count + currency  // Type error!
    """
    
    with pytest.raises(TypeCheckError) as exc_info:
        compile_pel(source)
    
    assert "incompatible types" in str(exc_info.value).lower()
    assert "Count" in str(exc_info.value)
    assert "Currency" in str(exc_info.value)
```

### Fixtures and Reusability

Use pytest fixtures to avoid repetition:

```python
# In conftest.py or test file
@pytest.fixture
def sample_model():
    return """
    parameter churn_rate: Rate = 5% / mo
    parameter monthly_revenue: Currency/Count = 100 USD / user
    """

def test_parser_extracts_parameters(sample_model):
    result = parse(sample_model)
    assert len(result.parameters) == 2

def test_compiler_generates_ir(sample_model):
    ir = compile_to_ir(sample_model)
    assert ir["parameters"]["churn_rate"]["value"] == 0.05
```

### Parameterized Tests

Use `@pytest.mark.parametrize` for testing multiple cases:

```python
@pytest.mark.parametrize("duration,expected_months", [
    ("1mo", 1),
    ("1yr", 12),
    ("1q", 3),
    ("2w", 0.5),
])
def test_duration_conversion_to_months(duration, expected_months):
    result = parse_duration(duration).to_months()
    assert result == pytest.approx(expected_months)
```

### Coverage Best Practices

**1. Test all branches:**
```python
def calculate_discount(amount, is_premium):
    if is_premium:
        return amount * 0.8  # Test this branch
    else:
        return amount * 0.9  # And this branch
```

**2. Test edge cases:**
- Empty inputs
- Boundary values (0, negative, very large)
- None/null values
- Invalid types

**3. Test error handling:**
- Expected exceptions
- Error messages are helpful
- Error recovery (if applicable)

---

## Coverage Requirements

### Minimum Thresholds

- **Overall coverage**: ≥ 80% (enforced in CI)
- **New code**: ≥ 90% (enforced in code review)
- **Critical paths**: 100% (compiler, type checker, runtime evaluation)

### Generating Coverage Reports

**Terminal report:**
```bash
pytest --cov=compiler --cov=runtime --cov-report=term-missing
```

**HTML report (recommended):**
```bash
make coverage
open htmlcov/index.html
```

**XML report (for CI tools):**
```bash
pytest --cov=compiler --cov=runtime --cov-report=xml
```

### Understanding Coverage Reports

**Terminal output:**
```
Name                             Stmts   Miss  Cover   Missing
--------------------------------------------------------------
compiler/lexer.py                  321      1    99%   335
compiler/parser.py                 534     11    98%   360, 417, 479-481
runtime/runtime.py                 192     37    81%   83-84, 134-136
--------------------------------------------------------------
TOTAL                             2613    270    90%
```

- **Stmts**: Total executable statements
- **Miss**: Statements not covered by tests
- **Cover**: Percentage covered
- **Missing**: Line numbers not covered

**HTML report benefits:**
- Visual line-by-line coverage highlighting
- Branch coverage details
- Easy navigation between files
- Identify uncovered branches

### Coverage Exclusions

Some code is intentionally excluded from coverage:

```python
# Defensive programming (should never execute)
if __name__ == "__main__":
    main()  # pragma: no cover

# Type checking imports
if TYPE_CHECKING:
    from typing import Protocol  # pragma: no cover

# Abstract methods (covered by implementations)
@abstractmethod
def process(self):
    raise NotImplementedError  # pragma: no cover
```

Configured in `pyproject.toml`:
```toml
[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "@(abc\\.)?abstractmethod",
]
```

---

## CI Pipeline

### Overview

All code must pass CI checks before merging to `main`. The pipeline runs on:
- All pushes to `main`
- All pushes to `premerge/**` branches
- All pull requests

### Pipeline Stages

#### 1. Lint (Fast Fail)
- **Tool**: `ruff`
- **Runtime**: ~10 seconds
- **Checks**: Code style, unused imports, complexity
- **Fail**: Code style violations

```bash
# Run locally
make lint
```

#### 2. Type Check (Fast Fail)
- **Tool**: `mypy`
- **Runtime**: ~15 seconds
- **Checks**: Type annotations, type safety
- **Fail**: Type errors, missing annotations

```bash
# Run locally
make typecheck
```

#### 3. Test (Matrix: Python 3.10, 3.11, 3.12)
- **Tool**: `pytest`
- **Runtime**: ~2-3 minutes per version
- **Checks**: All tests pass, coverage ≥ 80%
- **Fail**: Test failures, insufficient coverage

```bash
# Run locally (current Python version)
make test
make coverage
```

#### 4. Security Scan
- **Tool**: `bandit`
- **Runtime**: ~5 seconds
- **Checks**: Security vulnerabilities
- **Fail**: High/medium severity issues

```bash
# Run locally
make security
```

#### 5. Build
- **Tool**: Python `build`
- **Runtime**: ~10 seconds
- **Checks**: Package builds correctly
- **Fail**: Missing dependencies, build errors
- **Requires**: All above stages pass

```bash
# Run locally
pip install build
python -m build
```

### Required Checks for Merge

All PRs must satisfy:
- ✅ All CI stages pass (lint, typecheck, test, security, build)
- ✅ All tests pass on Python 3.10, 3.11, 3.12
- ✅ Code coverage ≥ 80%
- ✅ No security issues (medium or high severity)
- ✅ At least 1 approval from a maintainer
- ✅ Branch up to date with `main`

### Viewing CI Results

**GitHub Actions UI:**
1. Go to PR or commit
2. Click "Checks" tab
3. Expand failed stage to see logs

**Status checks on PR:**
- Green ✅: All checks passed
- Red ❌: One or more checks failed
- Yellow 🟡: Checks in progress

---

## Troubleshooting

### Common Test Failures

#### Import Errors

**Symptom:**
```
ImportError: No module named 'compiler'
```

**Solution:**
```bash
# Install package in editable mode
pip install -e .[dev]
```

#### Fixture Not Found

**Symptom:**
```
ERROR: fixture 'sample_model' not found
```

**Solution:**
- Ensure fixture is defined in `conftest.py` or same test file
- Check fixture name spelling
- Verify fixture scope (function, class, module, session)

#### Coverage Below Threshold

**Symptom:**
```
FAILED: coverage: total coverage (78.5%) is less than fail-under (80%)
```

**Solution:**
```bash
# Generate detailed coverage report
make coverage
open htmlcov/index.html

# Identify uncovered lines (red highlighting)
# Add tests for missing branches
```

#### Tests Pass Locally But Fail in CI

**Common causes:**
1. **Environment differences**:
   - Different Python versions
   - Missing dependencies
   - Platform-specific behavior

2. **Non-deterministic tests**:
   - Relying on current time
   - Random number generation without fixed seed
   - Filesystem race conditions

**Solutions:**
```python
# Fix random seed
import random
random.seed(42)

# Use fixed timestamps
from datetime import datetime
fixed_time = datetime(2024, 1, 1, 0, 0, 0)

# Use pytest-timeout for hanging tests
pytest.mark.timeout(10)
def test_thing():
    # ...
```

### CI Failure Troubleshooting

#### Lint Failures

**Auto-fix most issues:**
```bash
make format
make lint
```

**Common errors:**
- `F401: imported but unused` → Remove import
- `E501: line too long` → Break into multiple lines
- `W291: trailing whitespace` → Remove trailing spaces

#### Type Check Failures

**Common errors:**
- `error: Incompatible types` → Add type annotations
- `error: Missing return statement` → Add return or `-> None`
- `error: Argument has incompatible type` → Check function signature

**Suppressing false positives:**
```python
result = dangerous_operation()  # type: ignore[misc]
```

#### Coverage Failures

**Strategy:**
1. Run `make coverage` locally
2. Open `htmlcov/index.html`
3. Find uncovered lines (red highlighting)
4. Write tests for missing branches
5. Verify coverage improves

**Focus on:**
- Error handling branches
- Edge cases (None, empty, boundary values)
- Conditional logic (if/else, loops)

#### Conformance Test Failures

**Symptom:**
```
FAILED tests/conformance/test_parsing.py::TestParsingConformance::test_parsing_conformance
  Expected: PASS
  Actual: FAIL (SyntaxError: Unexpected token)
```

**Solution:**
1. Review YAML test case in `spec/conformance/`
2. Understand expected vs actual behavior
3. Fix implementation or update test case (if spec changed)
4. Re-run: `pytest tests/conformance/ -v`

### Getting Help

**If tests fail and you're stuck:**

1. **Check existing issues**: [github.com/pel-lang/pel/issues](https://github.com/pel-lang/pel/issues)
2. **Ask in discussions**: [github.com/pel-lang/pel/discussions](https://github.com/pel-lang/pel/discussions)
3. **Review PR comments**: Maintainers often provide feedback
4. **Consult documentation**:
   - [Contributing Guide](../CONTRIBUTING.md)
   - [Specification](../spec/)
   - [Examples](../examples/)

---

## Best Practices Summary

✅ **Do:**
- Write tests for all new code
- Test both success and error paths
- Use descriptive test names
- Keep tests isolated and deterministic
- Run tests locally before pushing
- Aim for >90% coverage on new code

❌ **Don't:**
- Skip writing tests ("I'll add them later")
- Test implementation details instead of behavior
- Write flaky tests (non-deterministic)
- Ignore coverage reports
- Commit code that fails CI

---

## Additional Resources

- **Pytest Documentation**: [docs.pytest.org](https://docs.pytest.org/)
- **Coverage.py Guide**: [coverage.readthedocs.io](https://coverage.readthedocs.io/)
- **PEL Contributing Guide**: [CONTRIBUTING.md](../CONTRIBUTING.md)
- **PEL Specification**: [spec/](../spec/)
- **Example Models**: [examples/](../examples/)

---

**Questions or suggestions?**  
Open an issue or discussion on [GitHub](https://github.com/pel-lang/pel/issues).
