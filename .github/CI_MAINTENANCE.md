# CI Maintenance Guide

## Overview

This document provides guidance on maintaining CI health and preventing common failures in the PEL project.

## Current CI Status Check

To check the current CI status for a pull request:
```bash
gh pr checks <PR_NUMBER>
```

To check CI for the current branch:
```bash
gh pr checks
```

## Common CI Failures and Solutions

### 1. Lint Failures (ruff)

**Symptoms:**
- CI Pipeline/lint job fails
- Errors about trailing whitespace, blank line whitespace, or other style issues

**Root Cause:**
- Code contains trailing whitespace or other style violations
- Typically happens when manually editing code without running formatter

**Solution:**
```bash
# Check for lint errors
make lint

# Auto-fix lint errors
ruff check compiler/ runtime/ tests/ --extend-exclude .github/prompts --fix

# For whitespace issues, use unsafe fixes
ruff check compiler/ runtime/ tests/ --extend-exclude .github/prompts --fix --unsafe-fixes

# Format code
make format
```

**Prevention:**
- Install pre-commit hooks: `make install` or `pre-commit install`
- Run `make ci` before committing
- Configure your editor to remove trailing whitespace on save

### 2. Type Check Failures (mypy)

**Symptoms:**
- CI Pipeline/lint job fails at mypy step
- Errors about incompatible types, missing type annotations, or type mismatches

**Root Cause:**
- Type annotations are incorrect or missing
- Using wrong types in assignments
- Duplicate attribute definitions

**Solution:**
```bash
# Check type errors
make typecheck

# Common fixes:
# - Add explicit type annotations: variable: dict[str, Any] = {...}
# - Remove duplicate definitions
# - Ensure function return types match actual returns
```

**Examples from Recent Fixes:**
```python
# WRONG: Implicit typing causes issues
action_ir = {"action_type": action.action_type}  # Inferred as dict[str, str]
action_ir["value"] = generate_expression(...)     # Error: expecting str, got dict

# CORRECT: Explicit typing
action_ir: dict[str, Any] = {"action_type": action.action_type}
action_ir["value"] = generate_expression(...)     # OK
```

```python
# WRONG: Duplicate definition
@dataclass
class Config:
    max_runs: int = 100000
    max_runs: int = 100000  # Error: redefinition

# CORRECT: Single definition
@dataclass
class Config:
    max_runs: int = 100000
```

### 3. Test Failures

**Symptoms:**
- Test jobs fail
- Specific tests fail or timeout

**Root Cause:**
- Code changes break existing functionality
- Tests have incorrect assertions
- Test dependencies not installed

**Solution:**
```bash
# Run all tests locally
make test

# Run with coverage
make coverage

# Run specific test file
pytest tests/unit/test_specific.py -v

# Run specific test
pytest tests/unit/test_specific.py::test_function_name -v
```

### 4. Security Scan Warnings

**Symptoms:**
- Security job shows warnings (usually doesn't fail due to `continue-on-error: true`)

**Root Cause:**
- Code patterns that bandit flags as potentially insecure
- Use of `assert`, `eval`, `exec`, etc.

**Solution:**
```bash
# Run security scan
make security

# Review warnings and either:
# 1. Fix the security issue
# 2. Add a # nosec comment with justification if it's a false positive
```

## Pre-Commit Hooks

Pre-commit hooks automatically check your code before you commit, catching issues early.

### Installation

```bash
# Install hooks (done automatically by make install)
pre-commit install
```

### Configured Hooks

The project uses these pre-commit hooks (.pre-commit-config.yaml):

1. **ruff**: Linting with auto-fix
2. **ruff-format**: Code formatting
3. **black**: Additional formatting
4. **mypy**: Type checking
5. **trailing-whitespace**: Remove trailing whitespace
6. **end-of-file-fixer**: Ensure files end with newline
7. **check-yaml**: Validate YAML syntax
8. **check-added-large-files**: Prevent large file commits
9. **check-merge-conflict**: Detect merge conflict markers

### Bypassing Hooks (Emergency Only)

If you need to commit without running hooks (after verifying with `make ci`):
```bash
git commit --no-verify -m "message"
```

**⚠️ Warning:** Only use `--no-verify` if you've already verified the code passes all checks with `make ci`.

## CI Workflow Files

The project has multiple CI workflows:

### `.github/workflows/ci.yml`
Main CI pipeline with:
- **lint**: ruff + mypy on Python 3.11
- **test**: pytest across Python 3.10, 3.11, 3.12 with coverage
- **security**: bandit security scan
- **build**: package building

### `.github/workflows/test.yml`
- **lint-and-test**: Combined lint and test across Python versions
- **conformance**: YAML validation and conformance tests

### `.github/workflows/language-eval.yml`
- Language specification validation
- Type checking
- Shellcheck for scripts

### `.github/workflows/benchmarks.yml`
- PEL-100 benchmark suite

### `.github/workflows/tutorial-qa.yml`
- Tutorial and documentation checks

## Best Practices

### Before Making Changes

1. **Pull latest changes:**
   ```bash
   git pull origin main
   ```

2. **Create a feature branch:**
   ```bash
   git checkout -b feature/my-feature
   ```

3. **Ensure CI passes on current branch before starting:**
   ```bash
   make ci
   ```

### While Developing

1. **Run relevant checks frequently:**
   ```bash
   # Quick lint check
   make lint
   
   # Run tests for affected area
   pytest tests/unit/test_affected_module.py -v
   ```

2. **Use editor configuration:**
   - Configure editor to remove trailing whitespace on save
   - Enable linting/type checking in editor
   - Use ruff/black formatting on save

### Before Committing

1. **Run full CI suite:**
   ```bash
   make ci
   ```

2. **Verify all checks pass:**
   - ✅ Lint (ruff)
   - ✅ Type check (mypy)
   - ✅ Security (bandit)
   - ✅ Tests (pytest with >80% coverage)

3. **If CI fails, fix issues before committing**

4. **Stage and commit:**
   ```bash
   git add <files>
   git commit -m "descriptive message"
   # Pre-commit hooks run automatically
   ```

### After Pushing

1. **Monitor CI status:**
   ```bash
   gh pr checks
   ```

2. **If CI fails:**
   - Pull the latest changes
   - Fix locally with `make ci`
   - Commit and push fixes
   - Verify CI passes

## Troubleshooting

### Pre-commit hooks are slow

Pre-commit hooks install their environments on first run, which can take several minutes. Subsequent runs are much faster.

To skip hooks temporarily (only if already verified with `make ci`):
```bash
git commit --no-verify
```

### CI passes locally but fails on GitHub

**Possible causes:**
1. Different Python versions - CI tests on 3.10, 3.11, 3.12
2. Different dependencies - ensure `requirements.txt` or `pyproject.toml` is up to date
3. Platform differences - CI runs on Ubuntu, you may be on different OS

**Solution:**
```bash
# Test with specific Python version
python3.10 -m pytest tests/
python3.11 -m pytest tests/
python3.12 -m pytest tests/
```

### Mypy errors that don't make sense

**Common causes:**
1. Stale mypy cache
   ```bash
   rm -rf .mypy_cache
   make typecheck
   ```

2. Missing type stubs
   ```bash
   pip install types-<package>
   ```

3. Need to add type ignore comment (last resort)
   ```python
   result = some_function()  # type: ignore[<error-code>]
   ```

## Recent CI Fixes (February 2026)

### Issue: Lint job failing with trailing whitespace errors

**Root Cause:**
- Code changes introduced trailing whitespace and blank lines with whitespace
- Duplicate `max_runs` definition in `RuntimeConfig`
- Mypy type errors from implicit dictionary typing
- Unused variables in test file

**Fix Applied:**
1. Ran `ruff check --fix --unsafe-fixes` to remove whitespace
2. Removed duplicate attribute definition
3. Added explicit type annotation: `action_ir: dict[str, Any]`
4. Removed unused test variables
5. Verified with `make ci` before pushing
6. Ensured pre-commit hooks are installed

**Lessons Learned:**
- Always run `make ci` before pushing
- Use `--unsafe-fixes` for whitespace issues
- Explicitly type dictionaries when they'll hold mixed types
- Remove unused variables or use underscore prefix if intentionally unused

## Makefile Commands Reference

```bash
# Setup
make install          # Install package with dev dependencies and pre-commit hooks

# Code Quality
make lint             # Run ruff linter
make format           # Format code with ruff
make typecheck        # Run mypy type checker
make security         # Run bandit security scanner

# Testing
make test             # Run test suite
make coverage         # Run tests with coverage report

# CI
make ci               # Run all CI checks (lint + typecheck + security + test)

# Cleanup
make clean            # Remove build artifacts and caches
```

## Emergency Procedures

### CI is broken and blocking merges

1. **Check if it's a flaky test:**
   ```bash
   gh pr checks --watch  # Re-run if needed
   ```

2. **Check recent commits:**
   ```bash
   git log --oneline -10
   ```

3. **Bisect to find breaking commit:**
   ```bash
   git bisect start
   git bisect bad HEAD
   git bisect good <last-known-good-commit>
   # Test each commit with: make ci
   ```

4. **Revert breaking commit if necessary:**
   ```bash
   git revert <commit-hash>
   git push
   ```

### CI taking too long

Some workflows are configured to `continue-on-error: true` or have reasonable timeouts. If CI is consistently slow:

1. Check for test inefficiencies
2. Review if all matrix combinations are necessary
3. Consider using test parallelization
4. Check if dependencies can be cached better

## Monitoring and Alerts

### How to check CI health

```bash
# For current PR
gh pr checks

# For specific PR
gh pr checks 42

# For main branch
gh run list --branch main --limit 10

# Watch CI progress
gh pr checks --watch
```

### Key metrics to monitor

- **Pass rate**: Should be >95% for main branch
- **Duration**: Lint ~30s, Tests ~1-2min, Full pipeline ~3-5min
- **Coverage**: Should maintain >80% (enforced by `--cov-fail-under=80`)

## Additional Resources

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Mypy Documentation](https://mypy.readthedocs.io/)
- [Pre-commit Documentation](https://pre-commit.com/)
- [Pytest Documentation](https://docs.pytest.org/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

## Contact

If CI issues persist or you need help:
1. Check existing GitHub Issues
2. Review recent PRs for similar problems
3. Ask in team chat/discussion
4. Create a new issue with:
   - CI workflow name
   - Error messages
   - Link to failed run
   - Steps to reproduce

---

**Last Updated:** February 20, 2026
**Maintained by:** PEL Core Team
