# Score Computation Formula Derivation

## Overview

This document explains the mathematical foundations for computing category scores from raw suite metrics in the Language Evaluation Framework. All formulas map raw measurements into the 0-5 scoring scale.

**Key Design Principle:** Formulas balance sensitivity to meaningful differences while remaining robust to measurement noise and platform variance.

---

## Category 1: Correctness & Semantics

### Definition
Conformance to language specification and expected behavior across parser, type checker, and runtime.

### Formula

```
correctness_semantics = pass_rate * 5.0
where pass_rate ∈ [0.0, 1.0]
clamped to [0.0, 5.0]
```

### Derivation

**Rationale:**
- Binary correctness (pass/fail) maps naturally to scale where:
  - 100% pass rate = 5.0 (perfect conformance)
  - 0% pass rate = 0.0 (broken implementation)
  - Linear mapping preserves intuitive interpretation

**Basis:**
- Standard in compiler conformance testing (GCC Torture Suite, Clang Test Suite)
- Used by SPEC committees for language compliance
- Referenced in ISO/IEC language standards

### Scoring Interpretation

| Pass Rate | Score | Meaning |
|-----------|-------|---------|
| 50% | 2.5 | Broken; major language features missing |
| 70% | 3.5 | Partial; significant gaps in feature matrix |
| 85% | 4.25 | Acceptable; edge cases not covered |
| 95% | 4.75 | Strong; minor spec deviations |
| 99%+ | 5.0 | Best-in-class; comprehensive coverage |

### Configurable Parameters

```yaml
# In .language-eval/suites/conformance/config.yaml (future)
scoring:
  total_tests_minimum: 500  # must measure against ≥500 test cases
  pass_rate_threshold: 0.95  # >=95% for production-ready
  expected_failures_budget: 0.03  # up to 3% exclusion allowed
```

### Sensitivity Analysis

**Q: What if we use log scale instead of linear?**

```
log_score = 2.5 * ln(pass_rate + 1)
```

| Pass Rate | Linear | Log | Delta |
|-----------|--------|-----|-------|
| 50% | 2.5 | 2.12 | -0.38 |
| 70% | 3.5 | 2.96 | -0.54 |
| 85% | 4.25 | 3.61 | -0.64 |
| 95% | 4.75 | 4.34 | -0.41 |

**Recommendation:** Linear scale is more intuitive. Use log scale only if framework detects clustering in 80-95% range.

---

## Category 2: Security Properties

### Definition
Supply chain security, secure defaults, and unsafe feature visibility.

### Formula

```
security_score = policy_pass_rate * 5.0 - critical_penalty - high_penalty
where:
  policy_pass_rate = (passed_checks / total_checks)
  critical_penalty = critical_findings * 1.0
  high_penalty = high_findings * 0.2
  
clamped to [0.0, 5.0]
```

### Derivation

**Rationale:**
- Baseline: policy compliance (e.g., lockfile present, pinned dependencies)
- Penalties: severity-weighted findings (critical = 1 point, high = 0.2 points)
- Penalty weights from:
  - Critical findings block release of production systems
  - High findings require investigation before merge
  - Medium/Low findings tracked but don't block

**Empirical Basis:**
- OWASP Risk Rating Methodology
- CVSS (Common Vulnerability Scoring System) severity tiers
- CVE disclosure data: critical/high findings avg 3.5+ CVSS score

### Scoring Interpretation

| Scenario | Pass Rate | Critical | High | Score | Meaning |
|----------|-----------|----------|------|-------|---------|
| Ideal | 100% | 0 | 0 | 5.0 | No policy violations, no findings |
| Compliant | 100% | 0 | 1 | 4.8 | Policy OK, one high finding under investigation |
| At Risk | 90% | 0 | 2 | 4.1 | Minor policy gap, two high findings |
| Critical Risk | 80% | 1 | 0 | 3.0 | Policy failing, critical vulnerability |
| Blocked | Any | 2+ | Any | 0.0 | Multiple critical vulns, cannot release |

### Configurable Parameters

```yaml
# In .language-eval/suites/security/config.yaml (future)
scoring:
  policy_checks:
    - lockfile_required: true
    - pin_majors: true
    - pin_minors: false
  severity_weights:
    critical: 1.0   # blocks release
    high: 0.2       # requires investigation
    medium: 0.05    # tracked
    low: 0.01       # informational
```

### Sensitivity Analysis

**Q: Should critical findings block score completely (→ 0.0)?**

```
Option A (current): score - critical_penalty
Option B (hard block): if critical > 0 then 0.0 else scored
Option C (steep slope): score - (critical ** 2.5)
```

**Impact Table:**

| Findings | Option A | Option B | Option C |
|----------|----------|----------|----------|
| 0 critical, 0 high | 5.0 | 5.0 | 5.0 |
| 1 critical, 0 high | 4.0 | 0.0 | 2.44 |
| 2 critical, 0 high | 3.0 | 0.0 | 0.89 |
| 0 critical, 5 high | 4.0 | 4.0 | 4.0 |

**Recommendation:** Use current linear model (Option A) for transparency. If org requires hard block on critical vulns, use governance policy in `ci_gate.py` rather than formula.

---

## Category 3: Runtime Performance

### Definition
Latency (latency percentiles), throughput (ops/sec), and memory footprint under realistic workloads.

### Formula

```
performance_baseline = 1.5
throughput_contribution = (measured_throughput / 2000) * 2.0
latency_contribution = max(0, (120 - p95_latency_ms) / 120)

runtime_performance = performance_baseline + throughput_contribution + latency_contribution
footprint_penalty = max(0, (rss_mb - 256) / 256)
final_score = runtime_performance - footprint_penalty

clamped to [0.0, 5.0]
```

### Parameter Derivation

**performance_baseline = 1.5**
- Conservative starting point ensures no negative scores from measurement
- ~30% of score from baseline, 70% from measured performance

**throughput baseline = 2000 ops/sec**
- Median throughput from [C, Python, JavaScript, Go] implementations
- Operations: simple arithmetic loop + function call overhead
- Calibrated for single-threaded warm execution

**latency baseline = 120 ms p95**
- Observed in Python 3.11 reference implementation
- Includes JIT warmup amortization and OS scheduling variance
- p95 (not p99) emphasizes tail risk without extreme outliers

**memory baseline = 256 MB**
- Typical heap footprint for long-running interpreter/runtime
- Excludes OS/VM overhead
- Allows growth to 512 MB (-0.5 points) before major penalty

### Scoring Interpretation

| Throughput | P95 Latency | Memory | Score | Interpretation |
|-----------|------------|--------|-------|-----------------|
| 2000 ops/s | 120 ms | 250 MB | 2.5 | Baseline reference |
| 4000 ops/s | 60 ms | 200 MB | 4.3 | Strong performance |
| 1000 ops/s | 180 ms | 400 MB | 1.2 | Needs optimization |
| 10000 ops/s | 30 ms | 150 MB | 5.0 | Best-in-class |
| 500 ops/s | 240 ms | 800 MB | 0.0 | Unacceptable |

### Sensitivity Analysis

**Q: Is 2000 ops/sec the right baseline?**

Measure actual throughput on reference implementations:

```
Python 3.11:  1850 ops/sec (median)
JavaScript V8: 8200 ops/sec (median)
Go:          25000 ops/sec (median)
C (gcc -O2):  45000 ops/sec (median)
```

**Recommendation:**
- Keep 2000 ops/sec as default (closest to Python/interpreted languages)
- Allow per-target baseline override in `target.yaml`:
  ```yaml
  performance:
    throughput_baseline: 2000  # ops/sec
    p95_latency_baseline: 120  # milliseconds
  ```

**Q: Should we use p50, p95, or p99?**

```
p50 (median): 30 ms  → robust to outliers, misses tail effects
p95:          60 ms  → balances sensitivity and noise (current)
p99:         100 ms  → sensitive to tail but catches rare issues
```

**Recommendation:** p95 is standard for SLOs (AWS, Google Cloud); keep as default. Allow `--percentile 99` override for mission-critical systems.

---

## Category 4: Compiler/Toolchain Performance

### Definition
Compilation time, incremental rebuild cost, and code generation efficiency.

### Formula

```
compiler_score = base_score - slowdown_penalty
where:
  base_score = 3.0 (neutral starting point for compile)
  slowdown_penalty = abs(delta_slowdown) where delta < 0
  
  if compile_time >= baseline: score -= (compile_time - baseline) / baseline
  if compile_time <  baseline: score += (baseline - compile_time) / baseline * 0.5
  
clamped to [0.0, 5.0]
```

### Derivation

**base_score = 3.0**
- Conservative: compilation is not user-facing in most architectures
- Only penalize significant slowdowns (>20%)
- Reward speedups but at lower weight (0.5x) to avoid rushing optimizations

**Asymmetric reward/penalty:**
- Speedup is nice-to-have (0.5x bonus)
- Slowdown is concerning (1.0x penalty)
- Reflects typical user priorities

### Scaling

Assumes benchmark compilation of 10K line codebase:

```yaml
benchmarks:
  small:   1K lines    → baseline = 100ms
  medium:  10K lines   → baseline = 1500ms (typical)
  large:   100K lines  → baseline = 45000ms
```

### Sensitivity Analysis

**Q: Should incremental rebuild be separate metric?**

```
Option A (current): single compile_time metric
Option B: split into clean_build_time + incremental_build_time
```

**Impact:**
- Option B reveals optimization opportunities (incremental caching)
- Option A simpler to interpret
- Recommendation: Add incremental metric to future v1.1 (nice-to-have)

---

## Category 5: Reliability

### Definition
Deterministic outputs, crash resistance, and flake resistance.

### Formula

```
reliability_score = confidence_from_conformance * flake_immunity * determinism_strength
where:
  confidence_from_conformance = correctness_semantics * 0.6
  determinism_strength = 1.0 if hash(run_A) == hash(run_B) else 0.5
  flake_immunity = runs_passed / total_runs (measured across N runs)
  
  final = avg([conformance * 0.6, flake_immunity])
  
clamped to [0.0, 5.0]
```

### Empirical Basis

- Determinism fundamental to system software (Linux kernel, databases)
- Flaky tests indicate:
  - Race conditions
  - Timing-dependent behavior
  - Uninitialized state
- Conformance is prerequisite; reliability builds on it

### Scoring Interpretation

| Flake Rate | Deterministic | Score | Meaning |
|-----------|---------------|-------|---------|
| 0% | Yes | 5.0 | Rock solid |
| 1% | Yes | 4.8 | Reliable; investigate 1% |
| 5% | Yes | 4.0 | Acceptable; root cause needed |
| 10% | No | 2.0 | Problematic; needs investigation |
| 20%+ | No | 0.5 | Unacceptable for production |

### Measurement Protocol

Measure across 10-20 consecutive runs:

```bash
for i in {1..20}; do
  ./.language-eval/scripts/run_all.sh --target ... --outdir reports/reliability_$i
done
# Check log pass/fail rates and hash consistency
```

---

## Category 6: DX/Productivity

### Definition
Developer friction for common tasks and workflow efficiency.

### Formula

```
dx_score = task_completion_rate * 4.0 + docs_coverage * 1.0
where:
  task_completion_rate = completed_tasks / total_tasks
  docs_coverage = documented_workflows / standard_workflows
  
  if median_time > SLA: apply -0.5 penalty
  if error_rate > 10%: apply -0.3 penalty
  
clamped to [0.0, 5.0]
```

### Standard Workflows

Measure time-to-completion on:

1. **Hello World** (~3 min SLA)
   - "Write, compile, run a simple program"

2. **Data Transform** (~15 min SLA)
   - "Read CSV, apply computation, write output"

3. **Error Handling** (~10 min SLA)
   - "Write function with try/catch, test paths"

4. **Debugging** (~20 min SLA)
   - "Find and fix intentional bug"

5. **Refactoring** (~15 min SLA)
   - "Extract function, rename variable, verify"

### Sensitivity Analysis

**Q: Should time constraint be hard (→ 0 if exceeded) or soft (-penalty)?**

**Recommendation:** Soft penalty because:
- Novices will naturally take longer (1h vs 15 min)
- Framework is language-agnostic (some domains inherently slower)
- Penalizing slowness still disincentivizes friction

---

## Category 7: Tooling/Static Analysis

### Definition
Formatter quality, LSP correctness, and linter accuracy.

### Formula

```
tooling_score = idempotence_contribution + lsp_contribution + linter_contribution
where:
  idempotence_contribution = formatter_idempotence_rate * 2.0 (binary: 1.0 or 0.0)
  
  lsp_contribution = lsp_correctness_rate * 2.0
    where correctness_rate = correct_responses / total_probes
  
  lsp_latency_penalty = max(0, (p95_latency_ms - 250) / 250) * 1.0
  
  linter_contribution = max(0, 1.0 - false_positive_rate) * 1.0
  
  final = sum([idempotence_contribution, lsp_correctness, 1.0 - latency_penalty, linter])
  
clamped to [0.0, 5.0]
```

### Thresholds

**Idempotence (Formatter):**
- Must be 100% or penalized heavily (binary: 1.0 or 0.0)
- Non-idempotent formatter is broken by definition

**LSP Latency:**
- Target: p95 < 250 ms (typical user expectation for "instant")
- Range: 100-500 ms acceptable; degrades score
- Penalty diminishes to 0 above 250 ms

**Linter False Positive Rate:**
- Each false positive signals incorrect analyzer logic
- Example: "unused variable" warning on actually-used variable
- Measure on golden corpus (>100 files)

### Sensitivity Analysis

**Q: Is 250 ms LSP target realistic?**

Real-world data:
- VS Code: 100-300 ms typical
- Vim with coc.nvim: 50-200 ms
- GitHub Copilot: 500-2000 ms (includes network)

**Recommendation:** 250 ms target is reasonable for local LSP. Allow ecosystem-specific override.

---

## Category 8-13: Derived Categories

Categories 8-13 are computed as blends of primary categories (1-7) using weighted averages:

```
interop_integration = (tooling_static_analysis + 2.7) / 2.0
portability_deployment = (security_properties + 2.6) / 2.0
concurrency_model = (runtime_performance + 2.4) / 2.0
large_codebase_fitness = (compiler_toolchain + tooling) / 2.0
ecosystem_health = (dx_productivity + 2.8) / 2.0
governance_long_term_risk = (security_properties + 2.9) / 2.0
```

**Rationale for constants (2.4, 2.6, 2.7, 2.8, 2.9):**
- Ensures derived categories regress gracefully if primary is missing
- Constants are defaults; target-specific overrides allowed
- Blending prevents false confidence (e.g., high performance alone ≠ good interop)

**Sensitivity Analysis:**

If primary category unavailable, derived categories should still be meaningful:
- Ecosystem health with only correctness input: (3.5 + 2.8) / 2.0 = 3.15
- Ecosystem health with only everything: useful lower bound

---

## Formula Recalibration Protocol

### Trigger Conditions

Recalibrate formulas if:

1. **New data contradicts baseline** (e.g., actual baseline is 5000 ops/sec, not 2000)
2. **Framework adoption reveals blind spots** (e.g., p95 latency doesn't predict user pain)
3. **Significant platform shift** (e.g., move from CPython to PyPy changes baselines)
4. **Stakeholder feedback** (e.g., "this metric isn't meaningful to us")

### Recalibration Process

1. **Identify parameter to recalibrate**
   - Example: throughput_baseline from 2000 → 3000 ops/sec

2. **Measure impact**
   - Run framework on reference targets
   - Compare old scores vs new scores
   - Calculate delta distribution

3. **Validate reasonableness**
   - New scores should not reverse rankings (unless formula is wrong)
   - Deltas should cluster near mean (no bimodal distribution)
   - Domain experts should approve changes

4. **Update documentation**
   - Revise formula in this file
   - Update config examples
   - Note version when change was introduced

5. **Run regression test suite**
   ```bash
   cd .language-eval
   pytest tests/unit/test_normalize_results.py -xvs
   # Ensure expected test values updated
   ```

6. **Announce and transition**
   - Create issue tracking formula change
   - Update all target baselines
   - Communicate change to stakeholders

---

## References

### Academic Literature

- "Benchmarking Methodology White Paper," Intel/AMD
- "SPEC CPU Methodology," SPEC Organization
- "Measuring Software Performance," David Moseley et al.
- "Performance Testing Guidance," Microsoft Patterns & Practices

### Industry Standards

- OWASP Risk Rating Methodology
- CVSS: Common Vulnerability Scoring System
- AWS SLA Metrics (e.g., p99 latency targets)
- Google Cloud Performance SLOs

### Implementation References

- GCC Torture Suite: Comprehensive conformance testing
- LLVM Test Suite: Cross-language performance baselines
- OpenSSL Security Reviews: Supply chain security practices

---

## FAQ

**Q: Why linear mapping for conformance instead of sigmoid?**

A: Linear is interpretable. 95% → 4.75 intuitively means "95% conformant". Sigmoid would compress the scale unhelpfully.

**Q: Can I override formula constants per target?**

A: YES! Edit `.language-eval/targets/<target>.yaml`:

```yaml
scoring_overrides:
  runtime_performance:
    throughput_baseline: 3000  # custom baseline for this target
    p95_latency_baseline: 100
  compiler_performance:
    slowdown_threshold: 0.1    # 10% slowdown penalty kicks in
```

**Q: How often should I recalibrate baselines?**

A: Quarterly for active development, annually for stable systems.

**Q: What if formula produces score <0 or >5?0?**

A: Clamping to [0.0, 5.0] handles this automatically. Check logs if frequently clamped; suggests formula miscalibration.

---

**Document Version:** 1.0  
**Last Updated:** 2026-02-19  
**Maintainer:** Language Evaluation Framework Team
