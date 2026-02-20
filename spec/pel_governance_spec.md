# PEL Governance Specification v0.1.0

**Document Status:** Stable  
**Last Updated:** February 2026  
**Canonical URL:** https://spec.pel-lang.org/v0.1/governance

---

## 1. Introduction

PEL governance ensures economic models are **auditable, reproducible, and trustworthy** through mandatory provenance tracking, model versioning, and assumption registries.

---

## 2. Provenance Requirements

### 2.1 Mandatory Metadata

Every `param` **MUST** include:

```pel
param name: Type = value {
  source: String,        // Data origin (REQUIRED)
  method: String,        // Derivation method (REQUIRED)
  confidence: [0.0, 1.0] // Confidence level (REQUIRED)
}
```

**Optional fields:** `freshness`, `owner`, `correlated_with`, `notes`

### 2.2 Method Types

- `observed`: Direct measurement from data
- `fitted`: Statistical fitting (e.g., MLE, regression)
- `derived`: Calculated from other parameters
- `expert_estimate`: Subject matter expert judgment
- `external_research`: Third-party study/publication
- `assumption`: Pure assumption (requires justification in `notes`)

### 2.3 Confidence Scale

| Confidence | Interpretation |
|------------|----------------|
| 0.90-1.00 | High confidence (direct observation, large sample) |
| 0.70-0.89 | Moderate confidence (fitted from data, medium sample) |
| 0.50-0.69 | Low confidence (small sample, extrapolation) |
| 0.30-0.49 | Very low confidence (expert guess, weak evidence) |
| 0.00-0.29 | Speculative (placeholder, requires measurement) |

### 2.4 Freshness Encoding

**ISO 8601 duration format:**
- `P1W` = 1 week
- `P1M` = 1 month
- `P3M` = 3 months
- `P1Y` = 1 year

**Example:**
```pel
param churnRate: Rate per Month = 0.05/1mo {
  source: "cohort_analysis_2025Q4",
  method: "fitted",
  confidence: 0.75,
  freshness: "P3M"  // Data is 3 months old
}
```

---

## 3. Assumption Register

### 3.1 Auto-Generation

Compiler **MUST** generate assumption register as compilation artifact.

**Output format:** JSON

```json
{
  "model_hash": "sha256:abc123...",
  "generated_at": "2026-02-13T10:30:00Z",
  "assumptions": [
    {
      "name": "churnRate",
      "type": "Rate per Month",
      "value": "0.05 / 1mo",
      "distribution": null,
      "source": "cohort_analysis_2025Q4",
      "method": "fitted",
      "confidence": 0.75,
      "freshness": "P3M",
      "owner": "analytics@company.com",
      "sensitivity_rank": 2,
      "notes": "Seasonality observed in Q4"
    }
  ],
  "assumption_completeness_score": 0.95
}
```

### 3.2 Assumption Completeness Score

$$\text{Completeness} = \frac{\text{\# params with full provenance}}{\text{Total \# params}}$$

**Full provenance** = source + method + confidence + (freshness **OR** freshness_not_applicable)

**Minimum threshold for publication:** 90% (configurable)

**Compiler error if below threshold:**
```
error[E0400]: Assumption completeness below threshold
  Completeness: 0.75 (15 of 20 params)
  Threshold: 0.90
  
  Missing provenance:
    - cac (line 45): No confidence specified
    - growthRate (line 67): No source specified
    - priceElasticity (line 89): No method specified
```

---

## 4. Model Hashing

### 4.1 Model Hash Computation

$$H_{\text{model}} = \text{SHA-256}(\text{CanonicalIR}(M))$$

where `CanonicalIR(M)` is normalized IR:
1. Sort all keys alphabetically
2. Remove whitespace
3. Normalize numeric representations (e.g., `1.0` = `1.00`)
4. Serialize to JSON

**Property:** Semantically equivalent models **MUST** produce identical hash.

### 4.2 Assumption Hash

$$H_{\text{assumptions}} = \text{SHA-256}(\text{serialize}(\text{provenance\_metadata}))$$

Includes all provenance blocks (source, method, confidence, correlations).

### 4.3 Combined Model Fingerprint

$$\text{Fingerprint} = (H_{\text{model}}, H_{\text{assumptions}}, V_{\text{runtime}})$$

where $V_{\text{runtime}}$ is PEL runtime version (e.g., `pel-0.1.0`).

---

## 5. Run Artifacts

### 5.1 Artifact Contents

Every simulation run **MUST** produce artifact containing:

```json
{
  "model_hash": "sha256:...",
  "assumption_hash": "sha256:...",
  "runtime_version": "pel-0.1.0",
  "seed": 42,
  "simulation_mode": "monte_carlo",
  "num_runs": 10000,
  "timestamp": "2026-02-13T12:00:00Z",
  "results": {
    "output_variables": [...],
    "constraint_violations": [...],
    "policy_executions": [...]
  },
  "metadata": {
    "execution_time_seconds": 3.5,
    "machine_id": "...",
    "user": "analyst@company.com"
  }
}
```

### 5.2 Reproducibility Guarantee

Given artifact with $(H_m, H_a, s, V)$:

**ANY conformant runtime** with version $V$ **MUST** reproduce identical results when given:
- Model with hash $H_m$
- Assumptions with hash $H_a$
- Seed $s$

**Test:**
```bash
# Run 1
pel run model.pel --seed 42 > run1.json

# Run 2 (different machine, time, user)
pel run model.pel --seed 42 > run2.json

# MUST be identical
pel verify-reproducibility run1.json run2.json
# Output: ✓ Results identical (bit-for-bit)
```

---

## 6. Model Diffing

### 6.1 Semantic Diff

**Command:**
```bash
pel diff model_v1.pel model_v2.pel
```

**Output categories:**

1. **Parameter changes:**
   - Value changed
   - Distribution changed
   - Provenance changed

2. **Structural changes:**
   - Variables added/removed
   - Constraints added/removed
   - Policies added/removed

3. **Economic changes:**
   - Unit economics impact (LTV, CAC, margin)
   - Cash flow impact
   - Constraint criticality changes

**Example output:**
```
Model Diff: model_v1.pel → model_v2.pel

Parameter Changes:
  churnRate:
    value: 0.05/1mo → 0.06/1mo (+20%)
    confidence: 0.75 → 0.80
    freshness: P3M → P1M
    
  cac:
    distribution: LogNormal(μ=$500, σ=$150) → LogNormal(μ=$550, σ=$180)
    impact: +10% mean, +20% variance

Structural Changes:
  + Added constraint: target_ltv_to_cac_ratio
  - Removed policy: emergency_hiring_freeze

Economic Impact Forecast:
  LTV: -16.7% (due to churnRate increase)
  Margin: -$180 per customer
  Runway: -3 months (cash depletes earlier)
  First binding constraint: Unchanged (cash_positive at t=18)
```

---

## 7. Audit Logging

### 7.1 Model Change Log

**Track:**
- Who changed what
- When
- Why (commit message)
- Approval workflow status

**Git integration recommended:**
```bash
git log --format="%h %an %ad %s" model.pel

# Example output:
abc123 Alice 2026-02-01 "Update churnRate from Q4 data"
def456 Bob   2026-01-15 "Add cash preservation policy"
```

### 7.2 Run Audit Trail

**For regulated environments:**

Persistent log of:
- Model version used
- Assumptions version
- Who ran simulation
- When
- Purpose (board meeting, planning, stress test)
- Results hash

**Example:**
```json
{
  "audit_id": "run-2026-02-13-001",
  "model_hash": "sha256:...",
  "run_by": "cfo@company.com",
  "run_at": "2026-02-13T09:00:00Z",
  "purpose": "Q1 board presentation",
  "scenario": "base_case",
  "approved_by": "ceo@company.com",
  "results_hash": "sha256:..."
}
```

---

## 8. Assumption Freshness Alerts

### 8.1 Staleness Detection

**Automatic alerts when assumptions age:**

```bash
pel check-freshness model.pel

# Output:
Warning: 3 assumptions stale (>6 months old)
  churnRate: Last updated 2025-09-01 (164 days ago)
  cac: Last updated 2025-08-15 (180 days ago)
  conversionRate: Last updated 2025-07-01 (225 days ago)

Recommendation: Refresh data before board presentation.
```

### 8.2 Confidence Decay (Optional)

**Future extension:** Automatically reduce confidence over time.

Not in v0.1, but planned.

---

## 9. PEL Enhancement Proposals (PEPs)

### 9.1 Specification Change Process

**For changes to PEL language or conformance:**

1. **Draft PEP** (use template at `/spec/pep_template.md`)
2. **Submit PR** to `/spec/peps/pep-NNNN-title.md`
3. **Community discussion** (minimum 2 weeks)
4. **Core team vote** (2/3 majority required)
5. **Implementation** (after acceptance)
6. **Finalization** (when released in stable version)

### 9.2 PEP Template

```markdown
# PEP-NNNN: Title

**Status:** Proposed | Accepted | Rejected | Implemented | Final
**Authors:** Name <email>
**Created:** YYYY-MM-DD

## Abstract
[1-paragraph summary]

## Motivation
[Why is this needed?]

## Specification
[Precise technical description]

## Rationale
[Design choices, alternatives considered]

## Backward Compatibility
[Impact on existing models]

## Reference Implementation
[Link to prototype or  PR]

## Examples
[Before/after code samples]
```

---

## 10. Versioning Policy

### 10.1 Semantic Versioning

**PEL uses semantic versioning:** `MAJOR.MINOR.PATCH`

- **MAJOR:** Breaking changes (incompatible IR, language changes)
- **MINOR:** New features (backward compatible)
- **PATCH:** Bug fixes only

### 10.2 Backward Compatibility Guarantee

**Within same MAJOR version:**
- Models compile identically
- Results reproduce identically (same seed)
- IR format compatible (can read older IR)

**Across MAJOR versions:**
- No guarantee (migration guide provided)

---

## Appendix A: Assumption Completeness Checklist

For publication-ready models:

- [ ] All `param` declarations include `source`
- [ ] All `param` declarations include `method`
- [ ] All `param` declarations include `confidence`
- [ ] `freshness` specified OR documented as static
- [ ] High-sensitivity params have confidence ≥ 0.60
- [ ] Correlations specified where applicable
- [ ] Model hash computed and recorded
- [ ] Assumption register generated
- [ ] Assumption completeness score ≥ 0.90
- [ ] Model diff reviewed (if updated from previous version)

---

**Document Maintainers:** PEL Core Team  
**Feedback:** [github.com/Coding-Krakken/pel-lang/discussions](https://github.com/Coding-Krakken/pel-lang/discussions)
