# PR-2: Complete Critical Stdlib Modules

## Summary
Complete the highest-value stdlib modules needed for end-to-end business modeling: cashflow, retention, and funnel.

## Base + Branch
- Base branch: `main`
- Feature branch: `feature/stdlib-cashflow-retention-funnel`

## Problem
- Stdlib coverage is incomplete for core pilot workflows.
- Missing/partial modules block realistic SaaS and marketplace models.

## Scope
### In scope
- Finish `stdlib/cashflow/`, `stdlib/retention/`, and `stdlib/funnel/` APIs and logic.
- Add/expand unit tests and conformance-style cases for these modules.
- Update stdlib docs with examples and failure modes.

### Out of scope
- Remaining stdlib modules beyond these three.
- Runtime engine internals unrelated to module behavior.

## Deliverables
- Completed module implementations and tests.
- Updated `stdlib/README.md` and per-module documentation.

## Acceptance Criteria
- `ruff` + `pytest` pass.
- Module-specific tests pass with strong coverage.
- Representative benchmark models depending on these modules execute successfully.

## Verification Commands
```bash
.venv-lint/bin/ruff check compiler/ runtime/ tests/
python -m pytest -q
python -m pytest tests/unit -k "stdlib or retention or funnel or cashflow" -q
```

## Risks & Mitigations
- Risk: formula correctness drift.
  - Mitigation: golden-value tests and explicit edge-case assertions.
- Risk: API instability.
  - Mitigation: freeze signatures and document compatibility expectations.

## Merge Gates
- Required CI checks: lint, tests, build.
- Human approval required: at least 1 maintainer review.
