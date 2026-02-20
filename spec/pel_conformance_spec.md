# PEL Conformance Specification v0.1.0

**Document Status:** Stable  
**Last Updated:** February 2026  
**Canonical URL:** https://spec.pel-lang.org/v0.1/conformance

---

## 1. Introduction

**Conformance levels** enable multiple PEL runtime implementations while ensuring interoperability and correctness.

**Three conformance levels:**
1. **PEL-Core:** Deterministic simulation + type checking (minimum viable)
2. **PEL-Extended:** + Monte Carlo + sensitivity analysis (production-ready)
3. **PEL-Calibration:** + Data ingestion + parameter fitting (full-featured)

---

## 2. Conformance Levels

### 2.1 PEL-Core (Level 1)

**Required features:**

**Compiler:**
- ✅ Lexer and parser (full EBNF grammar from language spec)
- ✅ AST construction
- ✅ Type checker with bidirectional inference
- ✅ Dimensional analysis (currency, rate, duration units)
- ✅ Scope checking (timeseries causality, entity isolation)
- ✅ Provenance validation (all params have source/method/confidence)
- ✅ Error reporting (287 error codes from language spec)
- ✅ PEL-IR generation (canonical JSON representation)

**Runtime:**
- ✅ Deterministic execution (single-run mode)
- ✅ Distribution sampling at mean/median (no Monte Carlo)
- ✅ Constraint checking (fatal stops, warning logs)
- ✅ Policy execution (trigger-action semantics)
- ✅ TimeSeries evaluation (t=0 to T)
- ✅ Result serialization (JSON output)
- ✅ Reproducibility (same seed → identical results)

**Standard Library:**
- ✅ Core types (Currency, Rate, Duration, Distribution, TimeSeries)
- ✅ Math functions (min, max, sum, avg, exp, log, sqrt)
- ✅ Aggregations (sum_over_range, count, filter)

**Not required in Core:**
- ❌ Monte Carlo simulation
- ❌ Sensitivity analysis
- ❌ Data connectors
- ❌ Calibration tools
- ❌ Visualizations

### 2.2 PEL-Extended (Level 2)

**All of PEL-Core PLUS:**

**Runtime:**
- ✅ Monte Carlo simulation (N runs with sampling)
- ✅ Correlation sampling (Gaussian copula + Cholesky)
- ✅ Sensitivity analysis (tornado charts, Sobol indices)
- ✅ Constraint tracer (slack variables, first-binding detection)
- ✅ Parallel execution (multi-core Monte Carlo)
- ✅ Percentile outputs (P10, P50, P90)

**Standard Library:**
- ✅ 9 stdlib modules (demand, funnel, pricing, unit_econ, cashflow, retention, capacity, hiring, shock_library)

**Tooling:**
- ✅ LSP server (autocomplete, diagnostics)
- ✅ Formatter (deterministic, idempotent)
- ✅ Linter (50+ rules)

**Not required in Extended:**
- ❌ Data connectors
- ❌ Calibration (MLE, Bayesian fitting)
- ❌ Drift detection

### 2.3 PEL-Calibration (Level 3)

**All of PEL-Extended PLUS:**

**Calibration:**
- ✅ Data connectors (CSV, SQL, Data Warehouse APIs)
- ✅ Parameter estimation (MLE, Bayesian, Method of Moments)
- ✅ Distribution fitting (K-S test, Anderson-Darling, Q-Q plots)
- ✅ Model-data reconciliation (residual analysis, MAPE)
- ✅ Drift detection (K-S test, CUSUM, sequential testing)
- ✅ Sensitivity-driven measurement prioritization

---

## 3. Test Harness

### 3.1 Official Test Suite

**Repository:** `github.com/Coding-Krakken/pel-conformance`

**Structure:**
```
/conformance-tests/
  /core/
    /compiler/
      /lexer/       # 50 tests
      /parser/      # 100 tests
      /typechecker/ # 150 tests
    /runtime/
      /deterministic/ # 80 tests
      /constraints/   # 60 tests
      /policies/      # 40 tests
  /extended/
    /monte_carlo/     # 50 tests
    /correlation/     # 40 tests
    /sensitivity/     # 30 tests
  /calibration/
    /fitting/         # 40 tests
    /drift/           # 20 tests
```

### 3.2 Test Format

**Each test is YAML:**

```yaml
test_id: core-compiler-typechecker-001
level: core
category: compiler/typechecker
description: "Detects currency mismatch"

input:
  file: test.pel
  content: |
    param usd: Currency<USD> = $100
    param eur: Currency<EUR> = €50
    var result = usd + eur

expected:
  result: error
  error_code: E0203
  error_message: "Currency mismatch: cannot add Currency<EUR> to Currency<USD>"
```

### 3.3 Running Conformance Tests

```bash
# Test your implementation
pel-conformance test --level core --runtime /path/to/your/runtime

# Output:
Running PEL-Core Conformance Tests...
  Compiler Tests:
    Lexer: 50/50 passed ✓
    Parser: 98/100 passed (2 failures)
    Typechecker: 150/150 passed ✓
  Runtime Tests:
    Deterministic: 80/80 passed ✓
    Constraints: 58/60 passed (2 failures)
    Policies: 40/40 passed ✓
    
Overall: 476/480 passed (99.2%)
Status: PASS (threshold: 98%)
```

---

## 4. Certification Process

### 4.1 Self-Certification

**For open-source implementations:**

1. Run official test suite
2. Publish results (markdown report)
3. Submit PR to `pel-lang/conformance-registry`

**Example entry:**
```yaml
implementation:
  name: "pel-reference"
  version: "0.1.0"
  language: "Python"
  license: "AGPL-3.0-or-later OR Commercial"
  url: "https://github.com/Coding-Krakken/pel-reference"
  
conformance:
  level: extended
  test_date: "2026-02-13"
  test_suite_version: "v0.1.0"
  results:
    core: 480/480 (100%)
    extended: 120/120 (100%)
    calibration: 0/60 (not implemented)
```

### 4.2 Official Certification (Future)

**For commercial implementations:**

- Submit implementation to PEL Foundation (TBD)
- Independent testing by core team
- Certification badge issued if passed
- Annual re-certification required

---

## 5. Backward Compatibility

### 5.1 Policy

**Within same MAJOR version (e.g., 0.x.y):**

**MUST preserve:**
- IR format (can read older IR)
- Semantics (same model → same results, given same seed)
- Error codes (E0xxx codes stable)

**MAY change:**
- Performance (optimizations allowed)
- Error messages (wording improvements)
- Internal implementation

### 5.2 Deprecation Process

**For breaking changes:**

1. **Announce deprecation** (in release notes)
2. **Issue warnings** (for 2 minor versions)
3. **Remove in next MAJOR version**

**Example:**
- v0.1.0: Feature X works normally
- v0.2.0: Feature X deprecated, warning issued
- v0.3.0: Warning continues
- v1.0.0: Feature X removed

---

## 6. Interoperability

### 6.1 IR Portability

**PEL models compiled to IR can run on ANY conformant runtime.**

**Test:**
```bash
# Compile with reference compiler
pel-reference compile model.pel -o model.ir.json

# Run on alternative runtime
pel-alternative run model.ir.json --seed 42 > output.json

# Results MUST be identical (bit-for-bit)
```

### 6.2 Cross-Runtime Testing

**Matrix testing:**

| Compiler ↓ Runtime → | pel-ref | pel-rust | pel-js |
|----------------------|---------|----------|--------|
| pel-ref | ✓ | ✓ | ✓ |
| pel-rust | ✓ | ✓ | ✓ |
| pel-js | ✓ | ✓ | ✓ |

**Each cell:** Run 100 test models, verify identical outputs.

---

## 7. Performance Benchmarks

### 7.1 Not Part of Conformance

**Conformance = correctness, not speed.**

**Implementations MAY vary in:**
- Compilation speed
- Execution speed
- Memory usage

### 7.2 Recommended Benchmarks (Optional)

**For performance comparison:**

```bash
# Standard benchmark models
pel benchmark --model pel-100-saas-001 --runs 10000

# Output (example):
Compilation time: 0.5s
Execution time (deterministic): 0.02s
Execution time (Monte Carlo, 10k runs): 3.5s
Memory peak: 150 MB
```

**Leaderboard:** Community-maintained (not official)

---

## 8. Conformance Checklist

### 8.1 PEL-Core Checklist

**Before self-certifying as PEL-Core:**

- [ ] All 50 lexer tests pass
- [ ] All 100 parser tests pass
- [ ] All 150 typechecker tests pass
- [ ] All 80 deterministic runtime tests pass
- [ ] All 60 constraint tests pass
- [ ] All 40 policy tests pass
- [ ] IR generation produces valid JSON Schema
- [ ] Reproducibility: same seed → same results (100/100 models)
- [ ] Error codes match spec (E0xxx)
- [ ] Documentation covers all implemented features

### 8.2 PEL-Extended Checklist

**All of Core PLUS:**

- [ ] All 50 Monte Carlo tests pass
- [ ] All 40 correlation tests pass (Cholesky, copula)
- [ ] All 30 sensitivity tests pass (tornado, Sobol)
- [ ] Parallel execution works (multicore)
- [ ] Stdlib modules implemented (9 modules)
- [ ] LSP server functional (autocomplete, diagnostics)
- [ ] Formatter is deterministic and idempotent
- [ ] Linter has ≥30 rules

### 8.3 PEL-Calibration Checklist

**All of Extended PLUS:**

- [ ] All 40 fitting tests pass (MLE, Bayesian, MoM)
- [ ] All 20 drift detection tests pass (K-S, CUSUM)
- [ ] Data connectors work (CSV, SQL)
- [ ] Distribution fitting quality metrics (K-S, Anderson-Darling)
- [ ] Residual analysis tools
- [ ] Sensitivity-driven prioritization

---

## 9. Non-Conformant Behavior

### 9.1 Prohibited

**Implementations MUST NOT:**
- Silently ignore errors (all errors must surface)
- Produce non-deterministic results (for same seed)
- Violate type safety (no runtime type errors)
- Skip provenance validation (all params need metadata)
- Introduce vendor-specific syntax (incompatible with spec)

### 9.2 Reporting Non-Conformance

**If you find a conformant implementation producing wrong results:**

1. Isolate minimal test case
2. File issue: `github.com/Coding-Krakken/pel-lang/issues`
3. Tag: `conformance-violation`
4. Include: implementation name, version, test input, expected output, actual output

---

## 10. Reference Implementation

### 10.1 Official Reference

**Repository:** `github.com/Coding-Krakken/pel-reference`

**Language:** Python 3.11+

**Status:** PEL-Extended conformant (as of v0.1.0)

**Purpose:**
- Canonical implementation of spec
- Reference for ambiguous cases
- Test suite development

### 10.2 Alternative Implementations (Planned)

**Community-driven:**
- **pel-rust:** Rust implementation (performance)
- **pel-js:** JavaScript/WASM (browser-based modeling)
- **pel-julia:** Julia implementation (scientific computing)

---

## 11. Versioning and Stability

### 11.1 Conformance Levels Are Stable

**Once certified, implementations:**
- MUST continue to pass tests
- SHOULD monitor regressions (CI)
- MUST disclose breaking changes

### 11.2 Test Suite Versioning

**Test suite versions track PEL spec:**

- **v0.1.x:** Tests for PEL v0.1 spec
- **v0.2.x:** Tests for PEL v0.2 spec
- **v1.0.x:** Tests for PEL v1.0 spec

**Implementations declare which test suite version they pass.**

---

## 12. Frequently Asked Questions

### Q1: Can I implement only PEL-Core?

**Yes.** Core is sufficient for deterministic modeling. Many use cases don't need Monte Carlo.

### Q2: Can I add extensions beyond the spec?

**Yes,** but:
- Extensions must be opt-in (not default behavior)
- Extensions must not break conformant models
- Document as non-standard (don't claim full conformance)

### Q3: How do I report ambiguities in the spec?

**File issue:** `github.com/Coding-Krakken/pel-lang/issues` with tag `spec-clarification`

### Q4: Can I charge for my implementation?

**Yes.** Spec is open (AGPL-3.0), and implementations can be commercial or dual-licensed. The reference implementation is dual-licensed (AGPL-3.0 OR Commercial).

### Q5: What if two implementations disagree?

**Reference implementation wins.** If reference is wrong, it's a spec bug (file issue).

---

## Appendix A: Conformance Matrix

| Feature | Core | Extended | Calibration |
|---------|------|----------|-------------|
| **Compiler** | | | |
| Lexer/Parser | ✅ | ✅ | ✅ |
| Type checker | ✅ | ✅ | ✅ |
| Dimensional analysis | ✅ | ✅ | ✅ |
| Provenance validation | ✅ | ✅ | ✅ |
| **Runtime** | | | |
| Deterministic sim | ✅ | ✅ | ✅ |
| Monte Carlo | ❌ | ✅ | ✅ |
| Correlation (copula) | ❌ | ✅ | ✅ |
| Sensitivity analysis | ❌ | ✅ | ✅ |
| Constraint checking | ✅ | ✅ | ✅ |
| Policy execution | ✅ | ✅ | ✅ |
| **Calibration** | | | |
| Data connectors | ❌ | ❌ | ✅ |
| Parameter fitting | ❌ | ❌ | ✅ |
| Drift detection | ❌ | ❌ | ✅ |
| **Stdlib** | | | |
| Core types | ✅ | ✅ | ✅ |
| 9 modules | ❌ | ✅ | ✅ |
| **Tooling** | | | |
| LSP server | ❌ | ✅ | ✅ |
| Formatter | ❌ | ✅ | ✅ |
| Linter | ❌ | ✅ | ✅ |

---

**Document Maintainers:** PEL Core Team  
**Conformance Registry:** [github.com/Coding-Krakken/conformance-registry](https://github.com/Coding-Krakken/conformance-registry)  
**Feedback:** [github.com/Coding-Krakken/pel-lang/discussions](https://github.com/Coding-Krakken/pel-lang/discussions)
