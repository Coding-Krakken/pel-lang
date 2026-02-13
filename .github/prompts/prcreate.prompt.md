---
name: prcreate
description: Create a new feature branch, implement changes, and open a Pull Request with a detailed description.
---

Create a new feature branch from the current main branch and implement the required changes for this task.

CRITICAL RULE — BRANCH SAFETY
You must ALWAYS review the PR from the PR branch itself.
You must NEVER review from main, a local feature branch, or any other branch.
You must always know which branch you are on, why you are on it, and whether switching branches is explicitly permitted by this prompt
Beyond all else, you must avoid merging the wrong base branch.
If at any point you are unsure which branch you are on, you must run:
git branch --show-current
to confirm.
If you find yourself on the wrong branch, you must STOP and fix it before proceeding.

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

CI + BRANCH DISCIPLINE (STRICT, NON-NEGOTIABLE)

- CI must ONLY run on:
  - main
  - branches matching premerge/\* (premerge/\*\*)

- You MUST NOT do any work that causes CI to run on feature/\* or any other branches.
  - Do NOT open PRs from feature/\* to main if CI would run.
  - Do NOT push commits to branches that would trigger CI outside main/premerge/\*.

- When a change set is ready for CI:
  1. Create a premerge branch from the working branch:
     - git checkout <working-branch>
     - git checkout -b premerge/<short-name>
     - git push -u origin premerge/<short-name>
  2. Open/target the PR from premerge/\* → main.

- BRANCH SAFETY
  - Never create extra “temp” branches.
  - Never switch branches unless the prompt explicitly allows it.
  - Before any commit or push, run: git branch --show-current
  - If you are on the wrong branch, STOP and correct it before proceeding.

- BASE BRANCH SAFETY
  - Never assume the base branch is main. Always read it from the PR.
  - Never merge main into a PR branch unless main is confirmed to be the PR base branch.
