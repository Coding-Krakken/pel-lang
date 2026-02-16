---
name: implement
description: Implement code changes with strict adherence to the Universal Model-First Copilot Implementation Directive, ensuring deterministic behavior, minimal entropy, and maximal maintainability across the entire codebase and delivery lifecycle.
agent: agent
---

================================================================================
UNIVERSAL MODEL-FIRST COPILOT IMPLEMENTATION DIRECTIVE (FULL MODEL GOVERNANCE)
(Deterministic, Entropy-Resistant, Multi-Model Enforcement)
================================================================================

PURPOSE:
This directive governs ALL implementation activities in the repository.

It may be invoked with:
- PR number
- Issue number
- Natural language request
- Feature idea
- Refactor request
- Bug report
- OR no arguments

Regardless of input, you MUST begin with model evaluation.

No code before models.
No prose before structure.
No drift between models and code.

================================================================================
GLOBAL PRINCIPLE
================================================================================

Every domain in the codebase has a canonical model.

Code must mirror models.
Tests must trace to models.
Docs must derive from models.
Delivery must be governed by models.
Roadmap must be governed by models.

You are probabilistic.
You must behave deterministically.

================================================================================
PHASE -1 — META-REASONING & INVOCATION CLASSIFICATION
================================================================================

1. Identify invocation type.
2. Restate mission formally.
3. Classify domain.
4. Assess risk.
5. Set proportional rigor.
6. Declare complexity and entropy budget.

Reject unnecessary abstraction.
Reject unnecessary refactor.
Justify minimal sufficient scope.

================================================================================
PHASE 0 — LOAD ALL CANONICAL MODELS
================================================================================

You must locate and validate:

1) Copilot Instruction Model:
   .system-state/copilot/instruction.model.yaml

2) System State Model:
   .system-state/model/system_state_model.yaml

3) Delivery State Model:
   .system-state/delivery/delivery_state_model.yaml

4) Contracts Model:
   .system-state/contracts/api.yaml
   .system-state/contracts/events.yaml
   .system-state/contracts/errors.yaml

5) Data Model:
   .system-state/data/data_state_model.yaml

6) Security Model:
   .system-state/security/threat_model.yaml
   .system-state/security/rbac_matrix.yaml

7) Failure & Resilience Model:
   .system-state/resilience/failure_modes.yaml

8) Observability Model:
   .system-state/ops/metrics_catalog.yaml
   .system-state/ops/slo.yaml

9) Test Traceability Model:
   .system-state/model/test_traceability.yaml

10) Performance Model:
   .system-state/perf/budgets.yaml

11) Dependency Governance Model:
   .system-state/deps/dependency_policy.yaml

12) CI/CD & Environment Model:
   .system-state/ci/pipeline_model.yaml
   .system-state/release/release_strategy.yaml

13) Roadmap & Prioritization Model:
   .system-state/roadmap/roadmap_model.yaml

If any model is missing for the affected scope:
- Create or minimally update it before proceeding.

No implementation without model alignment.

================================================================================
PHASE 1 — REVERSE-MODEL CURRENT CODEBASE STATE
================================================================================

Create:

.system-state/model/codebase_state_snapshot.yaml

Must include:

- Current ontology
- Current state variables
- Current transitions
- Current invariants enforced
- Current IO contracts
- Current persistence schema
- Current security enforcement
- Current failure handling
- Current observability hooks
- Current performance assumptions
- Current dependency usage
- Current CI/CD enforcement

This snapshot must reflect actual repository reality.

================================================================================
PHASE 2 — MODEL DIFFERENTIAL ANALYSIS
================================================================================

Create:

.system-state/model/model_codebase_diff.md

You must compute diffs between:

- system_state_model vs codebase
- contracts model vs endpoints
- data model vs DB schema
- security model vs enforcement points
- failure model vs implemented retries/timeouts
- observability model vs metrics/logging
- performance model vs hot paths
- dependency model vs package manifests
- CI model vs pipeline config
- delivery model vs actual work progress

Categorize diffs:

- Fatal
- Major
- Minor
- Documentation-only

If fatal gaps exist → STOP and clarify.

Minimize diff surface.
Prefer smallest alignment change first.

================================================================================
PHASE 3 — DELIVERY STATE UPDATE
================================================================================

Update:

.system-state/delivery/delivery_state_model.yaml

You must:

- Create or activate a WorkItem
- Assign complexity and entropy budget
- Define scope boundary
- Define required artifacts
- Define acceptance criteria
- Link affected models
- Define rollback requirements
- Define migration requirements (if any)

No transition to "Implementing" without:
- Model alignment
- Validation complete
- Plan complete

================================================================================
PHASE 4 — VALIDATION & STRESS ANALYSIS
================================================================================

Create:

.system-state/model/implementation_validation_report.md

Must include:

- Hidden state detection
- Undefined transitions
- Invariant enforcement gaps
- Security threat delta
- Failure mode coverage delta
- Performance impact forecast
- Entropy expansion risk
- Rollback feasibility
- Dependency risk
- CI/CD gate impact

If entropy or complexity exceeds budget → simplify.

================================================================================
PHASE 5 — IMPLEMENTATION PLAN
================================================================================

Create:

.system-state/plan/implementation_plan.md

Must include:

- Minimal diff boundary
- File-by-file changes
- Transition-by-transition mapping
- Invariant-by-invariant enforcement mapping
- Data migration steps
- Rollback strategy
- Dependency additions (justified)
- CI/CD modifications (if required)
- Model updates required
- Determinism enforcement checklist

You must explicitly declare:
"No unrelated code will be modified."

================================================================================
PHASE 6 — IMPLEMENTATION (CODE)
================================================================================

Now implement.

Strict rules:

- Enforce invariants.
- Enforce transitions.
- Enforce security.
- Enforce concurrency model.
- Implement failure behavior exactly as modeled.
- Respect performance budgets.
- Respect dependency policy.
- Respect CI/CD constraints.
- Do not rename unrelated symbols.
- Do not refactor outside scope boundary.
- Do not introduce speculative abstractions.
- Produce stable, deterministic code.

Choose ONE canonical implementation path.

================================================================================
PHASE 7 — TEST & TRACEABILITY UPDATE
================================================================================

Update:

- .system-state/model/test_traceability.yaml

Add tests for:

- Invariants
- Transitions
- Security rules
- Failure modes
- Performance expectations
- Determinism (where applicable)

Tests must trace directly to model elements.

================================================================================
PHASE 8 — POST-IMPLEMENTATION ALIGNMENT
================================================================================

Create:

.system-state/model/post_implementation_alignment_report.md

Must confirm:

- All affected models updated
- Code mirrors system model
- Contracts align
- Data schema aligns
- Security aligns
- Failure model aligns
- Observability aligns
- Performance budgets respected
- Delivery model updated
- Roadmap model updated if priority changed

No drift allowed.

================================================================================
PHASE 9 — ROADMAP EVALUATION (NO-ARG OR COMPLETED TASK)
================================================================================

If no argument was provided OR task is complete:

1. Evaluate:
   - Remaining model-code diffs
   - Test gaps
   - Security hardening gaps
   - Observability gaps
   - Performance risks
   - Dependency risks
   - CI/CD fragility
   - Entropy reduction opportunities

2. Use roadmap_model.yaml scoring to select next highest-leverage task.

3. Create next WorkItem in delivery_state_model.yaml.

================================================================================
FINAL SELF-AUDIT
================================================================================

Before completion:

- Did I begin with model evaluation?
- Did I align all models?
- Did I minimize diff?
- Did I stay within entropy budget?
- Did I update delivery model?
- Did I update roadmap model?
- Did I preserve determinism?
- Did I enforce rollback?
- Do tests trace to models?
- Do CI gates pass?

If any answer is no → fix before completion.

================================================================================
OUTPUT ORDER (STRICT)
================================================================================

1) Model loading confirmation
2) Codebase state snapshot
3) Model diff analysis
4) Delivery state update
5) Validation report
6) Implementation plan
7) Code changes
8) Tests + traceability update
9) Post-implementation alignment report
10) Roadmap update (if applicable)

================================================================================
END IMPLEMENTATION DIRECTIVE
================================================================================
