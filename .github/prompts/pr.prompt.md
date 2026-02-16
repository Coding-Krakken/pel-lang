---
name: pr
description: Create a new feature branch, implement changes, and open a Pull Request with a detailed description.
---
Create a new feature branch from the repository default branch (discover with `gh repo view --json defaultBranchRef`) and implement the required changes for this task.

This prompt is for an autonomous agent. Enforce branch, push, and PR safety checks automatically:

- Base branch selection: determine the correct base branch programmatically. Do NOT assume `main`.
- Working tree must be clean (`git status --porcelain` == empty) before creating a branch.
- Branch naming: use `feature/<short-description>` or `fix/<short-description>`. Verify branch does not already exist remotely.
- Commit hygiene: small, focused commits; run `git commit --no-verify` only if pre-commit hooks are satisfied.
- Pre-push gates: run format, lint, typecheck, and unit tests locally before pushing.
- Push policy: push to `origin/feature/...`. Confirm remote push succeeded (`git remote show origin` + `git fetch`).
- PR base: open PR against the repository default branch unless task specifies a different base. If opening against `main`/`master`, require a label `allow-main-pr` or explicit policy approval to proceed.

Follow these rules:

1. Branching
   - Create a new branch using a clear, descriptive name.
   - Use the format: feature/<short-description> or fix/<short-description>.

2. Implementation
   - Make all necessary code, configuration, and documentation changes.
   - Follow the existing project architecture, naming conventions, and coding standards.
   - Keep commits small, logical, and descriptive.
   - Ensure the solution is production-ready and meets elite engineering standards (similar to Microsoft/Google internal quality bars).

3. Testing & Validation
   - Add or update unit, integration, and/or end-to-end tests as needed.
   - Ensure all tests pass.
   - Fix any linting, type, or build errors.
   - Verify the project builds and runs successfully.

4. Documentation
   - Update README, inline comments, or other docs if behavior or usage changes.
   - Document any new environment variables, endpoints, or commands.

5. Pull Request
   - Push the branch to the remote repository.
   - Open a Pull Request against the main branch.
   - Use a clear, professional PR title.

6. PR Description must include:
   - Summary of changes
   - Problem being solved
   - Technical approach
   - Key files/modules affected
   - Testing performed
   - Screenshots or logs if relevant
   - Any risks, migrations, or follow-ups

Do not open the PR until:
- All tests pass
- The build succeeds
- There are no obvious errors or warnings
