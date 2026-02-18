# Merge Requirements and Quality Gates

This document defines the quality gates and requirements that must be satisfied before merging code into the `main` branch of the PEL project.

---

## Table of Contents

1. [Overview](#overview)
2. [Required CI Checks](#required-ci-checks)
3. [Code Review Requirements](#code-review-requirements)
4. [Quality Thresholds](#quality-thresholds)
5. [Branch Strategy](#branch-strategy)
6. [Merge Process](#merge-process)
7. [Enforcement](#enforcement)

---

## Overview

All changes to `main` must go through a pull request (PR) and satisfy all merge gates. This ensures:
- **Code quality**: All code meets style, type safety, and quality standards
- **Test coverage**: New code is well-tested and doesn't break existing functionality
- **Security**: No known vulnerabilities are introduced
- **Review**: Changes are reviewed by maintainers for correctness and design

**No exceptions** - all PRs must satisfy all gates, including those from maintainers.

---

## Required CI Checks

All of the following CI checks must pass before a PR can be merged:

### 1. Lint Check ✅

**Tool:** `ruff`  
**Purpose:** Enforce code style and quality standards  
**Passing criteria:**
- No code style violations
- No unused imports
- No complexity issues
- Follows PEP 8 and project conventions

**Run locally:**
```bash
make lint
```

**Auto-fix:**
```bash
make format
```

---

### 2. Type Check ✅

**Tool:** `mypy`  
**Purpose:** Ensure type safety and catch type-related bugs  
**Passing criteria:**
- No type errors
- All public functions have type annotations
- Type hints are accurate and consistent

**Run locally:**
```bash
make typecheck
```

---

### 3. Test Suite ✅

**Tool:** `pytest`  
**Purpose:** Verify functionality and prevent regressions  
**Passing criteria:**
- All tests pass on Python 3.10, 3.11, 3.12
- No test failures or errors
- No flaky tests (must pass consistently)

**Run locally:**
```bash
make test
```

**Test categories:**
- **Unit tests**: `tests/unit/` - Component-level tests
- **Integration tests**: `tests/integration/` - End-to-end workflows
- **Conformance tests**: `tests/conformance/` - Spec compliance

---

### 4. Coverage Check ✅

**Tool:** `pytest-cov` / `coverage.py`  
**Purpose:** Ensure adequate test coverage  
**Passing criteria:**
- **Overall coverage ≥ 80%** (enforced in CI)
- **New code coverage ≥ 90%** (enforced in code review)
- Critical paths at 100% coverage (compiler, runtime core)

**Run locally:**
```bash
make coverage
open htmlcov/index.html
```

**Coverage targets by module:**
| Module | Minimum | Target |
|--------|---------|--------|
| `compiler/lexer.py` | 95% | 99%+ |
| `compiler/parser.py` | 95% | 98%+ |
| `compiler/typechecker.py` | 85% | 90%+ |
| `compiler/ir_generator.py` | 95% | 99%+ |
| `runtime/runtime.py` | 80% | 85%+ |
| `runtime/reporting.py` | 70% | 80%+ |
| Overall | **80%** | **90%** |

---

### 5. Security Scan ✅

**Tool:** `bandit`  
**Purpose:** Detect security vulnerabilities  
**Passing criteria:**
- No high severity issues
- No medium severity issues (or explicitly acknowledged and justified)
- All issues are reviewed and addressed

**Run locally:**
```bash
make security
```

**Common issues:**
- Use of `pickle` (potential code execution)
- SQL injection vulnerabilities
- Hardcoded secrets or credentials
- Unsafe use of `eval()`, `exec()`, or `subprocess`

---

### 6. Build Check ✅

**Tool:** Python `build` module  
**Purpose:** Ensure package builds correctly  
**Passing criteria:**
- Package builds without errors
- All dependencies are declared correctly
- No build warnings

**Run locally:**
```bash
pip install build
python -m build
```

---

### 7. Benchmark Check (for runtime changes) ✅

**Tool:** `benchmarks/score_benchmark.py`  
**Purpose:** Ensure benchmark suite passes and no regressions  
**Passing criteria:**
- PEL-100 benchmark: ≥90% success rate
- No new benchmark failures introduced
- Performance acceptable (no major regressions)

**Run locally:**
```bash
cd benchmarks
python score_benchmark.py pel_100/ --min-success-rate 90
```

**When required:**
- Changes to `runtime/runtime.py`
- Changes to `compiler/` that affect execution
- Changes to dimension system or type checker

---

## Code Review Requirements

### Approval Requirements

**All PRs require:**
- ✅ **At least 1 approval** from a project maintainer
- ✅ **No unresolved review comments** or change requests
- ✅ **Author has addressed all feedback**

### What Reviewers Check

Reviewers verify:

1. **Correctness**
   - Implementation matches specification/requirements
   - Edge cases are handled properly
   - No logical errors or bugs

2. **Design Quality**
   - Code is maintainable and follows project patterns
   - Abstractions are appropriate
   - No unnecessary complexity

3. **Test Quality**
   - Tests cover critical paths
   - Tests are clear and maintainable
   - Both success and error cases are tested

4. **Documentation**
   - Public APIs are documented
   - Complex logic has explanatory comments
   - README/docs updated if needed

5. **Security & Safety**
   - No security vulnerabilities introduced
   - Error handling is robust
   - Input validation is present

6. **Performance**
   - No obvious performance issues
   - Algorithms are appropriate for scale
   - Benchmarks pass (if applicable)

### Review Turnaround

Maintainers aim to review PRs within:
- **Simple changes**: 1-2 business days
- **Medium changes**: 2-3 business days  
- **Complex changes**: 3-5 business days

**Expedited review** available for:
- Critical bug fixes
- Security patches
- Release blockers

---

## Quality Thresholds

### Code Coverage

| Type | Minimum | Recommended | Enforcement |
|------|---------|-------------|-------------|
| **Overall** | **80%** | 90%+ | CI gate |
| **New code** | **90%** | 95%+ | Code review |
| **Critical modules** | 95% | 99%+ | Code review |
| **Bug fixes** | 100% | 100% | Code review |

**Coverage measurement:**
- Measured by `pytest-cov` with `coverage.py`
- Includes statement and branch coverage
- Excludes test files, type-checking blocks, and defensive code

### Test Requirements

All PRs must include tests unless:
- Documentation-only changes
- Build/CI configuration changes
- Trivial fixes (typos, formatting)

**Required tests:**
- Unit tests for new functions/classes
- Integration tests for new features
- Regression tests for bug fixes
- Error case tests (not just happy path)

### Documentation Requirements

Required for:
- New public APIs (functions, classes, modules)
- Changed behavior (update existing docs)
- New features (user-facing documentation)
- Complex algorithms (inline comments)

**Documentation formats:**
- Docstrings for all public APIs (Google style)
- README updates for user-facing changes
- `docs/` updates for architectural changes
- Inline comments for complex logic

---

## Branch Strategy

### Branch Naming

| Branch Pattern | Purpose | CI Runs |
|---------------|---------|---------|
| `main` | Production branch | ✅ Yes |
| `premerge/**` | Integration testing | ✅ Yes |
| `feature/**` | Development work | ❌ No (run locally) |
| `bugfix/**` | Bug fixes | ❌ No (run locally) |
| `release/**` | Release candidates | ✅ Yes |

### Workflow

```bash
# 1. Create feature branch from main
git checkout main
git pull
git checkout -b feature/my-feature

# 2. Develop and test locally
# ... make changes ...
make ci  # Run all checks locally

# 3. Push to GitHub (or create premerge branch for CI)
git push -u origin feature/my-feature
# Or for CI:
git checkout -b premerge/my-feature
git push -u origin premerge/my-feature

# 4. Open PR: feature/my-feature → main
# CI runs automatically on PR

# 5. Address review feedback
# ... make changes ...
git push

# 6. Maintainer merges after all gates pass
```

### Pre-Merge Checklist

Before requesting review, ensure:

- [ ] All CI checks pass (lint, typecheck, test, coverage, security, build)
- [ ] New tests are included and passing
- [ ] Coverage ≥ 80% overall, ≥ 90% for new code
- [ ] Documentation is updated (if applicable)
- [ ] Commit messages are clear and follow conventions
- [ ] Branch is up to date with `main`
- [ ] No merge conflicts
- [ ] Code is self-reviewed

---

## Merge Process

### 1. PR Opened

- Author opens PR with description, linked issue (if applicable)
- CI runs automatically
- Reviewers are assigned (automatic or manual)

### 2. CI Validation

- All CI checks must pass (see [Required CI Checks](#required-ci-checks))
- If CI fails, author fixes issues and pushes updates
- CI re-runs automatically on new pushes

### 3. Code Review

- At least 1 maintainer reviews the code
- Reviewer provides feedback via GitHub review comments
- Author addresses feedback and pushes updates
- Reviewer re-reviews until approved

### 4. Final Checks

Before merge, verify:
- ✅ All CI checks passed on latest commit
- ✅ At least 1 maintainer approval
- ✅ No unresolved review comments
- ✅ Branch up to date with `main`
- ✅ No merge conflicts

### 5. Merge

- Maintainer merges PR using **Squash and Merge** (preferred) or **Merge Commit**
- Commit message follows conventional commits format
- Branch is automatically deleted after merge

### Merge Strategies

**Squash and Merge** (preferred):
- Combines all commits into one
- Creates clean, linear history
- Ideal for feature branches with many WIP commits

**Merge Commit**:
- Preserves all individual commits
- Creates merge commit
- Use for larger features or when commit history is important

**Rebase and Merge**:
- Not used in this project (to avoid rewriting history)

---

## Enforcement

### Automated Enforcement

**GitHub branch protection rules** enforce:
- ✅ All required CI checks must pass
- ✅ At least 1 approval required
- ✅ Branch must be up to date with `main`
- ✅ No force pushes to `main`
- ✅ No deletion of `main`

**CI/CD enforces:**
- ✅ Coverage threshold ≥ 80%
- ✅ All tests pass on Python 3.10, 3.11, 3.12
- ✅ No lint errors
- ✅ No type errors
- ✅ No high/medium security issues

### Manual Enforcement

**Code reviewers enforce:**
- ✅ Code quality and design standards
- ✅ Test quality and coverage for new code (≥ 90%)
- ✅ Documentation completeness
- ✅ Security best practices
- ✅ Performance considerations

### Exceptions

**Emergency hotfixes:**
- May bypass approval requirements (with post-merge review)
- Must still pass all CI checks
- Requires notification to all maintainers

**No exceptions for:**
- CI check failures
- Coverage threshold
- Security scan failures

---

## Summary Table

| Gate | Tool | Threshold | Enforcement | Exceptions |
|------|------|-----------|-------------|------------|
| **Lint** | ruff | 0 errors | CI | None |
| **Type Check** | mypy | 0 errors | CI | None |
| **Tests** | pytest | 100% pass | CI | None |
| **Coverage** | pytest-cov | ≥ 80% overall | CI | None |
| **Coverage (new)** | coverage | ≥ 90% | Review | Rare |
| **Security** | bandit | 0 high/med | CI | Justified only |
| **Build** | build | Success | CI | None |
| **Code Review** | GitHub | 1+ approval | GitHub | Emergency only |
| **Branch Protection** | GitHub | Up to date | GitHub | None |

---

## Additional Resources

- **[Contributing Guide](../../CONTRIBUTING.md)** - How to contribute
- **[Testing Guide](../TESTING.md)** - Comprehensive testing documentation
- **[CI Troubleshooting](./TROUBLESHOOTING.md)** - Debugging CI failures
- **[Development Setup](../../CONTRIBUTING.md#development-setup)** - Local setup guide

---

**Questions about merge requirements?**  
Ask in [GitHub Discussions](https://github.com/pel-lang/pel/discussions) or open an issue.

**Last updated:** 2026-02-18
