# Branch Protection Rules

## Main Branch Protection

The `main` branch is protected with the following rules to ensure code quality and stability:

### Required Status Checks

All of the following CI checks must pass before merging:

- **CI Pipeline / lint** - Code linting with ruff
- **CI Pipeline / test (3.10)** - Test suite on Python 3.10
- **CI Pipeline / test (3.11)** - Test suite on Python 3.11
- **CI Pipeline / test (3.12)** - Test suite on Python 3.12
- **CI Pipeline / security** - Security scan with bandit
- **CI Pipeline / build** - Package build verification

### Required Reviews

- Require at least **1 approval** from a code owner or maintainer
- Dismiss stale pull request approvals when new commits are pushed
- Require review from code owners (when CODEOWNERS file is present)

### Branch Restrictions

- **No force pushes** - Protects commit history integrity
- **No deletions** - Prevents accidental branch removal
- **Require linear history** - Enforces clean, linear commit history
- **Require branches to be up to date** - Must merge latest main before merging PR

## CI Trigger Rules

CI runs **ONLY** on the following branches:

- `main` - Production branch
- `premerge/**` - Pre-merge integration branches

CI does **NOT** run on:

- `feature/**` - Development branches
- Any other branch patterns

### Why This Matters

This branch strategy:
- Reduces CI resource consumption
- Prevents unnecessary CI runs during development
- Ensures thorough testing before main branch integration
- Maintains clean separation between development and integration environments

## Development Workflow

### Standard Flow

1. **Development Phase**
   ```bash
   # Create feature branch from main
   git checkout main
   git pull origin main
   git checkout -b feature/my-feature
   
   # Work on your feature (no CI runs)
   # Run local checks: make ci
   git add .
   git commit -m "feat: implement my feature"
   ```

2. **Pre-merge Phase**
   ```bash
   # When ready for CI validation
   git checkout -b premerge/my-feature
   git push -u origin premerge/my-feature
   
   # CI runs automatically on premerge branch
   ```

3. **Pull Request**
   ```bash
   # Open PR: premerge/my-feature → main
   # CI runs on PR events
   # Request reviews from team members
   ```

4. **Merge**
   ```bash
   # After approval + green CI:
   # Merge via GitHub UI (squash and merge preferred)
   # CI runs on main after merge
   ```

### Local Development Commands

Run the full CI suite locally before pushing:

```bash
# Run all CI checks
make ci

# Individual checks
make lint          # Linting
make typecheck     # Type checking
make security      # Security scan
make test          # Test suite
make coverage      # Tests with coverage report
```

## Required Checks Configuration

To enable these protections on GitHub:

1. Go to **Settings** → **Branches**
2. Add branch protection rule for `main`
3. Enable:
   - ✅ Require a pull request before merging
   - ✅ Require approvals (1)
   - ✅ Dismiss stale pull request approvals when new commits are pushed
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - ✅ Require linear history
   - ✅ Do not allow bypassing the above settings
4. Select required status checks:
   - `lint`
   - `test (3.10)`
   - `test (3.11)`
   - `test (3.12)`
   - `security`
   - `build`
5. Enable:
   - ✅ Restrict who can push to matching branches
   - ✅ Do not allow force pushes
   - ✅ Do not allow deletions

## Emergency Procedures

In case of critical production issues:

1. **Hotfix Branch**
   ```bash
   git checkout main
   git checkout -b premerge/hotfix-issue-name
   # Make minimal fix
   git commit -m "fix: critical issue description"
   git push -u origin premerge/hotfix-issue-name
   ```

2. **Fast-track Review**
   - Open PR with "HOTFIX:" prefix in title
   - Request immediate review from maintainers
   - CI must still pass (no exceptions)
   - Requires 1 approval (can be expedited)

3. **Post-merge Verification**
   - Monitor CI on main branch
   - Verify fix in production
   - Document incident in post-mortem

## Questions?

For questions about branch protection or CI/CD process:
- Open an issue labeled `ci/cd`
- Contact repository maintainers
- See [CONTRIBUTING.md](../../CONTRIBUTING.md) for contribution guidelines
