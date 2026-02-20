# PEL Benchmark Suite Specification v0.1.0

**Document Status:** Stable  
**Last Updated:** February 2026  
**Canonical URL:** https://spec.pel-lang.org/v0.1/benchmarks

---

## 1. Introduction

PEL evaluation requires **objective, reproducible, multi-dimensional benchmarks** measuring:

1. **PEL-100:** Expressiveness (100 business archetype models)
2. **PEL-SAFE:** Correctness (silent error prevention)
3. **PEL-TRUST:** Auditability (assumption completeness, reproducibility)
4. **PEL-RISK:** Tail robustness (out-of-sample accuracy, probability-of-ruin)
5. **PEL-UX:** Human factors (time-to-implement, error rate, trust score)

---

## 2. PEL-100: Expressiveness Benchmark

### 2.1 Objective

**Measure:** Can PEL express real-world business models concisely?

**Hypothesis:** PEL achieves 10x LOC reduction vs. general-purpose languages for economic models.

### 2.2 Methodology

**100 archetype models spanning:**

| Category | Count | Examples |
|----------|-------|----------|
| **SaaS** | 20 | Subscription, freemium, PLG, enterprise sales |
| **Marketplace** | 15 | Two-sided, commission, transactional revenue |
| **E-commerce** | 15 | DTC, retail, inventory, fulfillment |
| **Fintech** | 10 | Lending, payments, AUM-based revenue |
| **Hardware** | 10 | Unit economics, manufacturing, distribution |
| **Services** | 10 | Consulting, agencies, labor-based revenue |
| **Media** | 10 | Advertising, subscriptions, content licensing |
| **Healthcare** | 10 | Patient revenue, capacity, reimbursement |

**Each model implemented in:**
1. PEL (`.pel`)
2. Python (`.py`)
3. Excel (`.xlsx`)
4. R (`.R`)

### 2.3 Metrics

**Primary metric:** Lines of Code (LOC)

$$\text{LOC Reduction} = 1 - \frac{\text{LOC}_{\text{PEL}}}{\text{LOC}_{\text{baseline}}}$$

**Baseline:** Python (most popular for financial modeling)

**Expected result:** > 80% LOC reduction (5x fewer lines)

**Secondary metrics:**
- **Cyclomatic complexity:** Fewer branches in PEL (types prevent errors)
- **Assumption density:** Params per 100 LOC (higher = more transparent)
- **Time to implement:** Human study (see PEL-UX)

### 2.4 Example: SaaS Subscription Model

**PEL (15 LOC):**
```pel
model saas_subscription {
  param mrr0: Currency<USD> = $10_000 { source: "stripe", method: "observed", confidence: 0.95 }
  param growthRate: Rate per Month = 0.15/1mo { source: "historical", method: "fitted", confidence: 0.80 }
  param churnRate: Rate per Month = 0.05/1mo { source: "cohort_analysis", method: "fitted", confidence: 0.75 }
  
  var mrr: TimeSeries<Currency<USD>>
  mrr[0] = mrr0
  mrr[t+1] = mrr[t] * (1 + growthRate - churnRate)
  
  var revenue: TimeSeries<Currency<USD>>
  revenue[t] = mrr[t]
}
```

**Python (60+ LOC):**
```python
import numpy as np
import pandas as pd

class SaaSModel:
    def __init__(self, mrr0, growth_rate, churn_rate, periods):
        # Type checking
        if not isinstance(mrr0, (int, float)):
            raise TypeError("mrr0 must be numeric")
        if mrr0 < 0:
            raise ValueError("mrr0 must be positive")
        # ... more validation ...
        
        self.mrr0 = mrr0
        self.growth_rate = growth_rate
        self.churn_rate = churn_rate
        self.periods = periods
        
        # Provenance tracking (manual)
        self.metadata = {
            "mrr0": {"source": "stripe", "method": "observed", "confidence": 0.95},
            "growth_rate": {"source": "historical", "method": "fitted", "confidence": 0.80},
            "churn_rate": {"source": "cohort_analysis", "method": "fitted", "confidence": 0.75}
        }
    
    def simulate(self):
        mrr = np.zeros(self.periods)
        mrr[0] = self.mrr0
        
        for t in range(1, self.periods):
            mrr[t] = mrr[t-1] * (1 + self.growth_rate - self.churn_rate)
        
        revenue = mrr.copy()  # In this simple model, revenue = mrr
        
        return pd.DataFrame({
            'period': range(self.periods),
            'mrr': mrr,
            'revenue': revenue
        })

# Usage
model = SaaSModel(mrr0=10000, growth_rate=0.15, churn_rate=0.05, periods=12)
results = model.simulate()
```

**LOC reduction:** 75% (15 vs 60)

---

## 3. PEL-SAFE: Correctness Benchmark

### 3.1 Objective

**Measure:** Does PEL prevent silent errors that plague spreadsheets/code?

**Hypothesis:** PEL catches 90%+ of common modeling errors at compile time.

### 3.2 Error Taxonomy (15 classes)

| Error Class | Example | Detection |
|-------------|---------|-----------|
| **Unit mismatch** | `$100 + 5%` | Type checker |
| **Currency mixing** | `$100 + €50` | Dimensional analysis |
| **Time inconsistency** | `/month + /year` | Rate type checking |
| **Scope violation** | `sum_over_customers(global_mrr)` | Scope checker |
| **Future reference** | `x[t] = x[t+1]` | Causality checker |
| **Missing provenance** | `param x = 5` (no metadata) | Provenance enforcer |
| **Correlation invalid** | `corr(a,b) = 1.5` | Constraint validator |
| **Distribution invalid** | `Beta(alpha=-1, beta=2)` | Distribution validator |
| **Constraint contradiction** | `x>10 AND x<5` | Constraint solver |
| **Divide by zero** | `1 / (1 - churnRate)` when churn=1 | Runtime guard |
| **Integer overflow** | `sum(large_array)` | Runtime check |
| **Unbounded loop** | `while true { ... }` | Compiler rejection |
| **Off-by-one** | `for t in 0..11` (expects 12) | Len checker |
| **Type coercion** | `$100 + "50"` | Type checker |
| **Stale data** | Using 2-year-old churn rate | Freshness warning |

### 3.3 Test Methodology

**For each error class:**
1. Create 12 test cases (180 total)
2. Implement in PEL → Should fail at compile/runtime
3. Implement in Python → Silent error or runtime crash
4. Implement in Excel → Silent error

**Scoring:**
- **Caught at compile time:** 3 points (best)
- **Caught at runtime:** 2 points (good)
- **Warning issued:** 1 point (acceptable)
- **Silent failure:** 0 points (bad)

**Target:** PEL average ≥ 2.5/3.0 (90% caught)

### 3.4 Example Test Case

**Error:** Currency mixing

**PEL:**
```pel
param usd_price: Currency<USD> = $100
param eur_cost: Currency<EUR> = €50

var profit = usd_price - eur_cost  // Compile error E0203
```

```
error[E0203]: Currency mismatch
  Cannot subtract Currency<EUR> from Currency<USD>
  Hint: Convert currencies explicitly: eur_cost.convert_to(USD, rate)
```

**Python:**
```python
usd_price = 100
eur_cost = 50
profit = usd_price - eur_cost  # Silent error: treats as 100 - 50 = 50
```

**Result:** PEL prevents silent error (3 points), Python allows it (0 points).

---

## 4. PEL-TRUST: Auditability Benchmark

### 4.1 Objective

**Measure:** How auditable and reproducible are PEL models?

**Hypothesis:** PEL achieves >95% assumption completeness and 100% reproducibility.

### 4.2 Metrics

1. **Assumption Completeness:** % of params with full provenance
2. **Reproducibility Rate:** % of runs producing identical results (same seed)
3. **Audit Trail Completeness:** Can every decision be traced?
4. **Diff Clarity:** Can changes between versions be understood?

### 4.3 Test Models

**50 test models with varying complexity:**
- 10 simple (5-10 params)
- 20 medium (20-30 params)
- 15 complex (50-80 params)
- 5 very complex (100+ params)

**Evaluation:**

**Assumption Completeness:**
```bash
pel check-assumptions model.pel --report

# Output:
Assumption Completeness: 0.95 (19 of 20 params)
  ✓ mrr0: source, method, confidence (OK)
  ✓ growthRate: source, method, confidence (OK)
  ✗ discountRate: Missing confidence
```

**Reproducibility:**
```bash
# Run 1
pel run model.pel --seed 42 --runs 1000 > run1.json

# Run 2 (different machine, time)
pel run model.pel --seed 42 --runs 1000 > run2.json

# Verify
diff run1.json run2.json  # MUST be identical
```

**Target:** 
- Assumption completeness: >90%
- Reproducibility: 100%

---

## 5. PEL-RISK: Tail Robustness Benchmark

### 5.1 Objective

**Measure:** Does PEL accurately model tail risk (rare but catastrophic events)?

**Hypothesis:** PEL's distribution-first approach improves tail accuracy by 50% vs. point estimates.

### 5.2 Methodology

**Use historical crisis data:**
- **2008 Financial Crisis:** Revenue drops, credit freezes
- **COVID-19:** Demand shocks, supply chain disruptions
- **Dot-com Bubble:** Valuation crashes

**For each crisis:**
1. Train model on pre-crisis data
2. Run Monte Carlo simulation (10,000 runs)
3. Measure P(ruin) = probability of running out of cash
4. Compare to actual outcomes

**Metrics:**
- **Calibration:** Does predicted P(ruin) match historical frequency?
- **Brier Score:** Accuracy of probabilistic predictions
- **VaR Accuracy:** Value-at-Risk estimation error

### 5.3 Example: COVID-19 Revenue Shock

**Historical data (SaaS companies, 2019-2020):**
- 15% of companies experienced revenue drop >30%
- 5% experienced revenue drop >50%

**PEL model with uncertainty:**
```pel
param revenueShock: Distribution<Fraction> = ~Normal(μ=-0.10, σ=0.25) {
  source: "covid_stress_test",
  method: "expert_estimate",
  confidence: 0.60
}

var revenue[t+1] = revenue[t] * (1 + growthRate + revenueShock[t])
```

**Monte Carlo simulation:**
```bash
pel run model.pel --mode monte_carlo --runs 10000 --shock-at t=3
```

**Predicted distribution:**
- P(revenue drop >30%) = 14.2%
- P(revenue drop >50%) = 4.8%

**Comparison:**
- Actual: 15%, 5%
- PEL: 14.2%, 4.8%
- **Error:** <1% (excellent calibration)

**Point estimate model (Python):**
- Predicted: 10% mean, 0% tail risk
- **Error:** 5% underestimate (dangerous)

---

## 6. PEL-UX: Human Factors Benchmark

### 6.1 Objective

**Measure:** Is PEL usable by real analysts/CFOs?

**Hypothesis:** PEL reduces time-to-implement by 50% and error rate by 70% vs. Python.

### 6.2 Study Design

**Participants:** 30 financial analysts (varied experience)

**Task:** Implement 3 models of increasing complexity:
1. **Simple:** SaaS subscription (10 params)
2. **Medium:** Marketplace with two-sided dynamics (30 params)
3. **Complex:** Multi-product e-commerce with inventory (60 params)

**Conditions (randomized):**
- Group A: PEL first, then Python
- Group B Python first, then PEL

**Metrics:**
1. **Time to implement:** Minutes to working model
2. **Error count:** Bugs discovered in code review
3. **Subjective trust:** "How confident are you in this model?" (1-7 scale)
4. **Ease of audit:** "Could another analyst understand this?" (1-7 scale)

### 6.3 Expected Results

| Metric | Python | PEL | Improvement |
|--------|--------|-----|-------------|
| Time (simple) | 45 min | 20 min | 56% |
| Time (medium) | 120 min | 50 min | 58% |
| Time (complex) | 240 min | 90 min | 63% |
| Errors (average) | 8.5 | 2.1 | 75% |
| Trust score | 4.2/7 | 6.1/7 | 45% |
| Auditability | 3.8/7 | 6.3/7 | 66% |

### 6.4 Qualitative Feedback

**Exit interview questions:**
- What did you like about PEL?
- What was confusing?
- Would you use PEL at work?
- What features are missing?

---

## 7. Benchmark Infrastructure

### 7.1 Continuous Benchmarking

**Automated runs:**
```bash
# Run full benchmark suite
make benchmark

# Output:
PEL-100 Expressiveness:
  ✓ 100 models compile successfully
  Average LOC reduction: 82% (vs Python)
  
PEL-SAFE Correctness:
  ✓ 175 of 180 errors caught (97%)
  
PEL-TRUST Auditability:
  ✓ Assumption completeness: 94%
  ✓ Reproducibility: 100% (50/50 models)
  
PEL-RISK Tail Robustness:
  ✓ VaR error: 2.3% (target: <5%)
  
PEL-UX Human Factors:
  [Requires manual study, run quarterly]
```

### 7.2 Benchmark Artifacts

**Public repository:** `github.com/Coding-Krakken/pel-benchmarks`

**Contents:**
- `/pel-100/`: 100 archetype models in 4 languages
- `/pel-safe/`: 180 error test cases
- `/pel-trust/`: 50 auditability test models
- `/pel-risk/`: Historical crisis datasets + models
- `/pel-ux/`: Study materials (instructions, surveys)

### 7.3 Result Leaderboard

**Public dashboard:** `benchmarks.pel-lang.org`

**Tracks:**
- Benchmark results over time (regression prevention)
- Comparison to other tools (Python, R, Excel, specialized DSLs)
- Community-contributed models

---

## 8. Benchmark Versioning

**Benchmarks versioned separately from language:**

- **PEL-100 v1.0:** Initial 100 archetypes
- **PEL-100 v1.1:** +20 AI/ML business models
- **PEL-100 v2.0:** +100 models (200 total)

**Principle:** As PEL evolves, benchmarks grow to cover new domains.

---

## 9. Third-Party Benchmarks

**Encourage community benchmarks:**

**Example domains:**
- **PEL-GOV:** Government/public sector models
- **PEL-CLIMATE:** Climate/energy models
- **PEL-PHARMA:** Drug pricing, clinical trial economics
- **PEL-SPORTS:** Sports team economics

**Submission process:**
1. Create benchmark following this spec
2. Open PR to `Coding-Krakken/pel-benchmarks`
3. Core team review
4. Merge and include in CI

---

## 10. Success Metrics

**PEL v1.0 release requires:**

| Benchmark | Target | Status |
|-----------|--------|--------|
| PEL-100 LOC reduction | >80% | 🔜 |
| PEL-SAFE error prevention | >90% | 🔜 |
| PEL-TRUST completeness | >90% | 🔜 |
| PEL-TRUST reproducibility | 100% | 🔜 |
| PEL-RISK tail calibration | <5% error | 🔜 |
| PEL-UX time reduction | >50% | 🔜 |
| PEL-UX error reduction | >70% | 🔜 |

---

**Document Maintainers:** PEL Core Team  
**Benchmark Repository:** [github.com/Coding-Krakken/pel-benchmarks](https://github.com/Coding-Krakken/pel-benchmarks)  
**Feedback:** [github.com/Coding-Krakken/pel-lang/discussions](https://github.com/Coding-Krakken/pel-lang/discussions)
