---
name: merge

description: Merge a PR with strict branch and CI safety checks. This prompt enforces a comprehensive pre-merge validation checklist to ensure merges only occur from approved branches with passing CI. Follow the outlined steps carefully and abort if any check fails.

---

# Merge PR (with Safety Checks)

**CRITICAL**: This prompt enforces strict branch discipline and CI validation before merging.

## Pre-Merge Validation Checklist

Before proceeding with ANY merge operation, you MUST:

1. **Branch Verification**
   - Run `git branch --show-current` to verify current branch
   - ONLY proceed if on a `premerge/*` branch
   - NEVER merge from `feature/*` or other non-premerge branches
   - Read the PR to confirm the base branch (do NOT assume it's main)

2. **CI Local Validation** (NON-NEGOTIABLE)
   - Run `./scripts/ci-local-venv.sh` to replicate CI locally
   - ALL checks must pass (lint, typecheck, tests, backtest evaluator)
   - If ANY check fails, STOP and fix issues before proceeding
   - Document CI validation results in the PR description

3. **Base Branch Safety**
   - Identify the PR's base branch from GitHub (do NOT assume main)
   - NEVER merge main into the PR branch unless main is confirmed as the base
   - Verify no unintended branch switches have occurred

4. **PR Description Update**
   - Ensure PR description includes the complete checklist:
     * Title & summary of changes
     * Files changed and rationale
     * Tests added/updated with results
     * CI validation confirmation (✓ `./scripts/ci-local-venv.sh` passed)
     * Manual validation steps
     * Backward compatibility notes (if applicable)
   - Add any relevant context from the work performed
   - Link to related issues or documentation

5. **Final Safety Checks**
   - Verify no uncommitted changes: `git status`
   - Confirm all commits are pushed: `git log origin/$(git branch --show-current)..HEAD`
   - Check CI status on GitHub (must be green)
   - Review PR diff one final time for unintended changes

## Execution Steps

Once ALL validation checks pass:

1. **Update PR Description**
   - Add/update the PR checklist items
   - Summarize key changes and their impact
   - Note any breaking changes or migration requirements
   - Confirm CI validation passed locally

2. **Final Verification**
   - Ensure GitHub CI checks are complete and passing
   - Verify required approvals (if any) are obtained
   - Check for merge conflicts

3. **Merge**
   - Use GitHub's merge strategy appropriate for the project
   - Consider "Squash and merge" for cleaner history on main
   - Ensure commit message is descriptive

4. **Post-Merge**
   - Verify merge completed successfully
   - Confirm main branch CI passes after merge
   - Delete the merged premerge/* branch (if appropriate)

## Abort Conditions

STOP and DO NOT MERGE if:

- ❌ Not on a `premerge/*` branch
- ❌ `./scripts/ci-local-venv.sh` has not been run or failed
- ❌ GitHub CI checks are failing or pending
- ❌ Base branch is unclear or incorrect
- ❌ Uncommitted or unpushed changes exist
- ❌ Backward compatibility impact is unknown
- ❌ Tests are failing or missing

## Example PR Description Template

```markdown
## Summary
[Brief description of changes and why they were made]

## Changes
- [File/component changed]: [Rationale]
- [File/component changed]: [Rationale]

## Testing
- [x] Unit tests added/updated
- [x] Integration tests pass
- [x] Manual testing completed: [describe steps]
- [x] CI validation: `./scripts/ci-local-venv.sh` passed ✓

## Backward Compatibility
[Note any breaking changes or "No breaking changes"]

## Validation Steps
```bash
# Commands to reproduce/validate locally
./scripts/ci-local-venv.sh
pytest tests/specific_test.py
```

## Related Issues
Closes #[issue-number]
```

---

**AI Agent Workflow**: Read this prompt fully, execute validation steps in order, abort if any check fails, only proceed to merge when ALL checks pass.
