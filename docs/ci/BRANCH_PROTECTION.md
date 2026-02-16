# Branch Protection Rules

This document describes the branch protection configuration for the PEL repository.

## Main Branch Protection

The `main` branch should be protected with the following rules:

### Required Status Checks
All of these checks must pass before merging:
- **CI Pipeline / lint** - Code linting with ruff and type checking with mypy
- **CI Pipeline / test (3.10)** - Tests on Python 3.10
- **CI Pipeline / test (3.11)** - Tests on Python 3.11
- **CI Pipeline / test (3.12)** - Tests on Python 3.12
- **CI Pipeline / security** - Security scanning with bandit
- **CI Pipeline / build** - Package build verification

### Pull Request Requirements
- ✅ Require pull request before merging
- ✅ Require 1 approval from a code reviewer
- ✅ Dismiss stale pull request approvals when new commits are pushed
- ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging

### Additional Protections
- ✅ Require linear history (no merge commits)
- ✅ Do not allow bypassing the above settings
- ⛔ No force pushes
- ⛔ No deletions

## CI Trigger Rules

The CI pipeline is configured to run **only** on:
- `main` branch pushes
- `premerge/**` branch pushes
- Pull requests targeting `main`

### Why This Matters
- **Feature branches** (`feature/**`) do not trigger CI automatically
- This reduces CI usage and encourages local testing
- Use `premerge/**` branches when you want CI to run before creating a PR

## Development Workflow

### Standard Feature Development
```bash
# Create feature branch from main
git checkout main
git pull
git checkout -b feature/my-feature

# Make changes and test locally
make ci  # Run all checks locally

# Commit and push (no CI runs yet)
git add .
git commit -m "feat: implement feature"
git push -u origin feature/my-feature

# Create PR - CI will run on the PR
gh pr create --base main
```

### Using Premerge Branches
```bash
# Create premerge branch for CI validation
git checkout -b premerge/my-feature

# Push to trigger CI
git push -u origin premerge/my-feature
# CI runs automatically!

# After CI passes, create PR or merge to main
```

## Setting Up Branch Protection

### Via GitHub Web Interface

1. Go to repository **Settings** → **Branches**
2. Click **Add branch protection rule**
3. Branch name pattern: `main`
4. Configure the following:

#### Protect matching branches
- [x] Require a pull request before merging
  - [x] Require approvals: 1
  - [x] Dismiss stale pull request approvals when new commits are pushed
  - [x] Require review from Code Owners (if CODEOWNERS file exists)

#### Require status checks to pass before merging
- [x] Require status checks to pass before merging
- [x] Require branches to be up to date before merging
- Add these required status checks:
  - `lint`
  - `test (3.10)`
  - `test (3.11)`
  - `test (3.12)`
  - `security`
  - `build`

#### Additional settings
- [x] Require linear history
- [x] Do not allow bypassing the above settings
- [ ] Allow force pushes: **DISABLED**
- [ ] Allow deletions: **DISABLED**

5. Click **Create** or **Save changes**

### Via GitHub CLI

```bash
# Install GitHub CLI if not already installed
# https://cli.github.com/

# Enable branch protection
gh api repos/Coding-Krakken/pel-lang/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["lint","test (3.10)","test (3.11)","test (3.12)","security","build"]}' \
  --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true}' \
  --field enforce_admins=true \
  --field restrictions=null \
  --field required_linear_history=true \
  --field allow_force_pushes=false \
  --field allow_deletions=false
```

## Verifying Protection

After setting up branch protection, verify it works:

1. Try to push directly to main (should fail):
   ```bash
   git checkout main
   echo "test" >> test.txt
   git add test.txt
   git commit -m "test"
   git push  # Should be rejected!
   ```

2. Create a PR and verify status checks appear
3. Try to merge PR before checks pass (should be blocked)
4. After checks pass, merge should be allowed

## Local CI Validation

Before pushing code, always run local CI checks:

```bash
# Install dependencies and hooks
make install

# Run all CI checks locally
make ci

# Individual checks
make lint        # Linting
make typecheck   # Type checking
make test        # Tests only
make security    # Security scan
make coverage    # Tests with coverage report
```

## Coverage Requirements

- **Minimum coverage**: 95%
- Coverage is enforced in CI via `--cov-fail-under=95`
- View coverage report: `make coverage` (opens `htmlcov/index.html`)

## Troubleshooting

### CI not running on my branch
- Check branch name - CI only runs on `main` and `premerge/**`
- Rename your branch: `git checkout -b premerge/$(git rev-parse --abbrev-ref HEAD)`

### Status checks not appearing on PR
- Wait 1-2 minutes for CI to start
- Check the "Actions" tab to see if workflow is queued
- Verify the workflow file exists at `.github/workflows/ci.yml`

### Cannot merge PR
- Ensure all required status checks are green
- Get 1 approval from a reviewer
- Rebase if branch is not up to date: `git pull --rebase origin main`

### Local CI passes but GitHub CI fails
- Ensure you're testing with the same Python version (3.11 recommended)
- Commit any uncommitted files
- Check for environment-specific issues (paths, OS differences)

## References

- [GitHub Branch Protection Documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [GitHub Required Status Checks](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches#require-status-checks-before-merging)
- [Pre-commit Documentation](https://pre-commit.com/)
