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

## Advanced Provenance Techniques

### Provenance Inheritance and Transformation Rules

When deriving variables, how does provenance propagate?

```pel
model ProvenanceInheritance {
  param monthly_revenue: Currency<USD> = $100_000 {
    source: "stripe_dashboard",
    method: "observed",
    confidence: 0.99,
    notes: "January 2026 actual MRR"
  }
  
  param churn_rate: Probability = 0.05 {
    source: "analytics_cohort_analysis",
    method: "fitted",
    confidence: 0.85,
    notes: "3-month rolling average, n=2,500 customers"
  }
  
  // Derived variable: LTV
  var ltv: Currency<USD> = monthly_revenue / churn_rate {
    // Provenance is derived automatically:
    // - source: combination of parent sources
    // - method: "derived"
    // - confidence: min(0.99, 0.85) = 0.85 (weakest link)
    // - note: Auto-generated dependency graph
  }
}
```

**Rule**: Derived variable confidence ≤ min(confidence of inputs).

**Manual override with justification**:

```pel
var ltv: Currency<USD> = monthly_revenue / churn_rate {
  source: "ltv_calculation",
  method: "derived",
  confidence: 0.80,  // Lower than inputs due to formula assumptions
  notes: "LTV = MRR / churn assumes: (1) churn is stable, (2) no expansion revenue, (3) no cohort effects. Each assumption reduces confidence by ~5%."
}
```

### Multi-Source Provenance

When combining data from multiple sources:

```pel
model BlendedData {
  // Source 1: CRM system
  param customers_crm: Fraction = 10_500 {
    source: "salesforce_crm",
    method: "observed",
    confidence: 0.95,
    notes: "Active customer count as of 2026-02-19"
  }
  
  // Source 2: Billing system
  param customers_billing: Fraction = 10_450 {
    source: "stripe_subscriptions",
    method: "observed",
    confidence: 0.99,
    notes: "Active subscription count as of 2026-02-19"
  }
  
  // Reconciliation: Average with documented discrepancy
  var customers_actual: Fraction = (customers_crm + customers_billing) / 2.0 {
    source: "crm_billing_reconciliation",
    method: "derived",
    confidence: 0.85,
    notes: "50-customer discrepancy (0.5%) between CRM and billing. Likely cause: trial users in CRM but not yet billed. Using average as conservative estimate."
  }
}
```

### Time-Based Provenance Decay

Confidence degrades as data ages:

```pel
model ProvenanceDecay {
  param conversion_rate_q4_2025: Probability = 0.12 {
    source: "google_analytics_q4_2025",
    method: "observed",
    confidence: 0.95,
    notes: "Q4 2025 actual conversion rate (holiday season)"
  }
  
  // Q1 2026: Same value, but lower confidence (context changed)
  param conversion_rate_q1_2026: Probability = 0.12 {
    source: "google_analytics_q4_2025",  // Stale source
    method: "assumption",  // No longer observed (now assumed)
    confidence: 0.60,  // Confidence degraded
    notes: "Assumed Q1 2026 rate = Q4 2025 rate. Confidence reduced due to: (1) seasonal effects (holiday vs normal), (2) product changes since Q4, (3) market conditions may differ."
  }
}
```

**Best practice**: Document when and why historical data becomes less reliable.

### Provenance for Calibrated Distributions

When fitting distributions to data:

```pel
model CalibratedProvenance {
  param revenue: Currency<USD> ~ LogNormal(μ=11.5, σ=0.35) {
    source: "revenue_history_2023-2025_csv",
    method: "fitted",
    confidence: 0.85,
    notes: "Fitted LogNormal to 36 months of revenue data (2023-01 to 2025-12) using scipy.stats.lognorm.fit(). Goodness-of-fit: Kolmogorov-Smirnov p=0.42 (good fit). Parameters: μ=11.5 (median=$99K), σ=0.35 (P05=$62K, P95=$157K)."
  }
}
```

**Include in notes**:
- Data source (CSV file, database, API)
- Date range
- Sample size (n=36 above)
- Fitting method (library, algorithm)
- Goodness-of-fit test results
- Interpretation of parameters

### Provenance Audit Trails

Track changes to parameters over time:

```markdown
# assumption_changelog.md

## 2026-01-15: Initial Model
- `param conversion_rate = 0.10` (source: "industry_benchmark", confidence: 0.40)

## 2026-02-10: Updated with A/B test results
- `param conversion_rate = 0.12` (source: "ab_test_week_1-4", confidence: 0.70)
- Note: n=5,000 visitors, 600 conversions, 95% CI: [0.11, 0.13]

## 2026-03-05: Refined with additional cohorts
- `param conversion_rate = 0.115` (source: "ab_test_week_1-8", confidence: 0.85)
- Note: n=12,000 visitors, 1,380 conversions, tighter CI: [0.110, 0.120]
```

Automate with version control:

```bash
# Commit each change to parameter files
git log -p params.pel | grep "param conversion_rate"
```

### Provenance-Driven Model Refinement

**Governance process**:

1. **Identify low-confidence parameters**
   ```bash
   pel compile model.pel --provenance-report -o provenance.json
   cat provenance.json | jq '.parameters | sort_by(.confidence) | .[0:5]'
   ```
   Output:
   ```json
   [
     {"name": "viral_coefficient", "confidence": 0.30},
     {"name": "enterprise_conversion_rate", "confidence": 0.40},
     {"name": "expansion_revenue_rate", "confidence": 0.45},
     {"name": "support_cost_per_customer", "confidence": 0.50},
     {"name": "market_size", "confidence": 0.55}
   ]
   ```

2. **Prioritize data collection**
   - Focus on high-impact, low-confidence parameters
   - Run experiments, query databases, survey customers

3. **Update model with new evidence**
   ```pel
   // Before
   param viral_coefficient: Fraction = 1.5 {
     source: "founder_intuition",
     method: "assumption",
     confidence: 0.30
   }
   
   // After: Ran referral program
   param viral_coefficient: Fraction = 0.65 {
     source: "referral_program_jan_2026",
     method: "observed",
     confidence: 0.80,
     notes: "3,000 customers, 1,950 referrals, 65% viral coefficient"
   }
   ```

4. **Monitor confidence improvement**
   ```bash
   # Track average confidence over time
   pel compile model.pel --provenance-report \
     | jq '.parameters | map(.confidence) | add / length'
   ```
   - Model v1: 0.52 average confidence
   - Model v2: 0.68 average confidence (+30%)
   - Model v3: 0.79 average confidence (+52% from v1)

## Provenance in Different Organizational Roles

### For Data Analysts

**Responsibility**: Document data transformations clearly.

```pel
param customers: Fraction = 8_450 {
  source: "customers_query_v3.sql",
  method: "derived",
  confidence: 0.90,
  notes: "Query definition: SELECT COUNT(DISTINCT customer_id) FROM subscriptions WHERE status='active' AND created_at < '2026-02-01'. Excludes: trial users, churned accounts, internal test accounts. Last run: 2026-02-19 14:32 UTC."
}
```

**What to include**:
- SQL/code snippet or reference
- Data exclusions/filters
- Timestamp of query execution
- Database/table versions

### For Finance Teams

**Responsibility**: Link to accounting sources, ensure audit trail.

```pel
param q4_2025_revenue: Currency<USD> = $1_245_000 {
  source: "quickbooks_income_statement_q4_2025",
  method: "observed",
  confidence: 0.99,
  notes: "Audited financial statement, line item 'Total Revenue', page 3. Signed by CFO on 2026-01-15. Ref: QB-2025-Q4-REV."
}
```

**What to include**:
- Document reference ID
- Line item number/name
- Sign-off authority (CFO, auditor)
- Auditability (enable external verification)

### For Product Managers

**Responsibility**: Document product assumptions and rationale.

```pel
param feature_adoption_rate: Probability = 0.35 {
  source: "pm_estimate_based_on_similar_feature",
  method: "expert_estimate",
  confidence: 0.50,
  notes: "Estimated based on previous feature launch similarity. Previous feature ('dashboard_v2') had 40% adoption in 6 months. New feature is simpler, so estimating 35% ± 10%. Will measure via analytics after launch."
}
```

**What to include**:
- Analogies to past features
- Adjustment rationale
- Measurement plan (how to validate)

### For Executives/Board

**Responsibility**: High-level strategic assumptions with decision context.

```pel
param market_penetration_target: Probability = 0.05 {
  source: "strategic_plan_2026-2028",
  method: "assumption",
  confidence: 0.60,
  notes: "Board-approved target: Capture 5% of $2B TAM by 2028. Based on: (1) competitor analysis (leader has 12% share), (2) sales capacity model (3-year ramp), (3) product-market fit evidence (NPS 65, 40% WoM growth). Board meeting 2026-01-20, motion approved 7-0."
}
```

**What to include**:
- Strategic context
- Board/committee approval
- Supporting evidence summary
- Decision date

## Confidence Scoring Frameworks

### Framework 1: Evidence-Based Scoring

| Confidence | Evidence Level | Example |
|------------|----------------|---------|
| 0.95 - 1.00 | Audited, certified data | Financial statements, regulatory filings |
| 0.85 - 0.94 | Directly measured, high sample | Analytics (n>1000), A/B tests, transaction logs |
| 0.70 - 0.84 | Measured, moderate sample | Surveys (n=200-1000), cohort analysis |
| 0.50 - 0.69 | Small sample or expert estimate | Pilot program (n<200), SME consensus |
| 0.30 - 0.49 | Weak analogy or single expert | "Similar company did X", founder intuition |
| 0.10 - 0.29 | Guess with minimal basis | "Industry seems to be ~Y%" |
| 0.00 - 0.09 | Pure speculation | Placeholder values |

### Framework 2: Uncertainty Intervals

Confidence derived from statistical precision:

```
95% CI width = high - low
Confidence = 1 - (CI_width / mean)
```

**Example**:
- Mean conversion rate: 0.12
- 95% CI: [0.10, 0.14]
- CI width: 0.04
- Confidence: 1 - (0.04 / 0.12) = 0.67 (67%)

**Interpretation**: Narrower intervals → higher confidence.

### Framework 3: Consensus-Based (Multiple Experts)

```
Confidence = 1 - (std_dev_of_estimates / mean_of_estimates)
```

**Example**:
- 5 experts estimate conversion rate: [0.10, 0.12, 0.11, 0.13, 0.09]
- Mean: 0.11
- Std dev: 0.015
- Confidence: 1 - (0.015 / 0.11) = 0.86 (86%)

**Interpretation**: High agreement → high confidence.

## Governance Workflow Example

### Monthly Assumption Review Meeting

**Agenda**:

1. **Review low-confidence parameters** (< 0.60)
   - Identify 3-5 highest-impact parameters
   - Assign owners to collect better data

2. **Update provenance for changed parameters**
   - Example: Marketing ran new campaign → update CAC

3. **Validate recently updated parameters**
   - Did new data match assumptions?
   - Adjust confidence accordingly

4. **Document decisions**
   - Commit changes to version control
   - Update changelog

**Example meeting notes**:

```markdown
# Assumption Review Meeting - 2026-02-20

## Attendees
- CFO, Head of Analytics, VP Product, Lead Engineer

## Low-Confidence Parameters
1. **viral_coefficient** (0.30) → Assigned to Product (run referral analysis)
2. **enterprise_CAC** (0.40) → Assigned to Sales (pull CRM data)
3. **churn_cohort_2** (0.45) → Assigned to Analytics (fit Beta distribution)

## Updated Parameters (since last meeting)
- **monthly_revenue**: $1.2M → $1.35M (Stripe data, confidence 0.99)
- **conversion_rate**: 0.10 → 0.115 (A/B test complete, confidence 0.85)

## Validation Results
- Predicted Q1 revenue: $3.6M (P50), Actual: $3.9M (within P75, model calibrated well)
- Churn rate forecast: 5% (deterministic), Actual: 4.8% (close, no adjustment needed)

## Action Items
- [ ] Product: Analyze referral data by 2026-03-05
- [ ] Sales: Extract enterprise deal data by 2026-03-10
- [ ] Analytics: Fit churn distribution by 2026-03-12

## Next Meeting
2026-03-20, 2pm PT
```

## Automated Provenance Validation

### Pre-Commit Hooks

Enforce provenance quality before code merges:

```bash
# .git/hooks/pre-commit
#!/bin/bash

# Compile model and check provenance
pel compile model.pel --provenance-report -o /tmp/prov.json

# Check: No parameters have confidence < 0.30
low_conf=$(cat /tmp/prov.json | jq '[.parameters[] | select(.confidence < 0.30)] | length')

if [ "$low_conf" -gt 0 ]; then
  echo "ERROR: $low_conf parameters have confidence < 0.30 (too low)"
  echo "Run: pel compile model.pel --provenance-report | jq '.parameters[] | select(.confidence < 0.30)'"
  exit 1
fi

echo "Provenance validation passed"
exit 0
```

### CI/CD Pipeline Checks

```yaml
# .github/workflows/model-validation.yml
name: Model Provenance Validation

on: [push, pull_request]

jobs:
  provenance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install PEL
        run: pip install pel-lang
      
      - name: Generate Provenance Report
        run: pel compile model.pel --provenance-report -o provenance.json
      
      - name: Check Average Confidence
        run: |
          avg_conf=$(cat provenance.json | jq '.parameters | map(.confidence) | add / length')
          echo "Average confidence: $avg_conf"
          
          # Fail if avg confidence < 0.60
          if (( $(echo "$avg_conf < 0.60" | bc -l) )); then
            echo "ERROR: Average confidence too low ($avg_conf < 0.60)"
            exit 1
          fi
      
      - name: Upload Provenance Report
        uses: actions/upload-artifact@v3
        with:
          name: provenance-report
          path: provenance.json
```

## Provenance Report Examples

### HTML Report Template

```html
<!-- provenance_report.html -->
<!DOCTYPE html>
<html>
<head>
  <title>Model Provenance Report</title>
  <style>
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid black; padding: 8px; text-align: left; }
    .high-conf { background-color: #d4edda; }
    .med-conf { background-color: #fff3cd; }
    .low-conf { background-color: #f8d7da; }
  </style>
</head>
<body>
  <h1>Provenance Report: SaaS Revenue Model</h1>
  <p>Generated: 2026-02-20 14:30 UTC</p>
  <p>Model Version: v2.3.1</p>
  
  <h2>Summary Statistics</h2>
  <ul>
    <li>Total Parameters: 42</li>
    <li>Average Confidence: 0.72</li>
    <li>High Confidence (≥0.80): 18 (43%)</li>
    <li>Medium Confidence (0.50-0.79): 20 (48%)</li>
    <li>Low Confidence (<0.50): 4 (9%)</li>
  </ul>
  
  <h2>Parameter Details</h2>
  <table>
    <tr>
      <th>Parameter</th>
      <th>Value</th>
      <th>Confidence</th>
      <th>Source</th>
      <th>Method</th>
      <th>Notes</th>
    </tr>
    <tr class="high-conf">
      <td>monthly_revenue</td>
      <td>$1,350,000</td>
      <td>0.99</td>
      <td>stripe_dashboard</td>
      <td>observed</td>
      <td>January 2026 MRR</td>
    </tr>
    <tr class="med-conf">
      <td>churn_rate</td>
      <td>0.05</td>
      <td>0.75</td>
      <td>analytics</td>
      <td>fitted</td>
      <td>Beta(95, 1805) from 3-month cohort</td>
    </tr>
    <tr class="low-conf">
      <td>viral_coefficient</td>
      <td>1.5</td>
      <td>0.30</td>
      <td>assumption</td>
      <td>expert_estimate</td>
      <td>⚠️ LOW CONFIDENCE - needs data</td>
    </tr>
    <!-- ... more rows ... -->
  </table>
  
  <h2>Recommendations</h2>
  <ul class="low-conf">
    <li><strong>viral_coefficient</strong>: Run referral program analysis to measure actual k-factor</li>
    <li><strong>enterprise_CAC</strong>: Extract CRM data for large deal cycles</li>
    <li><strong>expansion_revenue_rate</strong>: Analyze upsell cohorts from billing system</li>
  </ul>
</body>
</html>
```

## Practice Exercises

### Exercise 1: Write Complete Provenance

Add provenance to this parameter:

```pel
param monthly_churn_rate: Probability = 0.048
```

**Requirements**:
- Data comes from your analytics system
- Based on last 90 days
- 2,000 customers, 96 churned
- You're fairly confident in this number

<details>
<summary>Solution</summary>

```pel
param monthly_churn_rate: Probability = 0.048 {
  source: "google_analytics_cohort_analysis_2025-11_to_2026-01",
  method: "observed",
  confidence: 0.90,
  notes: "96 churned out of 2,000 customers over 90-day period (Nov 2025 - Jan 2026). Churn rate = 96/2000 = 4.8%. High confidence due to large sample size and recent data."
}
```
</details>

### Exercise 2: Assess Confidence

An expert estimates conversion rate will be "around 12%, give or take 5%".

**Question**: What confidence score would you assign?

<details>
<summary>Answer</summary>

**Confidence: 0.40-0.50** (weak expert estimate)

**Rationale**:
- No data, just expert opinion → Not observed
- Wide uncertainty (±5% = ±42% relative error) → Low precision
- Single source (one expert) → No validation
- "Give or take" suggests low certainty

**Better approach**: Get estimates from 3-5 experts, compute consensus.
</details>

### Exercise 3: Provenance Audit

You inherit this code:

```pel
param revenue: Currency<USD> = $500_000 {
  source: "spreadsheet",
  method: "observed",
  confidence: 0.95
}
```

**Task**: What questions would you ask to validate this provenance?

<details>
<summary>Answer</summary>

1. **Which spreadsheet?** (file name, version, sheet name, cell reference)
2. **Who created it?** (author, reviewer, approver)
3. **When was it last updated?** (date, is it current?)
4. **What's the data source for the spreadsheet?** (where did $500K come from? Billing system? Bank statement?)
5. **Why confidence=0.95?** (seems high for "spreadsheet" - was it reconciled with financial system?)
6. **Is it audited?** (reviewed by finance/accounting?)

**Red flags**:
- "spreadsheet" is too vague (not auditable)
- confidence=0.95 seems unjustified for manual data entry

**Recommended fix**:
```pel
param revenue: Currency<USD> = $500_000 {
  source: "stripe_dashboard_mrr_jan_2026",
  method: "observed",
  confidence: 0.99,
  notes: "MRR as of 2026-01-31, verified against Stripe API. Matches financial records. Ref: revenue_q4_2025_report.pdf, page 2."
}
```
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
