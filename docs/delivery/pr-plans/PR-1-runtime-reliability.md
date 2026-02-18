# PR-1: Runtime Reliability & Benchmark Success

## PR Title
runtime: Fix expression evaluation and achieve 90%+ PEL-100 benchmark success

## One-Paragraph Summary
This PR closes the highest-risk production blocker in PEL: runtime execution reliability. It upgrades expression evaluation correctness, constraint enforcement fidelity (fatal vs warning), and correlation sampling support so benchmark outcomes become trustworthy and reproducible. The expected result is a measurable jump in PEL-100 runtime success rate to >=90%, with deterministic behavior preserved and backed by targeted regression tests and benchmark CI gating.

## Base + Branch
- Base branch: `main`
- Feature branch: `feature/runtime-reliability-v1`

## Problem Statement
- Current runtime benchmark success is materially below roadmap quality goals.
- Expression handling has gaps across complex/edge IR forms.
- Constraint behavior is inconsistently enforced during simulation loops.
- Correlation handling for stochastic runs is incomplete for production confidence.

Why now:
- This blocks end-to-end pilot trust and undermines reported model reliability.
- Runtime quality is the dependency for meaningful benchmarking and adoption.

## Scope

### In Scope
- Complete expression evaluator paths for supported IR constructs in runtime execution.
- Correct fatal/warning constraint semantics and ensure deterministic handling order.
- Implement/finish correlation sampling and matrix validation logic.
- Add runtime-focused regression tests and benchmark gating thresholds.
- Update runtime docs and verification commands.

### Out of Scope
- Any new language syntax or compiler feature additions.
- LSP/formatter/linter UX work.
- Non-runtime stdlib feature expansion.

## Deliverables
- Runtime reliability fixes in `runtime/` modules.
- New/expanded tests in `tests/runtime/` and benchmark checks in `tests/benchmarks/`.
- CI validation step for benchmark threshold.
- Documentation updates in runtime and delivery docs.

## Detailed To-Do Checklist

### Runtime Code Changes
- [x] Audit expression evaluator coverage against currently emitted IR expression variants.
- [x] Implement missing evaluator branches with explicit type-safe handling.
- [x] Add robust error paths for invalid/malformed expression nodes.
- [x] Enforce consistent constraint evaluation order per timestep.
- [x] Ensure fatal constraints fail-fast with clear trace metadata.
- [x] Ensure warning constraints record diagnostics without halting run.
- [x] Implement correlation matrix validation (shape, symmetry, positivity handling).
- [x] Integrate correlated sampling path into Monte Carlo execution flow.

### Tests
- [x] Add regression tests for newly covered expression variants.
- [x] Add runtime tests for fatal vs warning constraint behavior.
- [x] Add deterministic seed reproducibility test cases.
- [x] Add correlation sampling tests (including invalid matrix cases).
- [x] Add benchmark assertion test for >=90% target once fixes land.

### CI / Tooling
- [x] Add benchmark gate step to CI for runtime success threshold.
- [x] Keep lint and pytest gates green across supported matrix.

### Documentation
- [x] Update runtime docs with behavior clarifications.
- [x] Add troubleshooting notes for runtime constraint/correlation failures.

## Guardrails & Constraints
- No breaking changes to public CLI commands (`pel run`, `pel compile`, `pel check`).
- Preserve backward compatibility for existing valid IR structures.
- No introduction of non-deterministic behavior for fixed-seed deterministic mode.
- Avoid widening runtime API surface beyond required reliability fixes.

## Acceptance Criteria (Measurable)
- [x] `ruff` and `pytest` pass in CI and locally.
- [x] PEL-100 runtime success reaches >=90% on benchmark run.
- [x] Deterministic runs are reproducible for fixed seed.
- [x] Constraint semantics verified by explicit tests (fatal/warning behavior).
- [x] Correlation sampling path validated by tests (including error handling).
- [x] Documentation updated to reflect final behavior.

## How to Verify
```bash
.venv-lint/bin/ruff check compiler/ runtime/ tests/
python -m pytest -q
python -m pytest tests/runtime -q
python benchmarks/score_benchmark.py
```

## Risk Assessment
- Risk: hidden regressions in uncommon expression forms.
  - Mitigation: targeted regression tests + benchmark smoke on representative models.
- Risk: runtime performance degradation due to additional checks.
  - Mitigation: benchmark trend check and profile hot paths if threshold drops.
- Risk: edge-case matrix failures in correlation handling.
  - Mitigation: strict validation and clear fallback/error diagnostics.

## Parallelization Notes
- Parallel-safe with PR-2 (stdlib completion) and PR-3 (test infra) due to mostly distinct modules.
- Coordinate only on shared benchmark tests to avoid merge conflicts.

## Merge Gates
- Required CI checks: lint, tests, benchmark validation, build.
- Human approvals: at least 1 maintainer review before merge.
