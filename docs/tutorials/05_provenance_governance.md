# Tutorial 5: Provenance & Assumption Governance

## Overview

**The #1 problem with business models**: Nobody knows where the numbers came from. Six months later, stakeholders ask "Why did we assume 15% growth?" and the analyst who built the model has left the company. PEL solves this with **mandatory provenance** - every parameter must document:

- **Source**: Where the number came from
- **Method**: How it was derived
- **Confidence**: How certain we are
- **Notes** (optional): Additional context

This creates an **auditable assumption ledger** that makes models trustworthy and maintainable.

**Time required**: 20 minutes  
**Prerequisites**: Tutorials 1-2  
**Learning outcomes**: 
- Understand provenance fields and their purpose
- Write complete provenance metadata
- Generate assumption reports
- Track assumption quality over time

## Why Provenance Matters

### The Spreadsheet Problem: Ghost Assumptions

Consider this typical spreadsheet:

| Parameter | Value |
|-----------|-------|
| Growth Rate | 15% |
| Churn | 5% |
| ARPU | $100 |

**Critical questions**:
- Where did 15% come from? (Industry average? Historical data? Wild guess?)
- Who decided this? When?
- How confident are we?
- What happens if we're wrong?

**Result**: Models are black boxes. Stakeholders don't trust them.

### The PEL Solution: Assumption Transparency

```pel
param growth_rate: Rate per Month = 0.15 / 1mo {
  source: "historical_analysis",
  method: "fitted",
  confidence: 0.75,
  notes: "Fitted from last 18 months of customer growth data (Q3 2024 - Q1 2026)"
}

param churn: Probability = 0.05 {
  source: "assumption",
  method: "expert_estimate",
  confidence: 0.40,
  notes: "Industry benchmark - we lack internal data. High uncertainty."
}

param arpu: Currency<USD> = $100 {
  source: "billing_system",
  method: "observed",
  confidence: 0.95,
  notes: "Average of last 3 months from Stripe dashboard"
}
```

**Benefits**:
- **Auditability**: Clear record of every assumption
- **Confidence scoring**: Quantify uncertainty
- **Accountability**: Track who made which assumptions
- **Maintenance**: Future analysts understand the model
- **Trust**: Stakeholders see the reasoning

## Provenance Fields

### 1. `source`: Where the Number Came From

Describes the **origin** of the data. Common values:

| Source | Meaning | Example |
|--------|---------|---------|
| `observed` | Measured from reality | "Stripe billing data", "Google Analytics" |
| `historical_analysis` | Derived from historical data | "Fitted from 2 years of sales data" |
| `assumption` | Expert judgment or guess | "CFO estimate", "Industry benchmark" |
| `derived` | Calculated from other parameters | "ARPU = monthly_revenue / customer_count" |
| `external_research` | Third-party data | "Gartner report", "Census data" |
| `contract` | Legal/binding agreement | "Vendor SLA", "Loan covenant" |
| `regulation` | Legal requirement | "GDPR compliance", "Tax rate" |
| `experiment` | A/B test or trial | "Landing page test (Feb 2026)" |

**Best practices**:
- Be specific: ✅ "Stripe dashboard - Jan 2026" > ❌ "billing"
- Name the system: ✅ "Salesforce CRM" > ❌ "sales_data"
- Include timeframe: ✅ "Q4 2025 cohort analysis" > ❌ "cohort_analysis"

### 2. `method`: How It Was Derived

Describes the **process** used to obtain the value:

| Method | Meaning | When to Use |
|--------|---------|-------------|
| `observed` | Direct measurement | Live system data, accounting records |
| `fitted` | Statistical fitting | Regression, MLE, curve fitting |
| `derived` | Calculated from other values | Formulas, ratios |
| `expert_estimate` | Informed judgment | Industry experience, best guess |
| `assumption` | Placeholder / hypothesis | Unknown values, scenarios |
| `benchmark` | Industry comparison | "Typical SaaS churn is 5%" |
| `interpolated` | Estimated between known points | Missing data in time series |
| `calibration` | Tuned to match reality | Model parameters adjusted to fit observations |

**Examples**:

```pel
// Method: observed (direct measurement)
param current_arr: Currency<USD> = $1_200_000 {
  source: "billing_system",
  method: "observed",
  confidence: 0.99,
  notes: "Annual Recurring Revenue from Stripe as of Feb 2026"
}

// Method: fitted (statistical analysis)
param customer_lifetime_months: Duration ~ LogNormal(μ=3.2, σ=0.5) {
  source: "cohort_analysis",
  method: "fitted",
  confidence: 0.80,
  notes: "MLE fit to 5,432 churned customers (2024-2025)"
}

// Method: expert_estimate
param competitor_launch_delay: Duration ~ Uniform(min: 3mo, max: 12mo) {
  source: "product_team",
  method: "expert_estimate",
  confidence: 0.30,
  notes: "PM estimate based on competitor job postings - high uncertainty"
}

// Method: derived
param ltv_cac_ratio: Fraction = ltv / cac {
  source: "model",
  method: "derived",
  confidence: 0.85,
  notes: "Calculated from LTV and CAC parameters"
}
```

### 3. `confidence`: How Certain We Are

Numeric score from **0.0 (wild guess) to 1.0 (absolute certainty)**:

| Range | Interpretation | When to Use |
|-------|----------------|-------------|
| 0.95 - 1.0 | Near-certain | Legal contracts, accounting records |
| 0.80 - 0.94 | High confidence | Well-measured data, strong evidence |
| 0.60 - 0.79 | Moderate confidence | Some data, reasonable assumptions |
| 0.40 - 0.59 | Low confidence | Limited data, extrapolations |
| 0.20 - 0.39 | Very low | Educated guesses, high uncertainty |
| 0.0 - 0.19 | Speculation | Pure guesswork, placeholders |

**Guidelines**:

```pel
// Confidence: 0.99 (contractual obligation - certain)
param monthly_rent: Currency<USD> = $15_000 {
  source: "lease_agreement",
  method: "observed",
  confidence: 0.99,
  notes: "Office lease - 3 year contract signed Dec 2025"
}

// Confidence: 0.85 (measured data, recent)
param current_monthly_churn: Probability = 0.047 {
  source: "analytics_dashboard",
  method: "observed",
  confidence: 0.85,
  notes: "Trailing 90-day average from Amplitude (Feb 2026)"
}

// Confidence: 0.60 (reasonable assumption based on partial data)
param sales_cycle_days: Duration ~ LogNormal(μ=3.9, σ=0.4) {
  source: "crm_analysis",
  method: "fitted",
  confidence: 0.60,
  notes: "Fitted from 87 closed deals - limited sample size"
}

// Confidence: 0.30 (guess based on industry data)
param market_share_2027: Probability = 0.12 {
  source: "market_research_report",
  method: "benchmark",
  confidence: 0.30,
  notes: "Industry avg for new entrants - we may differ significantly"
}

// Confidence: 0.10 (placeholder - need to research)
param regulatory_approval_time: Duration = 6mo {
  source: "assumption",
  method: "assumption",
  confidence: 0.10,
  notes: "PLACEHOLDER - legal team review pending"
}
```

**Calibration tip**: If you're uncertain about confidence, that's a **low confidence** score (0.3-0.5).

### 4. `notes`: Additional Context (Optional but Recommended)

Free-text field for:
- Detailed sourcing information
- Caveats and limitations
- Rationale for choices
- Action items ("TODO: update with Q1 data")

**Examples**:

```pel
param churn_rate: Probability ~ Beta(alpha: 5, beta: 95) {
  source: "subscription_analytics",
  method: "fitted",
  confidence: 0.70,
  notes: "Beta fit to monthly churn over 14 months. Note: higher in Jan/Feb (post-holiday effect). Consider seasonal model for v2."
}

param cac: Currency<USD> ~ LogNormal(μ=5.5, σ=0.3) {
  source: "marketing_team",
  method: "derived",
  confidence: 0.65,
  notes: "Total marketing spend / new customers. Excludes word-of-mouth (25% of signups). May underestimate true CAC."
}

param ai_feature_adoption: Probability = 0.40 {
  source: "assumption",
  method: "expert_estimate",
  confidence: 0.25,
  notes: "SPECULATIVE - new feature launching Q3 2026. No comparable products. Range: 20-60%. Needs validation post-launch."
}
```

## Provenance Validation

PEL enforces **provenance completeness** at compile time:

### Complete Provenance (✅ Valid)

```pel
param revenue: Currency<USD> = $100_000 {
  source: "billing_system",
  method: "observed",
  confidence: 0.95
}
```

### Missing Fields (❌ Compile Error)

```pel
// ❌ Error: Missing provenance metadata
param revenue: Currency<USD> = $100_000
```

```
Compile Error: Parameter 'revenue' missing provenance metadata
  Required fields: source, method, confidence
  File: model.pel, line 5
```

### Incomplete Provenance (❌ Compile Error)

```pel
// ❌ Error: Missing confidence
param revenue: Currency<USD> = $100_000 {
  source: "billing_system",
  method: "observed"
}
```

```
Compile Error: Parameter 'revenue' provenance incomplete
  Missing field: confidence
  File: model.pel, line 5
```

## Provenance Reporting

PEL generates **assumption reports** to audit provenance quality:

### Generate Assumption Report

```bash
pel compile model.pel
pel report model.ir.json --type assumptions -o assumptions.html
```

### Example Report: Assumption Summary

```
Assumption Quality Report
Model: SaasGrowthModel
Generated: 2026-02-19 14:32:00 UTC

=== Provenance Completeness ===
Parameters: 12
Complete provenance: 12 (100%)
Missing provenance: 0 (0%)

=== Confidence Distribution ===
High (≥0.80):      5 parameters (42%)
Moderate (0.60-0.79): 4 parameters (33%)
Low (0.40-0.59):   2 parameters (17%)
Very Low (<0.40):  1 parameter  (8%)

=== Source Breakdown ===
observed:          6 parameters
fitted:            3 parameters
assumption:        2 parameters
derived:           1 parameter

=== Low-Confidence Parameters (Action Required) ===
1. competitor_response_time (confidence: 0.25)
   Source: assumption | Method: expert_estimate
   Notes: "Pure speculation - no market intelligence"
   ⚠️ Consider: Market research, war-gaming scenarios

2. viral_coefficient (confidence: 0.45)
   Source: experiment | Method: fitted
   Notes: "Only 200 invites sent - need more data"
   ⚠️ Consider: Extend experiment, increase sample size
```

### Export to JSON for Programmatic Access

```bash
pel report model.ir.json --type assumptions --format json -o assumptions.json
```

```json
{
  "model": "SaasGrowthModel",
  "timestamp": "2026-02-19T14:32:00Z",
  "parameters": [
    {
      "name": "growth_rate",
      "type": "Rate per Month",
      "value": "0.15 / 1mo",
      "provenance": {
        "source": "historical_analysis",
        "method": "fitted",
        "confidence": 0.75,
        "notes": "Fitted from 18 months of customer data"
      }
    },
    {
      "name": "churn_rate",
      "type": "Probability",
      "value": "0.05",
      "provenance": {
        "source": "assumption",
        "method": "expert_estimate",
        "confidence": 0.40,
        "notes": "Industry benchmark - lack internal data"
      },
      "flags": ["low_confidence"]
    }
  ],
  "summary": {
    "total_parameters": 12,
    "avg_confidence": 0.68,
    "low_confidence_count": 3
  }
}
```

## Provenance Governance Workflow

### Step 1: Initial Model (Many Assumptions)

```pel
model ProductLaunchV1 {
  // Week 1: Placeholder assumptions
  param market_size: Currency<USD> = $50_000_000 {
    source: "assumption",
    method: "assumption",
    confidence: 0.20,
    notes: "PLACEHOLDER - market research needed"
  }
  
  param conversion_rate: Probability = 0.10 {
    source: "assumption",
    method: "expert_estimate",
    confidence: 0.30,
    notes: "PM guess based on similar products"
  }
}
```

**Report shows**: 70% low-confidence parameters → **High risk**

### Step 2: Data Gathering (Improve Provenance)

```pel
model ProductLaunchV2 {
  // Week 4: Market research complete
  param market_size: Currency<USD> = $68_000_000 {
    source: "gartner_report_2026",
    method: "external_research",
    confidence: 0.70,
    notes: "Gartner: 'SaaS Analytics Market 2026-2030', page 47. TAM estimate for North America."
  }
  
  // Landing page experiment complete
  param conversion_rate: Probability ~ Beta(alpha: 12, beta: 88) {
    source: "landing_page_experiment",
    method: "observed",
    confidence: 0.80,
    notes: "A/B test: 1,200 visitors, 144 conversions (12%). CI: [10.2%, 14.1%]"
  }
}
```

**Report shows**: 30% low-confidence → **Improving**

### Step 3: Production Model (High Confidence)

```pel
model ProductLaunchV3 {
  // Month 3: Post-launch calibration
  param market_size: Currency<USD> = $68_000_000 {
    source: "gartner_report_2026",
    method: "external_research",
    confidence: 0.70,
    notes: "Gartner TAM estimate - validated against actual sales velocity"
  }
  
  param conversion_rate: Probability ~ Beta(alpha: 152, beta: 848) {
    source: "production_analytics",
    method: "observed",
    confidence: 0.90,
    notes: "10,000 visitors, 1,520 conversions over 8 weeks. Stable at 15.2%."
  }
}
```

**Report shows**: 10% low-confidence → **Production-ready**

## Best Practices

### ✅ Do This

1. **Be specific about sources**
   ```pel
   source: "Stripe billing API - MRR endpoint, Jan 1-31 2026"
   ```

2. **Document uncertainty honestly**
   ```pel
   confidence: 0.35,
   notes: "High uncertainty - entering new market with no comparable data"
   ```

3. **Update provenance when data changes**
   ```pel
   // v1: assumption
   confidence: 0.40,
   notes: "Industry benchmark - no internal data (Q4 2025)"
   
   // v2: fitted (3 months later)
   confidence: 0.80,
   notes: "Fitted from 3 months of actual churn data (Jan-Mar 2026)"
   ```

4. **Use notes for action items**
   ```pel
   notes: "TODO: Replace with CAC from marketing dashboard when campaign launches (Q2 2026)"
   ```

### ❌ Don't Do This

1. **Vague sources**
   ```pel
   source: "data"  // ❌ What data? From where?
   ```

2. **Overconfident guesses**
   ```pel
   confidence: 0.90,  // ❌ This is just a guess!
   notes: "Seems reasonable"
   ```

3. **Copy-paste provenance**
   ```pel
   // ❌ Every parameter has identical provenance
   source: "model",
   method: "assumption",
   confidence: 0.50
   ```

4. **Outdated notes**
   ```pel
   notes: "Use Q3 2024 data"  // ❌ It's now 2026!
   ```

## Practical Example: Financial Model with Provenance

```pel
model SaasFinancials2026 {
  // --- High-Confidence Observed Data ---
  
  param current_mrr: Currency<USD> = $285_000 {
    source: "stripe_dashboard",
    method: "observed",
    confidence: 0.98,
    notes: "MRR as of Feb 15, 2026 from Stripe subscription dashboard"
  }
  
  param current_customer_count: Fraction = 472.0 {
    source: "subscription_database",
    method: "observed",
    confidence: 0.99,
    notes: "Active paid subscriptions (Feb 15, 2026)"
  }
  
  // --- Moderate-Confidence Fitted Data ---
  
  param monthly_churn_rate: Probability ~ Beta(alpha: 18, beta: 354) {
    source: "churn_analysis",
    method: "fitted",
    confidence: 0.75,
    notes: "Beta fit to monthly churn over 12 months (Mar 2025 - Feb 2026). Average: 4.8%, 95% CI: [3.2%, 6.7%]"
  }
  
  param customer_growth_rate: Rate per Month ~ Normal(μ=0.18/1mo, σ=0.06/1mo) {
    source: "cohort_analysis",
    method: "fitted",
    confidence: 0.65,
    notes: "Fitted from 9 months of net customer additions. High variance due to seasonal effects."
  }
  
  // --- Low-Confidence Assumptions ---
  
  param price_increase_2027: Fraction = 0.15 {
    source: "pricing_committee",
    method: "assumption",
    confidence: 0.50,
    notes: "Planned 15% price increase for Q1 2027. Board approval pending. Risk: customer backlash, churn spike."
  }
  
  param market_expansion_impact: Fraction ~ Uniform(min: 1.2, max: 2.0) {
    source: "assumption",
    method: "expert_estimate",
    confidence: 0.25,
    notes: "HIGHLY UNCERTAIN - EU market launch (Q3 2026). Multiplier on customer acquisition. Need: market research, localization cost estimates."
  }
  
  // --- Derived Values ---
  
  var arpu: TimeSeries<Currency<USD>>
  arpu[0] = current_mrr / current_customer_count {
    source: "model",
    method: "derived",
    confidence: 0.95,
    notes: "Calculated from MRR and customer count"
  }
}
```

## Quiz: Test Your Understanding

1. **What's the difference between `source: "observed"` and `method: "observed"`?**
   <details>
   <summary>Answer</summary>
   
   - `source`: WHERE the data came from (e.g., "billing_system")
   - `method`: HOW it was obtained (e.g., "observed" = measured directly)
   
   Both can be "observed" but serve different purposes.
   </details>

2. **What confidence score for a wild guess?**
   <details>
   <summary>Answer</summary>
   0.1 - 0.3 (very low confidence). Anything above 0.5 implies you have some evidence.
   </details>

3. **Is this provenance complete?**
   ```pel
   param revenue: Currency<USD> = $100K {
     source: "Stripe",
     method: "observed"
   }
   ```
   <details>
   <summary>Answer</summary>
   ❌ No - missing `confidence` field. PEL will reject with compile error.
   </details>

4. **When should you update provenance?**
   <details>
   <summary>Answer</summary>
   
   - When you get better data (assumption → observed)
   - When timeframe changes (Q4 2025 → Q1 2026)
   - When method changes (expert_estimate → fitted)
   - When confidence changes (new evidence)
   </details>

## Key Takeaways

1. **Provenance is mandatory**: PEL enforces documentation at compile time
2. **Four required fields**: `source`, `method`, `confidence`, (+ optional `notes`)
3. **Confidence is a score**: 0.0 (guess) to 1.0 (certain)
4. **Generate reports**: Track assumption quality over time
5. **Iterate toward high confidence**: Start with assumptions, replace with data

## Next Steps

- **Tutorial 6**: Time-Series Modeling - model values that change over time
- **Tutorial 8**: Calibration - replace assumptions with data-fitted parameters
- **Reference**: See `/docs/model/provenance.md` for complete provenance specification

## Additional Resources

- [Provenance Specification](/docs/model/provenance.md)
- [Assumption Governance Best Practices](/docs/governance/assumptions.md)
- [Confidence Scoring Guidelines](/docs/governance/confidence_scoring.md)

---

**Feedback**: Found an error or want to suggest an improvement? [Open an issue](https://github.com/Coding-Krakken/pel-lang/issues/new).
