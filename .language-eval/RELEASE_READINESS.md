# Release Readiness Checklist

This document outlines required readiness criteria before using Language Evaluation Framework results for production release decisions.

## ⚠️ Critical Warning

**The current framework includes scaffold-level placeholder suite implementations.**

Do NOT rely on framework scores for release gating until suites are validated against real workloads and project-specific baselines are established. See "Production Readiness Tracks" below.

## Framework Maturity

### Phase 1: Framework Architecture ✅ COMPLETE
- [x] Metric taxonomy defined (13 categories)
- [x] Scoring rubric published (0-5 scale)
- [x] Weight profiles established (5 roles)
- [x] Schema validation implemented
- [x] CI gating logic implemented
- [x] Test coverage comprehensive

### Phase 2: Suite Implementations 🚧 IN PROGRESS

Each suite must complete the checklist below before results can inform release decisions:

#### Conformance Suite

**Readiness Criteria:**

- [ ] Test fixtures sourced from language specification (not just PEL implementation)
- [ ] Tests cover:
  - [ ] Parser correctness (positive + negative cases)
  - [ ] Type checker diagnostics (error location, message accuracy)
  - [ ] Runtime semantics (reference behavior matching)
  - [ ] Edge cases and error handling
- [ ] Pass rate baseline established with reference implementation
- [ ] Expected failures documented with expiry dates
- [ ] CI execution completes in < 10 minutes
- [ ] Pass rate >= 95% for production-ready target

**Status:** Scaffold - implementing hardcoded 0.976 pass rate

**Next Steps:**
1. Migrate conformance tests from project test suite to `.language-eval/suites/conformance/tests/`
2. Source additional fixtures from language spec ISO/IEC standard or equivalent
3. Run baseline pass rate collection on reference implementation
4. Document any intentional deviations in expected_failures.yaml

---

#### Security Suite

**Readiness Criteria:**

- [ ] Supply chain policy checks implemented:
  - [ ] Lockfile presence validation
  - [ ] Direct dependency version pinning verification
  - [ ] High-risk dependency tracking
  - [ ] Reproducible build path validation
- [ ] Unsafe feature inventory operational
- [ ] SAST/dependency scanner integrated (optional but recommended)
- [ ] Policy pass rate baseline established
- [ ] All findings documented with severity/remediation plan
- [ ] CI execution completes in < 5 minutes

**Status:** Scaffold - implementing hardcoded 0.95 policy_pass_rate

**Next Steps:**
1. Integrate project's SAST tooling (if available): Semgrep, CodeQL, etc.
2. Set up dependency scanning: Dependabot, Snyk, or OSSIndex
3. Document supply chain assumptions specific to target language ecosystem
4. Establish baseline with current implementation

---

#### Performance Suite

**Readiness Criteria:**

- [ ] Micro workloads defined and validated:
  - [ ] Arithmetic operations benchmarks
  - [ ] Parser tokenization paths
  - [ ] Core runtime ops
  - [ ] Measured on stable hardware with>=3 runs averaged
- [ ] Macro workloads defined and validated:
  - [ ] HTTP-like request handling
  - [ ] JSON encode/decode pipelines
  - [ ] DB-like read/write simulations
- [ ] Real-world workloads integrated:
  - [ ] Sample application compile/build
  - [ ] End-to-end scenario execution
- [ ] Baseline performance established with known configuration
- [ ] Performance degradation thresholds agreed (e.g., ±5%)
- [ ] CI execution completes in < 30 minutes
- [ ] Latency p95 < 200ms for typical web backend workload
- [ ] Memory footprint < 1GB for typical scenario

**Status:** Scaffold - implementing hardcoded latency/throughput/memory metrics

**Next Steps:**
1. Define reference workloads with published specifications
2. Set up performance measurement harness with:
   - Warmup phase (configurable via --warmup flag)
   - Multiple iterations (configurable via --repeat flag)
   - Percentile calculation (p50/p95/p99)
   - Memory tracking (RSS, peak allocation)
3. Run baseline across reference hardware platforms
4. Document environmental dependencies (CPU model, clock speed, memory, etc.)
5. Establish allowed variance window for CI

---

#### Tooling Suite

**Readiness Criteria:**

- [ ] Formatter idempotence validation:
  - [ ] Automated test: format → format → byte-identical comparison
  - [ ] Real source corpus (>1000 files tested)
  - [ ] Pass rate = 100%
- [ ] LSP integration tested:
  - [ ] Completion latency measured (p95 < 200ms target)
  - [ ] Correctness spot-checks on common symbols
  - [ ] Diagnostics accuracy verified
- [ ] Linter sanity checks:
  - [ ] False positive rate measured on reference corpus
  - [ ] Common patterns validated (unused variables, type mismatches)
- [ ] CI execution completes in < 5 minutes

**Status:** Scaffold - implementing hardcoded idempotence/LSP/linter metrics

**Next Steps:**
1. Wire formatter executable to run twice over test corpus
2. Measure LSP latency via HTTP/JSON-RPC client calls
3. Sample linter output against golden files
4. Establish baselines for each metric
5. Document tool version requirements

---

#### Human Factors Suite

**Readiness Criteria:**

- [ ] Study protocol defined (documented reproducibly)
- [ ] Participant profile established (e.g., "experienced Python developers, first time with PEL")
- [ ] Tasks defined with success criteria:
  - [ ] Task 1: Hello World program
  - [ ] Task 2: Simple data transformation
  - [ ] Task 3: Debugging a common error
  - [ ] Task 4: Refactoring exercise
- [ ] Metrics collected:
  - [ ] Time-to-completion per task
  - [ ] Error count / blockers encountered
  - [ ] Subjective difficulty rating
- [ ] Baseline study completed with >=5 participants
- [ ] Results documented with:
  - [ ] Participant background summary
  - [ ] Raw metrics and variance
  - [ ] Observations about common friction points
- [ ] Checklist coverage >= 80%

**Status:** Scaffold - implementing hardcoded checklist_coverage metric

**Next Steps:**
1. Define study protocol in `.language-eval/suites/human_factors/protocol.md`
2. Create task scripts/materials in `.language-eval/suites/human_factors/tasks/`
3. Run pilot study with internal team
4. Document findings and pain points
5. Establish baseline checklist coverage

---

## Baseline Establishment Process

Before using framework scores for release decisions:

1. **Run Full Suite on Reference Implementation**
   ```bash
   ./.language-eval/scripts/run_all.sh \
     --target .language-eval/targets/example-target.yaml
   ```

2. **Review Results**
   - Check all artifacts present (results.raw.json, results.normalized.json, scorecard.json, report.json)
   - Verify suite scores are realistic (not all 5.0)
   - Validate determinism (hash matches across runs)

3. **Document Baseline**
   - Copy scorecard.json to `baselines/baseline.<version>.json`
   - Add environment fingerprint (OS, arch, Python version, timestamps)
   - Document any deviations from ideal in metadata

4. **Approve for Governance**
   - Get maintainer sign-off on baseline reasonableness
   - Record decision and date in changelog

5. **Set Regression Threshold**
   - Calculate acceptable tolerance based on:
     - Suite variability (measure std dev across 10 runs)
     - Known platform variance
     - Release criticality
   - Typical: 5% tolerance for web backends, 2% for systems code

## Release Decision Gate

Do NOT use framework scores for release gating until:

```
✅ All 5 suites fully implemented (non-placeholder)
✅ Each suite has >1000 test cases or >1 hour of measurement data
✅ Baseline established on reference implementation
✅ Regression tolerance calibrated
✅ Expected failures policy in place with expiry enforcement
✅ Governance review completed and signed off
✅ Team training documentation created
```

When all criteria met, framework scores can inform (but not solely determine) release decisions.

## Ongoing Maintenance

### Quarterly Review

- [ ] Review expired expected failures
- [ ] Recalibrate performance baselines if major environmental changes
- [ ] Check ecosystem health indicators for target
- [ ] Update weight profiles if domain priorities shift

### Annual Review

- [ ] Comprehensive baseline recalibration
- [ ] Metric formula sensitivity analysis
- [ ] Survey user feedback on metric relevance
- [ ] Update RELEASE_READINESS.md based on lessons learned

## Questions & Escalation

**Q: Can we use framework scores now?**

A: Framework is excellent for development/CI gating to prevent major regressions. Production release decisions require completion of Phase 2. Use scores as *one input* among code review, integration testing, and domain expertise until Phase 2 complete.

**Q: Which suite is highest priority to implement first?**

A: **Conformance** (correctness) — it's upstream of reliability scoring and establishes baseline trustworthiness.

**Q: How do we know baselines are correct?**

A: Establish baselines by:
1. Running on known-good reference implementation
2. Comparing results against published benchmarks (academic papers, competitor reports)
3. Soliciting domain expert review of metrics

**Q: What if scores regress significantly?**

A: Before gating the release:
1. Re-run suite multiple times to verify determinism
2. Check if baseline/threshold was miscalibrated
3. Investigate root cause (code change, environment variance, suite bug)
4. Update expected_failures.yaml if intentional tradeoff
5. Recalibrate threshold if needed (with governance approval)

---

## Version History

| Version | Date | Phase | Status |
|---------|------|-------|--------|
| 0.1.0 | 2026-02-19 | Phase 1 | ✅ Framework complete |
| 0.2.0 | 2026-06-30 | Phase 2 | 🚧 Target: Conformance suite 100% |
| 1.0.0 | 2026-12-31 | Phase 2 | 🎯 Target: All suites production-ready |
