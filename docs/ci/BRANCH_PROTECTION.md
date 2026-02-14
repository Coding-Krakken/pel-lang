# Branch Protection Setup Guide

This document provides step-by-step instructions for configuring GitHub branch protection rules to enforce the CI/CD quality gates defined in this repository.

## Overview

The PEL repository uses a multi-stage CI pipeline to ensure code quality:
- **Lint**: Code formatting (black, ruff)
- **Type Check**: Type safety (mypy - informational)
- **Test**: Unit tests with ≥95% coverage across Python 3.10, 3.11, 3.12
- **Docs**: Documentation smoke tests

## Branch Protection Configuration

### Protected Branches

Apply these rules to the following branches:
- `main` - Primary development branch
- `premerge/**` - Pre-merge integration branches

### Required Settings

#### 1. Enable Branch Protection

Navigate to: **Settings → Branches → Add branch protection rule**

Configure the following settings:

#### 2. Branch Name Pattern

```
main
```

Create a separate rule for:

```
premerge/**
```

#### 3. Required Status Checks

Enable: **☑ Require status checks to pass before merging**

Select the following required checks:
- `lint`
- `test (3.10)`
- `test (3.11)`
- `test (3.12)`
- `docs`

**Note**: `typecheck` is informational only and should not block merges (it will show type errors for legacy code that are being addressed incrementally).

#### 4. Additional Settings

Recommended settings:

- **☑ Require branches to be up to date before merging**
  - Ensures CI runs on the latest code
  
- **☑ Require conversation resolution before merging**
  - All review comments must be addressed
  
- **☐ Require approval from Code Owners** (optional)
  - Enable if you have CODEOWNERS file
  
- **☑ Require linear history** (optional)
  - Prevents merge commits, requires rebase or squash
  
- **☑ Include administrators**
  - Enforces rules for all users including admins

#### 5. Restrictions (Optional)

If you want to restrict who can push to protected branches:
- **Restrict pushes that create matching branches**
- **Restrict who can push to matching branches**: Add specific users/teams

## Workflow Trigger Configuration

The CI workflow (`.github/workflows/ci.yml`) is configured to run on:

```yaml
on:
  push:
    branches:
      - main
      - 'premerge/**'
  pull_request:
    branches:
      - main
```

This ensures:
- Direct pushes to `main` or `premerge/*` branches trigger CI
- Pull requests targeting `main` trigger CI for validation

## Local Development

Developers should run CI locally before pushing:

```bash
# Install pre-commit hooks (runs automatically on git commit)
make install-hooks

# Run full CI suite manually
make ci

# Run individual checks
make lint       # Code formatting
make typecheck  # Type checking (informational)
make test       # Tests with coverage
```

## Coverage Requirements

All code changes must maintain minimum test coverage:
- **Minimum**: 95%
- **Current**: 100%

The `test` job enforces this with:
```bash
pytest --cov=compiler --cov=runtime --cov-fail-under=95
```

## Handling CI Failures

### Lint Failures

```bash
# Auto-fix most issues
black .
ruff check --fix .

# Verify
make lint
```

### Test Failures

```bash
# Run tests locally
pytest tests/ -v

# Run with coverage report
make test

# Run specific test file
pytest tests/unit/test_parser.py -v
```

### Type Check Issues

Type checking is informational and does not block merges. Type errors in legacy code are being addressed incrementally.

```bash
# View type check results
make typecheck

# Check specific directory
mypy compiler/ --explicit-package-bases
```

## Emergency Overrides

If you need to bypass branch protection (e.g., critical hotfix):

1. Contact repository maintainer
2. Document reason in commit message
3. Create follow-up issue to address CI bypass
4. Plan to restore protection immediately after fix

## Verification

After configuring branch protection:

1. Create a test branch
2. Make a trivial change
3. Create PR to `main`
4. Verify all CI checks run
5. Verify merge is blocked if any check fails
6. Close test PR

## Troubleshooting

### CI doesn't run on PR

- Check workflow trigger configuration in `.github/workflows/ci.yml`
- Verify PR targets `main` branch
- Check GitHub Actions are enabled for the repository

### Status check not appearing as required

- Ensure exact name matches in both workflow and branch protection
- CI must run at least once before it appears in the list
- Create a test PR to trigger the workflow

### Merge blocked despite passing checks

- Verify "Require branches to be up to date" is not causing issues
- Rebase/merge `main` into your branch
- Re-run CI if needed

## Support

For questions or issues:
- GitHub Issues: https://github.com/Coding-Krakken/pel-lang/issues
- Maintainer: davidtraversmailbox@gmail.com

## References

- [GitHub Branch Protection Documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [GitHub Actions Status Checks](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/about-status-checks)
