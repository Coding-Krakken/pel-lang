# CI Troubleshooting Guide

This guide helps you diagnose and fix common CI failures in the PEL project.

---

## Table of Contents

1. [Quick Diagnosis](#quick-diagnosis)
2. [Lint Failures](#lint-failures)
3. [Type Check Failures](#type-check-failures)
4. [Test Failures](#test-failures)
5. [Coverage Failures](#coverage-failures)
6. [Security Scan Failures](#security-scan-failures)
7. [Build Failures](#build-failures)
8. [Platform-Specific Issues](#platform-specific-issues)
9. [Getting Help](#getting-help)

---

## Quick Diagnosis

### Viewing CI Results

**In GitHub:**
1. Navigate to your PR or commit
2. Click the "Checks" tab
3. Click on the failed check to see logs
4. Scroll to the red ❌ section for error details

**In Terminal (local reproduction):**
```bash
# Run full CI suite locally
make ci

# Run individual checks
make lint
make typecheck
make test
make coverage
make security
```

### Common Failure Patterns

| Error Message | Likely Cause | Quick Fix |
|--------------|--------------|-----------|
| `ruff check failed` | Code style issues | `make format && make lint` |
| `mypy: error: ...` | Type annotation issues | Add type annotations |
| `FAILED tests/...` | Test assertion failed | Review test output, fix code |
| `coverage: total coverage (XX%) < 80%` | Insufficient test coverage | Add tests for uncovered lines |
| `bandit: High severity` | Security vulnerability | Review and fix security issue |
| `ImportError: No module` | Missing dependency | `pip install -e .[dev]` |

---

## Lint Failures

### Symptom
```
ruff check compiler/ runtime/ tests/
compiler/parser.py:123:5: F401 'ast_nodes.BinaryOp' imported but unused
runtime/runtime.py:456:80: E501 line too long (92 > 100 characters)
Found 2 errors.
```

### Common Errors

#### F401: Imported but unused
**Error:**
```
compiler/parser.py:123:5: F401 'ast_nodes.BinaryOp' imported but unused
```

**Fix:**
```python
# Remove the unused import
# Before:
from compiler.ast_nodes import BinaryOp, VariableDeclaration

# After (if BinaryOp is unused):
from compiler.ast_nodes import VariableDeclaration
```

#### E501: Line too long
**Error:**
```
runtime/runtime.py:456:80: E501 line too long (92 > 100 characters)
```

**Fix:**
```python
# Before:
result = calculate_complex_expression(parameter1, parameter2, parameter3, parameter4, parameter5)

# After:
result = calculate_complex_expression(
    parameter1, parameter2, parameter3, 
    parameter4, parameter5
)
```

#### W291: Trailing whitespace
**Error:**
```
compiler/lexer.py:234:20: W291 trailing whitespace
```

**Fix:**
Remove spaces at the end of the line.

#### I001: Import not sorted
**Error:**
```
compiler/parser.py:1:1: I001 import block is un-sorted or un-formatted
```

**Fix:**
```bash
# Auto-fix with ruff
make format
```

### Auto-Fix Strategy

```bash
# Format code (fixes most lint issues)
make format

# Check remaining issues
make lint

# If issues remain, fix manually
```

### Ignoring Specific Rules (Last Resort)

```python
# Ignore specific line
result = very_long_function_call()  # noqa: E501

# Ignore specific rule for file (in pyproject.toml)
[tool.ruff.lint.per-file-ignores]
"specific_file.py" = ["E501"]
```

**⚠️ Use sparingly** - prefer fixing the underlying issue.

---

## Type Check Failures

### Symptom
```
mypy -p compiler -p runtime
compiler/parser.py:123: error: Incompatible types in assignment (expression has type "str", variable has type "int")
runtime/runtime.py:456: error: Function is missing a return type annotation
Found 2 errors in 2 files
```

### Common Errors

#### Incompatible Types
**Error:**
```
compiler/parser.py:123: error: Incompatible types in assignment (expression has type "str", variable has type "int")
```

**Fix:**
```python
# Before:
count: int = "123"  # Wrong type!

# After:
count: int = 123
# Or if converting:
count: int = int("123")
```

#### Missing Return Type Annotation
**Error:**
```
runtime/runtime.py:456: error: Function is missing a return type annotation
```

**Fix:**
```python
# Before:
def calculate_total(values):
    return sum(values)

# After:
def calculate_total(values: list[float]) -> float:
    return sum(values)
```

#### Argument Has Incompatible Type
**Error:**
```
error: Argument 1 to "process" has incompatible type "str"; expected "int"
```

**Fix:**
```python
# Before:
process("123")  # process expects int

# After:
process(123)
# Or convert:
process(int("123"))
```

#### None Type Issues
**Error:**
```
error: Item "None" of "Optional[str]" has no attribute "upper"
```

**Fix:**
```python
# Before:
def process(value: Optional[str]) -> str:
    return value.upper()  # value might be None!

# After:
def process(value: Optional[str]) -> str:
    if value is None:
        return ""
    return value.upper()

# Or:
def process(value: Optional[str]) -> str:
    return value.upper() if value else ""
```

### Suppressing False Positives

```python
# When mypy is wrong (rare!)
result = complex_operation()  # type: ignore[misc]

# With explanation (better)
result = complex_operation()  # type: ignore[misc]  # TODO: Fix after mypy#12345 resolved
```

---

## Test Failures

### Symptom
```
FAILED tests/unit/test_parser.py::test_variable_declaration - AssertionError: assert 'revenue' == 'profit'
```

### Diagnosis Steps

1. **Read the full error message:**
```bash
pytest tests/unit/test_parser.py::test_variable_declaration -v
```

2. **Run with verbose output:**
```bash
pytest tests/unit/test_parser.py::test_variable_declaration -vv
```

3. **Show local variables:**
```bash
pytest tests/unit/test_parser.py::test_variable_declaration -l
```

4. **Enter debugger on failure:**
```bash
pytest tests/unit/test_parser.py::test_variable_declaration --pdb
```

### Common Causes

#### Assertion Failure
**Error:**
```
AssertionError: assert 'revenue' == 'profit'
```

**Fix:**
- Review test logic: is the test correct?
- Review implementation: is the code correct?
- Update test or code accordingly

#### Exception Not Raised
**Error:**
```
Failed: DID NOT RAISE <class 'CompilerError'>
```

**Fix:**
```python
# Test expects exception but none is raised
# Before:
with pytest.raises(CompilerError):
    compile("valid code")  # Doesn't raise!

# After:
with pytest.raises(CompilerError):
    compile("invalid code")  # Now raises as expected
```

#### Wrong Exception Type
**Error:**
```
Failed: Expected CompilerError but got TypeError
```

**Fix:**
- Check if implementation raises correct exception type
- Catch and re-raise with correct type if needed

#### Import Errors
**Error:**
```
ImportError: cannot import name 'NewClass' from 'compiler.ast_nodes'
```

**Fix:**
```bash
# Reinstall package in editable mode
pip install -e .[dev]
```

### Tests Pass Locally But Fail in CI

**Common causes:**

1. **Python version differences:**
   - Test may rely on Python 3.12 features but CI runs 3.10
   - Solution: Use version-compatible code or skip tests conditionally

2. **Non-deterministic tests:**
   - Tests rely on random values, timestamps, or filesystem race conditions
   - Solution: Use fixed seeds, mock timestamps, add synchronization

3. **Missing environment variables:**
   - Tests assume certain env vars are set
   - Solution: Provide default values or skip if not available

**Fixing non-deterministic tests:**
```python
# Before (flaky):
import random
def test_random_behavior():
    value = random.randint(1, 100)
    assert value > 50  # Fails 50% of the time!

# After (stable):
import random
def test_random_behavior():
    random.seed(42)  # Fixed seed
    value = random.randint(1, 100)
    assert value == 52  # Deterministic
```

---

## Coverage Failures

### Symptom
```
FAILED: coverage: total coverage (78.5%) is less than fail-under (80%)
```

### Diagnosis

**Generate detailed coverage report:**
```bash
make coverage
open htmlcov/index.html
```

**In HTML report:**
- Green lines: covered
- Red lines: not covered  
- Yellow lines: partially covered (branches)

### Strategies

#### 1. Test Missing Branches

**Before (partial coverage):**
```python
def calculate_discount(amount: float, is_premium: bool) -> float:
    if is_premium:
        return amount * 0.8  # Only this branch tested
    else:
        return amount * 0.9  # NOT tested - red in coverage report
```

**After (full coverage):**
```python
def test_calculate_discount_premium():
    result = calculate_discount(100.0, True)
    assert result == 80.0

def test_calculate_discount_regular():
    result = calculate_discount(100.0, False)  # Now tested!
    assert result == 90.0
```

#### 2. Test Error Handling

```python
def test_parser_raises_on_invalid_syntax():
    with pytest.raises(SyntaxError):
        parse("invalid { syntax")  # Tests error branch
```

#### 3. Test Edge Cases

```python
def test_handle_empty_input():
    result = process([])  # Tests empty case
    assert result == []

def test_handle_none_input():
    result = process(None)  # Tests None case
    assert result is None
```

### Acceptable Exclusions

Some code doesn't need coverage:

```python
# Main entry point
if __name__ == "__main__":  # pragma: no cover
    main()

# Type checking only
if TYPE_CHECKING:  # pragma: no cover
    from typing import Protocol

# Defensive error handling
else:
    raise AssertionError("Unreachable")  # pragma: no cover
```

### Coverage Too Low to Fix Immediately?

**Short-term:**
- Add `# pragma: no cover` to untestable code (sparingly!)
- Focus on testing critical paths first
- Plan to improve coverage incrementally

**Long-term:**
- Refactor code to be more testable
- Break large functions into smaller, testable units
- Add regression tests as bugs are discovered

---

## Security Scan Failures

### Symptom
```
>> Issue: [B301:blacklist] Use of pickle can be insecure
   Severity: Medium   Confidence: High
   Location: runtime/runtime.py:123
```

### Common Issues

#### B301: Pickle Usage
**Issue:** `pickle` can execute arbitrary code

**Fix:**
```python
# Before (insecure):
import pickle
data = pickle.loads(untrusted_input)

# After (secure):
import json
data = json.loads(untrusted_input)
```

#### B608: SQL Injection
**Issue:** String formatting in SQL queries

**Fix:**
```python
# Before (vulnerable):
query = f"SELECT * FROM users WHERE id = {user_id}"

# After (safe):
query = "SELECT * FROM users WHERE id = ?"
cursor.execute(query, (user_id,))
```

#### B603: Subprocess Without Shell Validation
**Issue:** Potential shell injection

**Fix:**
```python
# Before (vulnerable):
subprocess.run(f"ls {user_input}", shell=True)

# After (safe):
subprocess.run(["ls", user_input], shell=False)
```

### False Positives

If bandit flags safe code, suppress with comment:
```python
# Bandit flags this but it's safe because input is validated
result = eval(sanitized_expression)  # nosec B307
```

**⚠️ Only suppress if you're certain it's safe!**

---

## Build Failures

### Symptom
```
error: Package 'unknown-dependency' not found
ERROR: Could not build wheels for pel-lang
```

### Common Causes

#### Missing Dependencies

**Error:**
```
ModuleNotFoundError: No module named 'some_package'
```

**Fix:**
```toml
# Add to pyproject.toml
[project.dependencies]
dependencies = [
    "some_package>=1.0.0",
]
```

#### Version Conflicts

**Error:**
```
ERROR: Cannot install pel-lang because these package versions have conflicting dependencies
```

**Fix:**
- Review dependency versions in `pyproject.toml`
- Loosen version constraints if too strict
- Update conflicting packages

#### Build System Issues

**Error:**
```
error: invalid command 'bdist_wheel'
```

**Fix:**
```bash
pip install --upgrade setuptools wheel build
python -m build
```

---

## Platform-Specific Issues

### Windows

**Path separators:**
```python
# Before:
path = "tests/unit/test_parser.py"  # Fails on Windows

# After:
import os.path
path = os.path.join("tests", "unit", "test_parser.py")
# Or:
from pathlib import Path
path = Path("tests") / "unit" / "test_parser.py"
```

**Line endings:**
- Git may convert `\n` to `\r\n` on Windows
- Configure `.gitattributes`: `* text=auto`

### macOS

**Case-sensitive filesystem:**
- Linux/CI uses case-sensitive filesystem
- macOS is case-insensitive by default
- Ensure imports match actual file names exactly

### Python Version Differences

**3.10 vs 3.11 vs 3.12:**
```python
# Syntax that works in 3.10+:
def process(items: list[str]) -> dict[str, int]:  # Built-in generics (3.9+)
    ...

# Older Python 3.9 and below:
from typing import List, Dict
def process(items: List[str]) -> Dict[str, int]:
    ...
```

---

## Getting Help

### Before Asking

1. **Read the full error message** - it usually tells you what's wrong
2. **Search existing issues** - someone may have hit this before
3. **Try to reproduce locally** - run `make ci` to replicate CI environment
4. **Check recent commits** - did a recent change break something?

### How to Ask

**Good question includes:**
1. What you're trying to do
2. Exact error message (use code blocks)
3. What you've already tried
4. Relevant code snippets
5. Python version and OS

**Example:**
```
**Problem:** CI test fails with "AssertionError: assert 'USD' == 'EUR'"

**What I'm trying to do:**
Test currency conversion in runtime/runtime.py

**Error:**
```
FAILED tests/unit/test_runtime.py::test_currency_conversion
AssertionError: assert 'USD' == 'EUR'
```

**What I tried:**
- Ran test locally: passed ✅
- Checked Python version: 3.11 (same as CI)
- Reviewed test code: looks correct

**Code:**
```python
def test_currency_conversion():
    result = convert(100, "USD", "EUR")
    assert result.currency == "EUR"  # Fails in CI
```

**Environment:**
- Python 3.11.5
- Ubuntu 22.04 (CI uses ubuntu-latest)
```

### Where to Ask

1. **GitHub Issues**: [github.com/Coding-Krakken/pel-lang/issues](https://github.com/Coding-Krakken/pel-lang/issues)  
   For bugs, CI failures, unexpected behavior

2. **GitHub Discussions**: [github.com/Coding-Krakken/pel-lang/discussions](https://github.com/Coding-Krakken/pel-lang/discussions)  
   For questions, best practices, general help

3. **PR Comments**: Ask maintainers for specific feedback on your PR

---

## Prevention Tips

### Before Every Commit

```bash
# Run full CI suite locally
make ci

# This catches 95% of CI failures before pushing
```

### Use Pre-Commit Hooks

```bash
# Install once
pip install pre-commit
pre-commit install

# Runs automatically on every commit
# Catches formatting, lint issues immediately
```

### Run Tests Frequently

```bash
# During development, run tests often
pytest tests/unit/test_<your_module>.py -v

# Quick check
pytest tests/unit/ -x  # Stop on first failure
```

### Keep Dependencies Updated

```bash
# Update dependencies regularly
pip install --upgrade pip setuptools wheel
pip install -e .[dev] --upgrade
```

---

## Summary Checklist

When CI fails:

- [ ] Read the full error message carefully
- [ ] Identify which stage failed (lint, test, coverage, security, build)
- [ ] Reproduce failure locally with `make ci`
- [ ] Check this guide for the specific failure type
- [ ] Try suggested fixes
- [ ] Run `make ci` again to verify fix
- [ ] Push fixes and verify CI passes

**Still stuck?** Ask for help with a detailed question! 🚀

---

**Last updated:** 2026-02-18  
**Questions?** Open an issue on [GitHub](https://github.com/Coding-Krakken/pel-lang/issues)
