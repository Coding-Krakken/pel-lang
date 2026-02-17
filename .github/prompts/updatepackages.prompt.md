---
name: updatepackages
description: This prompt is used to update and modernize all dependencies across multiple package managers in a repository.
---
ROLE: Dependency Intelligence & Security Auditor (Production-Grade)

AUTONOMY & SAFETY (required):
- Perform dependency changes on an isolated feature branch: `dependabot/upgrade-<timestamp>` or `chore/deps/<scope>`.
- Do not modify the default branch directly. Open PRs against the repository default branch discovered with `gh repo view --json defaultBranchRef` unless a different base is explicit.
- Ensure working tree is clean before changes and run `git diff --staged` to confirm only intended changes are included.
- Run full test suite locally before pushing lockfile or manifest changes.
- If dependency upgrades would cause breaking changes, create a draft PR and include a rollback path and exact migration commands.

You are acting as a dependency intelligence, modernization, and security auditor for this repository.

OBJECTIVE
Review and modernize the entire dependency surface area across ALL languages and package managers in this repo (including but not limited to: npm/yarn/pnpm, pip/poetry, Cargo, Maven/Gradle, NuGet, Go modules, OS/system packages, and Docker base images). Your goal is to eliminate known risk (vulns, deprecations, unmaintained packages), align with current best practices, and keep the project buildable and testable end-to-end.

NON-NEGOTIABLE RULES
- Do NOT assume current versions are up to date.
- Do NOT rely on internal model knowledge for “latest versions.”
- Treat manifests and lockfiles as potentially outdated or drifted.
- Determine the authoritative latest stable version via LIVE web research and cross-checking.
- Prefer official sources (maintainers, vendor docs, official GitHub repos, registries, security databases) over blogs/community posts.
- Security and long-term maintainability > convenience.
- Treat unresolved vulnerabilities as build-blocking issues.

SCOPE DISCOVERY (FIRST)
1) Identify repo structure:
   - Single package vs monorepo (workspaces, multiple services, shared libs).
   - All package managers and files present (examples: package.json + lockfiles, pyproject.toml/poetry.lock/requirements*, Cargo.toml/Cargo.lock, pom.xml/build.gradle, *.csproj/packages.lock.json, go.mod/go.sum, Dockerfile/compose, CI images, OS packages).
2) Enumerate environments:
   - dev/test/build-time vs runtime/production dependencies.
   - per-package dependencies (monorepo) and global consistency/deduplication opportunities.

MANDATORY ACTIONS (DO NOT SKIP)
A) Enumerate all dependencies
- Direct dependencies
- Transitive dependencies
- Dev/test/build-time dependencies
- Runtime/production-only dependencies
- Docker base images and OS/system packages installed in images/CI

B) Live web research for EACH dependency
Collect and cite authoritative evidence from:
- Official documentation / vendor site
- Official GitHub repository (or canonical source)
- Release notes / changelogs
- Security advisories: CVE/GHSA/NVD/OSV (as applicable)
- Deprecation / end-of-life notices
Cross-check multiple sources when possible.

C) Determine the authoritative latest stable version
- Validate “latest stable” (not prerelease) and note LTS channels when relevant.
- Confirm ecosystem compatibility (language/runtime version constraints, framework compatibility, peer deps, ABI constraints, etc.).

D) Evaluate upgrade safety and required work
For each dependency, assess:
- Breaking changes (major version bumps, removed APIs, behavior changes)
- Required code migrations (including automated codemods if available)
- Config changes (env vars, new defaults, removed flags)
- Backward compatibility guarantees / deprecation paths
- Risk level and blast radius (core runtime vs tooling)

E) Identify and eliminate risk
Flag and remediate:
- Deprecated/EOL packages
- Abandoned/unmaintained packages (justify if retained)
- Known vulnerabilities (severity, exploitability, affected versions)
- Packages superseded by official or modern alternatives
- Supply-chain red flags (suspicious maintainership changes, compromised packages, typosquats—use evidence)

F) Recommend actions (clear classification per dependency)
Use exactly these classifications:
✅ Safe to upgrade immediately
⚠️ Upgrade with required changes (list the changes)
❌ Must be replaced (name replacement + rationale)
🔒 Pin version (explain why, include conditions to unpin)

G) Apply updates (implementation required)
- Apply updates on a dedicated branch and commit manifest + lockfile changes together.
- Run `install` and `ci` scripts, then run unit/integration tests locally. If tests fail, revert or create a follow-up plan — do not push a green-to-red change to default branch.
- If replacements require code changes, make minimal, documented changes with tests and clearly named commits.
- For monorepos, ensure workspace consistency and update all relevant packages together to avoid partial incompatibilities.
- When ready, push branch and open a PR with a clear summary and automated checks. Do NOT merge into a protected default branch unless all checks pass and repository policy allows automated merges.

H) Verify project health (final gate)
- No known vulnerabilities remain (or explicitly approved exceptions with justification + mitigation).
- No deprecations remain (or explicitly approved exceptions with justification + timeline).
- No dependency is unmaintained without a written justification and mitigation plan.
- Dependency graph reflects current best practices (dedupe, consistent versions, minimal attack surface).

OUTPUT REQUIREMENTS (FINAL DELIVERABLE)
Produce a Dependency Audit Report that includes:
1) Executive Summary
   - Overall risk posture before/after
   - Major wins and remaining blockers
2) Inventory (per package/module + global)
   - Direct + transitive counts, notable hotspots
3) Actions Taken
   - Updated packages (from → to)
   - Replacements (old → new)
   - Removed unused deps
4) Breaking Changes & Migrations
   - What changed, what you modified, and why it’s safe
5) Security Resolution
   - Vulnerabilities found and fixed (with references)
   - Any exceptions (must include justification + mitigation)
6) Decisions & Justifications
   - Every pin/holdback and why it cannot be upgraded safely today
7) Verification
   - Commands run (build/test/lint), results, and any remaining failures

MONOREPO-AWARE MODE (IF APPLICABLE)
- Analyze dependencies per package AND globally.
- Enforce consistency (shared versions, dedupe, workspace hoisting strategy).
- Prevent drift: recommend policies (renovate/dependabot, update cadence, lockfile strategy).

SECURITY-FIRST MODE (ALWAYS ON)
- Treat unresolved vulnerabilities as build-blocking issues.
- Prefer reducing attack surface over “keeping legacy behavior.”
- If a risky dependency is unavoidable, propose layered mitigations (sandboxing, feature flags, runtime guards, SCA policies).

START NOW
Begin with discovery: list every package manager and dependency file you find, then proceed through the steps above in order.
