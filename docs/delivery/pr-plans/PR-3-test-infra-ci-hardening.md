# PR-3: Test Infrastructure & CI Hardening

## Summary
Raise quality confidence with broader automated tests, coverage enforcement, and stricter CI quality gates.

## Base + Branch
- Base branch: `main`
- Feature branch: `feature/test-infrastructure-v1`

## Problem
- Current tests and CI gates are not sufficient for rapid, safe parallel delivery.
- Regressions can slip through without stronger coverage and policy checks.

## Scope
### In scope
- Expand unit/integration/conformance tests in `tests/`.
- Add/strengthen CI gating for coverage and critical checks.
- Improve test documentation and contributor guidance.

### Out of scope
- New language/runtime features unrelated to testing infrastructure.
- Product UX/tooling features outside CI/testing.

## Deliverables
- New and expanded tests across critical paths.
- CI workflow updates in `.github/workflows/` for stricter quality gating.
- Documentation updates in testing guidance docs.

## Acceptance Criteria
- `ruff` + `pytest` pass.
- Coverage threshold enforced in CI.
- CI checks required for merge reflect hardened policy.

## Verification Commands
```bash
.venv-lint/bin/ruff check compiler/ runtime/ tests/
python -m pytest -q
python -m pytest tests/conformance -q
```

## Risks & Mitigations
- Risk: slower CI turnaround.
  - Mitigation: optimize matrix and split fast/slow jobs.
- Risk: flaky tests.
  - Mitigation: isolate nondeterminism and pin seeds/time-sensitive assertions.

## Merge Gates
- Required CI checks: lint, tests, security scan, build.
- Human approval required: at least 1 maintainer review.
