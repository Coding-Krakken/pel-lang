# Tutorial 9: Migration from Spreadsheets

## Overview

Most business models today live in **Excel or Google Sheets**. This tutorial provides a step-by-step guide to migrating spreadsheet models to PEL, transforming implicit assumptions into explicit, auditable, type-safe code.

**Time required**: 40 minutes  
**Prerequisites**: Tutorials 1-7  
**Learning outcomes**: 
- Identify migration candidates
- Convert spreadsheet formulas to PEL
- Add types and units to untyped data
- Document assumptions with provenance
- Validate migrated models

## Why Migrate from Spreadsheets?

### Spreadsheet Limitations

| Problem | Impact | How PEL Solves |
|---------|--------|----------------|
| **No types/units** | $100 + 10% = ??? | Type system enforces dimensional correctness |
| **Ghost assumptions** | "Where did 15% come from?" | Mandatory provenance |
| **No version control** | "Final_v3_FINAL.xlsx" | Git-compatible text format |
| **Manual validation** | Hopes you check cells | Automated constraint checking |
| **Hard to audit** | Formulas hidden in cells | Declarative, readable syntax |
| **No uncertainty** | Single-point estimates | Built-in distributions |

### When to Migrate

**Good candidates**:
- ✅ Models you update monthly/quarterly
- ✅ Models shared across teams
- ✅ Models with regulatory/audit requirements
- ✅ Complex models with many assumptions
- ✅ Models that feed decisions (budgets, hiring, pricing)

**Not worth migrating** (yet):
- ❌ One-off analysis
- ❌ Simple arithmetic (no logic)
- ❌ Data tables (use CSV input instead)
- ❌ Visual dashboards (use PEL output in BI tools)

## Migration Workflow

```
┌─────────────────┐
│ 1. Audit Excel  │  Understand structure, identify assumptions
└────────┬────────┘
         │
┌────────▼────────┐
│ 2. Extract Data │  Separate constants, formulas, time series
└────────┬────────┘
         │
┌────────▼────────┐
│ 3. Add Types    │  Convert numbers → Currency, Rate, etc.
└────────┬────────┘
         │
┌────────▼────────┐
│ 4. Add Provenance│ Document sources, methods, confidence
└────────┬────────┘
         │
┌────────▼────────┐
│ 5. Test & Validate│ Ensure PEL = Excel (deterministic mode)
└────────┬────────┘
         │
┌────────▼────────┐
│ 6. Enhance      │  Add uncertainty, constraints, stdlib
└─────────────────┘
```

## Example: SaaS Financial Model

### Step 1: Audit the Excel Model

**Original spreadsheet** (`SaaS_Model_2026.xlsx`):

**Sheet 1: Inputs**

| Parameter | Value | Note |
|-----------|-------|------|
| Initial MRR | $50,000 | From Stripe |
| Monthly Growth | 15% | Guess |
| Churn Rate | 5% | Industry avg |
| COGS % | 25% | |
| OpEx | $40,000 | Budget |

**Sheet 2: Time Series Calculations**

| Month | MRR | Formula | COGS | OpEx | Profit |
|-------|-----|---------|------|------|--------|
| 0 | $50,000 | (input) | $12,500 | $40,000 | -$2,500 |
| 1 | $57,500 | `=B2*1.15*(1-0.05)` | $14,375 | $40,000 | $3,125 |
| 2 | $66,125 | `=B3*1.15*(1-0.05)` | $16,531 | $40,000 | $9,594 |

**Observations**:
- 5 parameters (Initial MRR, Growth, Churn, COGS%, OpEx)
- 1 time series (MRR grows each month)
- Formulas combine growth and churn: `MRR[t+1] = MRR[t] * 1.15 * 0.95`
- No documentation of assumptions
- No units (is 15% monthly or annual?)
- No uncertainty modeling

### Step 2: Extract Data

**Constants** (don't change over time):
- `initial_mrr = $50,000`
- `monthly_growth_rate = 15% per month` (assume monthly from context)
- `monthly_churn_rate = 5%`
- `cogs_percentage = 25%`
- `monthly_opex = $40,000`

**Time series** (change over time):
- `mrr[t]` - Monthly Recurring Revenue
- `cogs[t]` - Cost of Goods Sold
- `profit[t]` - Operating Profit

**Formulas**:
- `mrr[t+1] = mrr[t] * (1 + growth_rate) * (1 - churn_rate)`
- `cogs[t] = mrr[t] * cogs_percentage`
- `profit[t] = mrr[t] - cogs[t] - opex`

### Step 3: Add Types

Convert raw numbers → typed PEL:

```pel
model SaaS_Model_V1 {
  // --- Parameters (with types) ---
  
  // ❌ Excel: "50000" (no units)
  // ✅ PEL: Explicit currency type
  param initial_mrr: Currency<USD> = $50_000
  
  // ❌ Excel: "0.15" (monthly? annual?)
  // ✅ PEL: Rate with explicit time unit
  param monthly_growth_rate: Rate per Month = 0.15 / 1mo
  
  // ❌ Excel: "0.05" (dimensionless)
  // ✅ PEL: Probability type (bounded [0,1])
  param monthly_churn_rate: Probability = 0.05
  
  // Dimensionless percentage
  param cogs_percentage: Fraction = 0.25
  
  // Currency with time unit
  param monthly_opex: Currency<USD> = $40_000
  
  // --- Time Series ---
  
  var mrr: TimeSeries<Currency<USD>>
  mrr[0] = initial_mrr
  mrr[t+1] = mrr[t] * (1 + monthly_growth_rate) * (1 - monthly_churn_rate)
  
  var cogs: TimeSeries<Currency<USD>>
  cogs[t] = mrr[t] * cogs_percentage
  
  var profit: TimeSeries<Currency<USD>>
  profit[t] = mrr[t] - cogs[t] - monthly_opex
}
```

**Benefits**:
- Type checker catches `$50K + 15%` errors
- Units are self-documenting
- No ambiguity about monthly vs. annual rates

### Step 4: Add Provenance

Document where assumptions came from:

```pel
model SaaS_Model_V2 {
  // --- Well-Provenance Parameters ---
  
  param initial_mrr: Currency<USD> = $50_000 {
    source: "stripe_dashboard",
    method: "observed",
    confidence: 0.98,
    notes: "MRR as of Feb 1, 2026 from Stripe billing"
  }
  
  param monthly_growth_rate: Rate per Month = 0.15 / 1mo {
    source: "assumption",
    method: "expert_estimate",
    confidence: 0.40,
    notes: "Excel: 'Guess' - NO DATA. Replace with historical fit ASAP."
  }
  
  param monthly_churn_rate: Probability = 0.05 {
    source: "industry_benchmarks",
    method: "benchmark",
    confidence: 0.30,
    notes: "Excel: 'Industry avg' - SaaS Metrics Report 2025. Not specific to our product."
  }
  
  param cogs_percentage: Fraction = 0.25 {
    source: "finance_team",
    method: "observed",
    confidence: 0.85,
    notes: "Trailing 6-month average COGS/Revenue ratio"
  }
  
  param monthly_opex: Currency<USD> = $40_000 {
    source: "budget_2026",
    method: "assumption",
    confidence: 0.80,
    notes: "Approved budget - excludes COGS"
  }
  
  // ... (time series same as V1)
}
```

**Benefits**:
- Audit trail for every assumption
- Low confidence scores highlight risks
- Notes flag action items ("replace with data")

### Step 5: Test & Validate

Compare PEL output to Excel:

```bash
# Compile and run deterministic mode
pel compile saas_model_v2.pel
pel run saas_model_v2.ir.json --mode deterministic --steps 12 -o pel_output.json
```

**Validation checklist**:

| Month | Excel MRR | PEL MRR | Match? |
|-------|-----------|---------|--------|
| 0 | $50,000 | $50,000 | ✅ |
| 1 | $57,500 | $57,500 | ✅ |
| 2 | $66,125 | $66,125 | ✅ |
| 12 | $182,450 | $182,450 | ✅ |

**If values don't match**:
1. Check formula translation (did you correctly convert Excel logic?)
2. Verify rounding (Excel may use different precision)
3. Check time indexing (Excel row 1 = PEL t=0 or t=1?)

### Step 6: Enhance Beyond Excel

Now add features Excel can't provide:

#### 6a. Add Uncertainty

```pel
model SaaS_Model_V3 {
  // Replace point estimates with distributions
  
  param monthly_growth_rate: Rate per Month 
    ~ Normal(μ=0.15/1mo, σ=0.05/1mo) {
      source: "assumption",
      method: "expert_estimate",
      confidence: 0.40,
      notes: "Range: 10-20% growth. High uncertainty - need data."
    }
  
  param monthly_churn_rate: Probability 
    ~ Beta(alpha: 5, beta: 95) {
      source: "industry_benchmarks",
      method: "benchmark",
      confidence: 0.30,
      notes: "Beta distribution centered at 5%, range 3-7%"
    }
  
  // ... rest of model
}
```

**Run Monte Carlo**:
```bash
pel run saas_model_v3.ir.json --mode monte_carlo --samples 10000 -o mc_output.json
```

**Result**:
```json
{
  "profit[12]": {
    "mean": "$95,000",
    "median": "$92,000",
    "p5": "$45,000",   // Pessimistic case
    "p95": "$145,000"  // Optimistic case
  }
}
```

**Insight**: Excel showed one number ($95K profit). PEL shows a **range** - you're 90% confident profit will be between $45K-$145K.

#### 6b. Add Constraints

```pel
model SaaS_Model_V4 {
  // ... (parameters from V3)
  
  // --- Time Series ---
  var mrr: TimeSeries<Currency<USD>>
  mrr[0] = initial_mrr
  mrr[t+1] = mrr[t] * (1 + monthly_growth_rate) * (1 - monthly_churn_rate)
  
  var cogs: TimeSeries<Currency<USD>>
  cogs[t] = mrr[t] * cogs_percentage
  
  var profit: TimeSeries<Currency<USD>>
  profit[t] = mrr[t] - cogs[t] - monthly_opex
  
  // --- Constraints (Excel can't do this automatically) ---
  
  constraint profitability_by_month_3 {
    profit[3] > $0
      with severity(warning)
      with message("Not profitable by month 3: profit = {profit[3]}")
  }
  
  constraint sustainable_growth {
    monthly_growth_rate > monthly_churn_rate
      with severity(fatal)
      with message("Churn exceeds growth - MRR will decline")
  }
  
  constraint reasonable_cogs {
    cogs_percentage >= 0.10 && cogs_percentage <= 0.50
      with severity(fatal)
      with message("COGS% outside realistic range [10%, 50%]")
  }
}
```

#### 6c. Use Stdlib Functions

```pel
model SaaS_Model_V5 {
  // ... (parameters from V4)
  
  // --- Unit Economics (stdlib) ---
  
  param customer_count: Fraction = 500.0 {
    source: "crm",
    method: "observed",
    confidence: 0.99
  }
  
  var monthly_arpu: TimeSeries<Currency<USD>>
  monthly_arpu[t] = mrr[t] / customer_count
  
  var ltv: Currency<USD>
    = ltv_simple(monthly_arpu[0], monthly_churn_rate)
  // Reuses stdlib logic
  
  param cac: Currency<USD> = $450 {
    source: "marketing",
    method: "derived",
    confidence: 0.70
  }
  
  var ltv_cac_ratio: Fraction
    = ltv_to_cac_ratio(ltv, cac)
  
  // --- Constraint using stdlib output ---
  constraint healthy_unit_economics {
    ltv_cac_ratio >= 3.0
      with severity(warning)
      with message("LTV:CAC ratio {ltv_cac_ratio} below healthy threshold (3.0)")
  }
}
```

## Common Migration Patterns

### Pattern 1: Excel IF → PEL if-then-else

**Excel**:
```
=IF(A1>100, A1*1.2, A1*0.8)
```

**PEL**:
```pel
var result = if value > 100.0
               then value * 1.2
               else value * 0.8
```

### Pattern 2: Excel VLOOKUP → PEL conditionals or params

**Excel** (price tiers):
```
=VLOOKUP(A1, PriceTable, 2, TRUE)
```

**PEL**:
```pel
var price: Currency<USD>
price = if volume <= 100.0 then $10
        else if volume <= 500.0 then $8
        else $6
```

Or use parameters:
```pel
param tier1_price: Currency<USD> = $10 { ... }
param tier2_price: Currency<USD> = $8 { ... }
param tier3_price: Currency<USD> = $6 { ... }
```

### Pattern 3: Excel Row-by-Row → Time Series

**Excel**:
```
B2: =B1 * 1.10    (Month 1)
B3: =B2 * 1.10    (Month 2)
...
```

**PEL**:
```pel
var revenue: TimeSeries<Currency<USD>>
revenue[0] = $100_000
revenue[t+1] = revenue[t] * 1.10
```

### Pattern 4: Excel Named Ranges → PEL Parameters

**Excel**:
```
Define Name: "GrowthRate" = 0.15
Formula: =Revenue * GrowthRate
```

**PEL**:
```pel
param growth_rate: Rate per Month = 0.15 / 1mo { ... }
var new_revenue = revenue * (1 + growth_rate)
```

### Pattern 5: Excel Data Tables → CSV Import (Calibration)

**Excel** (historical data in rows 1-24):
```
Month | Actual Revenue
1     | $105,000
2     | $112,000
...
```

**PEL** (calibrate from CSV):
```bash
# Store data as CSV
cat > revenue_history.csv << EOF
month,revenue
1,105000
2,112000
...
EOF

# Calibrate model (Tutorial 8)
pel calibrate model.ir.json \
  --csv revenue_history.csv \
  --fit growth_rate \
  -o calibrated_model.ir.json
```

## Excel → PEL Translation Cheat Sheet

| Excel Feature | PEL Equivalent |
|---------------|----------------|
| Cell reference `A1` | Parameter or variable name |
| `=B1*1.15` | `var result = value * 1.15` |
| `=SUM(A1:A12)` | `sum(array)` or manual loop |
| `=IF(A1>0, A1, 0)` | `if x > 0 then x else 0` |
| `=AVERAGE(A1:A12)` | `(sum(array) / length(array))` |
| `=VLOOKUP(...)` | Conditional logic or parameter lookup |
| Data Validation | Constraints (`constraint { ... }`) |
| Conditional Formatting | Not needed (constraints auto-validate) |
| Named Ranges | `param` declarations |
| Row-by-row formulas | `TimeSeries` with recurrence relations |
| Monte Carlo add-in | Built-in: `--mode monte_carlo` |

## Migration Checklist

Before declaring migration complete:

- [ ] All Excel inputs converted to `param` with types
- [ ] All Excel formulas converted to `var` calculations
- [ ] All time series use `TimeSeries<T>` syntax
- [ ] All parameters have provenance (`source`, `method`, `confidence`)
- [ ] Deterministic PEL output matches Excel (within rounding)
- [ ] Low-confidence parameters flagged for data collection
- [ ] Constraints added for validation
- [ ] Uncertainty added where appropriate (distributions)
- [ ] Stdlib functions used where applicable
- [ ] Model committed to Git

## Quiz: Test Your Understanding

1. **What Excel feature has no PEL equivalent?**
   <details>
   <summary>Answer</summary>
   Conditional formatting (visual styling). PEL focuses on logic, not presentation. Use constraints instead of cell colors.
   </details>

2. **How do you convert `=A1*0.15` to PEL?**
   <details>
   <summary>Answer</summary>
   ```pel
   var result = value * 0.15
   ```
   Or if it's a growth rate:
   ```pel
   param growth_rate: Rate per Month = 0.15 / 1mo { ... }
   var result = value * growth_rate
   ```
   </details>

3. **What's the PEL equivalent of dragging a formula down 24 rows?**
   <details>
   <summary>Answer</summary>
   Time series with recurrence relation:
   ```pel
   var x: TimeSeries<T>
   x[0] = initial_value
   x[t+1] = f(x[t])
   ```
   </details>

4. **Should you migrate every spreadsheet?**
   <details>
   <summary>Answer</summary>
   No - focus on models that are:
   - Updated regularly
   - Shared across teams
   - Critical for decisions
   - Complex with many assumptions
   
   Skip one-off calculations and simple data tables.
   </details>

## Key Takeaways

1. **Migration is a 6-step process**: Audit → Extract → Type → Provenance → Validate → Enhance
2. **Always validate**: PEL deterministic output should match Excel
3. **Add provenance first**: Document assumptions before adding uncertainty
4. **Enhance beyond Excel**: Use distributions, constraints, stdlib
5. **Use Git**: Version control your models (impossible with `.xlsx`)

## Next Steps

- **Tutorial 10**: Production Deployment - CI/CD for PEL models
- **Tutorial 8**: Calibration - fit distributions to historical data
- **Reference**: See `/docs/MIGRATION_GUIDE.md` for extended examples

## Additional Resources

- [Excel Formula Translation Guide](/docs/migration/excel_formula_reference.md)
- [Migration Case Studies](/docs/migration/case_studies.md)
- [Common Migration Gotchas](/docs/troubleshooting/migration_errors.md)

---

**Feedback**: Found an error or want to suggest an improvement? [Open an issue](https://github.com/Coding-Krakken/pel-lang/issues/new).
