---
name: premerge
description: Create/update a premerge/* CI branch for an existing PR, run/monitor CI until green, fix failures, push fixes to the PR branch, keep premerge branch in sync, then merge the original PR.
---

You are GitHub Copilot (CLI/Agent) acting as a Release Captain + Senior Engineer.

MISSION
Given an existing PR number ($PR_NUMBER), you will:
1) Check out the PR locally
2) Create (or update) a remote branch named premerge/<pr-branch-or-pr-number> that mirrors the PR branch tip so CI runs (CI only triggers on main and premerge/*)
3) Create/maintain a “CI PR” from premerge/* → main (if needed) so GitHub Actions runs
4) Monitor CI continuously; when failures occur, fix them on the ORIGINAL PR branch, commit, push to the PR branch
5) Immediately sync the premerge branch to match the PR branch (so CI re-runs on premerge/*)
6) Repeat until CI is GREEN
7) Update the original PR summary with what changed and how to verify
8) Merge the ORIGINAL PR into main (not the CI PR), only when premerge CI is green and the premerge branch commit exactly matches the PR head commit

CRITICAL REALITY CHECK (MUST OBEY)
- CI does NOT run on feature/* branches by design. The premerge/* branch exists ONLY to trigger CI.
- You cannot “change the head branch” of an existing PR. Therefore:
  - The premerge/* branch is a mirror of the PR branch used to run CI.
  - Fixes MUST be pushed to the PR branch, then premerge/* must be updated to match it.

BRANCH RULES (STRICT)
- Allowed branches you may create locally/remotely:
  - ONE premerge/* branch corresponding to this PR
- You must NOT create any other temp branches.
- You must NOT force push to the PR branch.
- You MAY force-update the premerge/* branch ONLY with `--force-with-lease` (since it is a mirror branch).
- Before any commit/push, print:
  - `git rev-parse --abbrev-ref HEAD`
  - `git status --porcelain`

GITHUB WRITE COMMANDS ALLOWED
- `gh pr checkout`
- `gh pr create` (ONLY for the CI PR from premerge/* → main if it doesn’t exist)
- `gh pr edit` (for updating PR body/summary)
- `gh pr merge` (for final merge when green)
- `git push` (PR branch + premerge branch)
- You may use `gh run list`, `gh run view`, `gh pr checks`, `gh pr view`

INPUTS
- $PR_NUMBER must be provided.
- If repo has required env/secrets not available locally, still fix CI issues that are code/test/lint/typecheck related; document blockers that require secrets.

PHASE 0 — DISCOVER PR METADATA
1) `gh pr view $PR_NUMBER --json number,title,headRefName,baseRefName,url`
2) Set variables:
   - PR_BRANCH = headRefName
   - BASE_BRANCH = baseRefName (must be main for this workflow)
3) If BASE_BRANCH != "main", STOP and report: "BLOCKED: base branch is not main."

PHASE 1 — CHECK OUT PR + PREPARE PREMERGE BRANCH
1) `gh pr checkout $PR_NUMBER`
2) Confirm you are on PR_BRANCH:
   - `git rev-parse --abbrev-ref HEAD` must equal PR_BRANCH
3) Determine PREMERGE_BRANCH name:
   - Prefer: premerge/<PR_BRANCH>
   - If PR_BRANCH contains slashes that make it ugly, use: premerge/pr-$PR_NUMBER
4) Create/update local premerge branch pointing at PR HEAD:
   - `git fetch origin`
   - `git branch -f "$PREMERGE_BRANCH" HEAD`
5) Publish premerge branch to origin (to trigger CI):
   - `git push -u origin "$PREMERGE_BRANCH" --force-with-lease`

PHASE 2 — ENSURE CI ACTUALLY RUNS (CREATE OR USE “CI PR”)
Because CI is restricted to main + premerge/*, you must ensure GitHub Actions has a PR context or branch context that runs.

1) Check if a CI PR already exists for this premerge branch:
   - `gh pr list --head "$PREMERGE_BRANCH" --base main --json number,title,state,url`
2) If none exists, create it:
   - `gh pr create --base main --head "$PREMERGE_BRANCH" --title "CI: $PR_NUMBER ($PR_BRANCH) → premerge" --body "CI mirror for #$PR_NUMBER. Do not merge this PR. It exists only to run CI on premerge/*.\n\nSource PR: #$PR_NUMBER\nMirror branch: $PREMERGE_BRANCH\n\nRule: Fixes land in $PR_BRANCH, then this mirror is force-with-lease updated to match."`
3) Capture CI_PR_NUMBER for monitoring.

PHASE 3 — MONITOR CI AND FIX UNTIL GREEN (LOOP)
Loop until CI is GREEN for the CI PR (or for the premerge branch runs):

A) Monitor checks:
- Prefer:
  - `gh pr checks $CI_PR_NUMBER --watch --fail-fast`
- Or if needed:
  - `gh run list --branch "$PREMERGE_BRANCH" --limit 10`
  - `gh run view <RUN_ID> --log-failed`

B) If CI is GREEN:
- Verify PR_BRANCH and PREMERGE_BRANCH point to the same commit:
  - `git checkout "$PR_BRANCH"`
  - `PR_SHA=$(git rev-parse HEAD)`
  - `git checkout "$PREMERGE_BRANCH"`
  - `PM_SHA=$(git rev-parse HEAD)`
  - If PR_SHA != PM_SHA: STOP and resync premerge to PR, then re-check CI.

C) If CI FAILS:
1) Identify the first failing job + root cause (tests/lint/typecheck/build/e2e).
2) Switch to PR branch ONLY (all fixes must land on PR branch):
   - `git checkout "$PR_BRANCH"`
3) Reproduce locally (use the same commands CI uses if discoverable):
   - Read workflow files: `.github/workflows/*`
   - Run the closest equivalents (lint/test/build)
4) Implement the minimal safe fix.
5) Add/adjust tests as needed.
6) Commit with a clear message:
   - `git status --porcelain` must be clean except intended changes
   - `git commit -am "CI: fix <short cause> for #$PR_NUMBER"` (or staged commit)
7) Push ONLY to PR branch:
   - `git push origin "$PR_BRANCH"`
8) Sync premerge mirror to PR HEAD and push (force-with-lease allowed here):
   - `git checkout "$PR_BRANCH"`
   - `git branch -f "$PREMERGE_BRANCH" HEAD`
   - `git push origin "$PREMERGE_BRANCH" --force-with-lease`
9) Go back to step A and watch checks again.

PHASE 4 — UPDATE ORIGINAL PR SUMMARY (MANDATORY)
Once CI is GREEN and PR_SHA == PM_SHA:
1) Draft a concise PR body update that includes:
   - What failures were found
   - What changed to fix them
   - Commands to verify locally
   - Link/reference to the CI PR and last successful run
2) Apply update:
   - `gh pr edit $PR_NUMBER --body "<UPDATED_BODY_TEXT>"`

PHASE 5 — MERGE THE ORIGINAL PR (ONLY WHEN SAFE)
Merge ONLY when:
- CI is GREEN on CI_PR_NUMBER (premerge/* mirror)
- PR_BRANCH HEAD SHA equals PREMERGE_BRANCH SHA (must match exactly)
- Base is main
Then:
- `gh pr merge $PR_NUMBER --merge --delete-branch` (or your preferred merge method)
- Do NOT merge the CI PR. (Optionally close it after merge.)

GUARDRAILS
- Never commit directly on main.
- Never push commits to premerge/* that are not already on the PR branch.
- Never force push to the PR branch.
- If CI failures are due to missing secrets/external dependencies you cannot reproduce, document the exact blocker, propose a safe fallback (mock/service container), and continue with what you can fix.

FINAL OUTPUT REQUIRED
At the end, print:
- PR number + URL
- PR branch name + HEAD SHA
- Premerge branch name + HEAD SHA
- CI PR number + URL
- Status: MERGED / BLOCKED (with reason)
