# PEL Model Alignment Plan (Phase 4)

**Date:** 2026-02-13  
**Model Version:** 0.1.0  
**Status:** Active plan — implementation alignment begins in Phase 5

## 0) Scope and Inputs

### In scope
- Align the **existing implementation** to the **canonical models and contracts** produced in Phases 0–3.
- Use **incremental, low-entropy** changes (small diffs, minimal refactors) and enforce drift-prevention governance.

### Out of scope (Phase 4)
- Production code changes.
- Adding “nice-to-have” features not required by the canonical model.

### Primary inputs (source of truth)
- Baseline reality: docs/model/codebase_state_snapshot.yaml
- Canonical behavior: docs/model/system_state_model.yaml
- Delivery governance: docs/delivery/delivery_state_model.yaml

### Canonical domain models (Phase 3 outputs)
- CI/CD: ci/pipeline_model.yaml (also mirrored in docs/ci/pipeline_model.yaml)
- Contracts: contracts/api.yaml, contracts/events.yaml, contracts/errors.yaml, contracts/compiler_api.yaml
- Data model: docs/data/data_state_model.yaml
- Security: security/threat_model.yaml, security/rbac_matrix.yaml
- Resilience: resilience/failure_modes.yaml
- Ops: ops/metrics_catalog.yaml, ops/slo.yaml
- Perf: perf/budgets.yaml
- Release: release/release_strategy.yaml
- Test traceability: docs/model/test_traceability.yaml
- Roadmap model: docs/roadmap/roadmap_model.yaml

## 1) Alignment Principles

- **Model-first:** if behavior is ambiguous, update the model first, then implement.
- **Determinism is non-negotiable:** same source → same IR; same IR+seed → same results.
- **Fail-fast errors:** compiler errors are structured, actionable, and location-based.
- **Low entropy:** fix the root cause with minimal change surface; avoid broad refactors.
- **Tests before trust:** introduce tests early to prevent regressions.

## 2) Severity Rubric

- **FATAL:** violates a global invariant in docs/model/system_state_model.yaml (e.g., determinism, type safety, causality). Blocks release-quality claims.
- **MAJOR:** materially impacts correctness, portability, or governance guarantees; should be fixed before broad adoption.
- **MINOR:** gaps in advanced features or ergonomics; can be deferred.
- **DOC-ONLY:** documentation/claims drift from actual implementation.

## 3) Gap Register (Snapshot → Canonical)

| Gap ID | Area | As-is evidence (snapshot) | Canonical requirement (model) | Severity | Phase 5 WorkItem |
|---|---|---|---|---|---|
| G-001 | Lexer | Duration literal tokenization incomplete (known issue) | TOKENIZE must accept duration literals; errors must be correct and deterministic | FATAL | WI-001 |
| G-002 | Parser | Per-duration expression parsing incomplete (known issue) | PARSE must produce correct AST for rate-per-time expressions | FATAL | WI-002 |
| G-003 | Parser | Distribution named args may not parse (uncertain) | Distribution calls must parse per language spec; deterministic parsing | MAJOR | WI-003 |
| G-004 | Tests | Unit tests = 0; integration tests = 0; coverage = 0% | Validation must be enforced by tests; determinism must be tested | MAJOR | WI-004, WI-005 |
| G-005 | CI/CD | Current state: NONE | Canonical pipeline gates required (lint/type/test/coverage) | MAJOR | WI-006 (blocked by WI-004) |
| G-006 | Stdlib | 3/9 modules incomplete | Canonical stdlib growth path; functions should be pure + documented | MAJOR | WI-007..WI-009 |
| G-007 | Runtime determinism | Snapshot claims bit-identical results; no tests; RNG usage inconsistent (stdlib random listed; snapshot mentions numpy RandomState) | Runtime reproducibility invariant must hold and be verified | FATAL (if violated), otherwise MAJOR | WI-005 (adds determinism tests); may require new WorkItem |
| G-008 | Correlation | Correlation sampling not implemented | Monte Carlo mode should respect correlation when specified | MINOR (advanced) | (future WorkItem) |
| G-009 | Observability | Metrics/tracing not implemented; logging ad-hoc | Events/metrics must be optional and non-semantic | MINOR | (future WorkItem) |
| G-010 | Security sandbox | Snapshot lists sandbox controls as planned/partial; enforcement unclear | Security invariants (no dynamic code, bounded resources) must be enforced and tested | MAJOR | (future WorkItem) |
| G-011 | Error contract | Error contract model exists; code conformance not verified | Structured errors must conform to contracts/errors.yaml | MAJOR | (future WorkItem) |
| G-012 | Documentation claims | README describes extensive tooling/dirs not present in repo tree; snapshot says alpha + missing CI/tests | Documentation must reflect implementation reality | DOC-ONLY | (doc WorkItem) |

## 4) Recommended Phase 5 Execution Order (Critical Path)

1. **WI-001** (lexer duration literals) → unblocks WI-002.
2. **WI-002** (per-duration parsing) → enables example compilation paths.
3. **WI-003** (distribution named args) → remove syntax uncertainty.
4. **WI-004** (unit test infrastructure) → establish baseline coverage and regression prevention.
5. **WI-005** (integration + determinism tests) → validate global invariants.
6. **WI-006** (CI/CD) → enforce drift prevention.
7. **WI-007..WI-009** (stdlib modules) → expand functionality after core correctness gates.

## 5) WorkItem Acceptance Criteria Augments (Model-derived)

These are *additions* to the WorkItems in docs/delivery/delivery_state_model.yaml to ensure they fully prove canonical invariants:

- **WI-001 / WI-002**
  - Add at least one test that compiles a minimal model containing `$500/1mo` and verifies:
    - compilation succeeds
    - IR is stable across two runs

- **WI-005 (Determinism verification)**
  - In deterministic mode: run twice, compare full result JSON (exact match).
  - In monte_carlo mode: run twice with same seed, compare summary outputs (exact match) and a fixed set of samples if exposed.

- **WI-006 (CI gates)**
  - Treat coverage threshold as a hard gate once tests exist; until then, CI should at least run lint/type/tests.

## 6) Open Decisions (Must be resolved before claiming full conformance)

- **Runtime RNG source of truth:** choose and document whether runtime uses `random` (stdlib) or `numpy` and pin behavior to guarantee reproducibility.
- **Bit-identical floats across platforms:** the canonical model currently states “bit-identical including floats.” If this is not realistically achievable across CPU/BLAS variations, update the canonical model to clarify scope (same platform + pinned deps) before implementation.

## 7) Phase 4 Exit Criteria

Phase 4 is complete when:
- This plan exists (docs/model/model_alignment_plan.md).
- The gap register is enumerated and mapped to WorkItems.
- Any newly discovered gaps during Phase 5 are appended here first (model-first governance).
