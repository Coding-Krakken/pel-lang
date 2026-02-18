# PR-1: Runtime Reliability & Benchmark Success

## Summary
Fix runtime execution correctness so PEL-100 reaches >=90% success, including expression evaluation completeness, constraint enforcement, and correlated sampling support.

## Base + Branch
- Base branch: `main`
- Feature branch: `feature/runtime-reliability-v1`

## Problem
- Benchmark runtime success is far below target.
- Constraint handling and expression coverage are incomplete in runtime paths.
- Correlation handling is not production-complete.

## Scope
### In scope
- Complete runtime expression evaluator coverage for supported IR forms.
- Enforce fatal vs warning constraints consistently at runtime.
- Implement/finish correlation sampling support and validation.
- Add runtime-focused tests and benchmark gate criteria.

### Out of scope
- New language features.
- LSP/formatter/linter features.

## Deliverables
- Runtime reliability improvements in `runtime/`.
- New/expanded tests in `tests/runtime/` and benchmark checks.
- Updated docs for runtime behavior and verification commands.

## Acceptance Criteria
- `ruff` + `pytest` pass.
- PEL-100 runtime success >=90% in CI benchmark gate.
- Deterministic runs remain reproducible with fixed seed.

## Verification Commands
```bash
.venv-lint/bin/ruff check compiler/ runtime/ tests/
python -m pytest -q
python benchmarks/score_benchmark.py
```

## Risks & Mitigations
- Risk: runtime regressions in edge expressions.
  - Mitigation: targeted regression tests + conformance checks.
- Risk: performance regressions.
  - Mitigation: benchmark threshold + profiling follow-up.

## Merge Gates
- Required CI checks: lint, tests, benchmark validation, build.
- Human approval required: at least 1 maintainer review.
