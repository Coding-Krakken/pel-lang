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

## Advanced Migration Techniques

### Complex Excel Formulas Translation

#### IF() Statements

Excel:
```excel
=IF(B2>10000, B2*0.2, B2*0.3)
```

PEL:
```pel
var result = if customers > 10_000
  then revenue * 0.2
  else revenue * 0.3
```

#### Nested IF()

Excel:
```excel
=IF(B2<5000, "Small", IF(B2<20000, "Medium", "Large"))
```

PEL:
```pel
var segment = if customers < 5_000
  then "Small"
  else if customers < 20_000
    then "Medium"
    else "Large"
```

#### SUMIF() and Array Formulas

Excel:
```excel
=SUMIF(A2:A100, ">100", B2:B100)
```

PEL (using time series):
```pel
var filtered_sum = sum(
  revenue[t] for t in 0..99 if customers[t] > 100
)
```

#### VLOOKUP() Replacement

Excel:
```excel
=VLOOKUP(A2, PricingTable, 2, FALSE)
```

PEL (using parameters or CSVs):
```pel
// Option 1: Hard-code lookup table
param pricing_tier_1: Currency<USD> = $99
param pricing_tier_2: Currency<USD> = $199
param pricing_tier_3: Currency<USD> = $399

var price = if tier == "basic"
  then pricing_tier_1
  else if tier == "pro"
    then pricing_tier_2
    else pricing_tier_3

// Option 2: Import from CSV (future feature)
// import pricing_table from "pricing.csv"
// var price = lookup(pricing_table, tier)
```

#### NPV() and IRR()

Excel:
```excel
=NPV(10%, B2:B10)
```

PEL:
```pel
use stdlib.cashflow

var project_npv = npv(
  cash_flows: [revenue[t] - costs[t] for t in 0..8],
  discount_rate: 0.10
)
```

### Circular References and Iteration

Excel often has circular references (e.g., debt depends on interest, interest depends on debt).

**Excel approach** (with iteration enabled):
```excel
// Cell A1: Debt
=B1*12  // Interest × 12 months

// Cell B1: Annual Interest
=A1*0.05  // Debt × 5% rate
```

**PEL approach** (break circular dependency):

```pel
model DebtModel {
  // Option 1: Iterative solver (manual)
  param initial_debt_guess: Currency<USD> = $1_000_000
  param interest_rate: Probability = 0.05
  
  var debt: Currency<USD> = initial_debt_guess
  var annual_interest: Currency<USD> = debt * interest_rate
  
  // Debt = Interest × 20 (solve: D = 0.05D × 20 → D = D)
  // This creates circular dependency - must refactor
  
  // Option 2: Explicit formula (break circularity)
  // If Debt = f(Interest) and Interest = g(Debt),
  // solve algebraically: D = 0.05D × 20 → D = D (trivial)
  // If more complex, solve manually:
  
  // Example: Debt = Operating_Cash - Interest, Interest = Debt × 0.05
  // Substitute: Debt = OC - (Debt × 0.05)
  // Solve: Debt = OC / 1.05
  
  param operating_cash: Currency<USD> = $1_000_000
  var debt_solved: Currency<USD> = operating_cash / 1.05
  var interest_solved: Currency<USD> = debt_solved * interest_rate
}
```

**Best practice**: Refactor circular dependencies into explicit time-series or algebraic solutions.

### Migrating Scenario Analysis

Excel scenario manager:
```excel
// Scenario 1: Base Case
Revenue_Growth = 15%
Churn_Rate = 5%

// Scenario 2: Pessimistic
Revenue_Growth = 5%
Churn_Rate = 10%

// Scenario 3: Optimistic
Revenue_Growth = 25%
Churn_Rate = 3%
```

PEL approach:

```pel
// Option 1: Multiple model files
// base_case.pel
param revenue_growth: Rate per Month = 0.15 / 1mo
param churn_rate: Probability = 0.05

// pessimistic.pel
param revenue_growth: Rate per Month = 0.05 / 1mo
param churn_rate: Probability = 0.10

// optimistic.pel
param revenue_growth: Rate per Month = 0.25 / 1mo
param churn_rate: Probability = 0.03

// Option 2: Distributions (Monte Carlo replaces scenarios)
param revenue_growth: Rate per Month ~ Normal(μ=0.15/1mo, σ=0.05/1mo)
param churn_rate: Probability ~ Beta(alpha: 10, beta: 190)
// Monte Carlo samples thousands of scenarios automatically

// Option 3: Command-line overrides
// pel run model.ir.json --set revenue_growth=0.05/1mo --set churn_rate=0.10
```

### Migrating Data Tables (Goal Seek)

Excel Data Table:
```
        | CAC=$400 | CAC=$500 | CAC=$600
--------|----------|----------|----------
Churn=3%|  $4,000  |  $5,000  |  $6,000
Churn=5%|  $2,400  |  $3,000  |  $3,600
Churn=7%|  $1,714  |  $2,143  |  $2,571
```

PEL approach (sensitivity sweep):

```bash
#!/bin/bash
# sensitivity_sweep.sh

for cac in 400 500 600; do
  for churn in 0.03 0.05 0.07; do
    echo "CAC=$cac, Churn=$churn"
    pel run model.ir.json \
      --set cac=$cac \
      --set churn_rate=$churn \
      | jq '.variables.ltv.deterministic'
  done
done
```

### Handling Macros (VBA Code)

Excel macros cannot be directly migrated. Options:

1. **Rewrite logic in PEL**:
   ```vba
   ' VBA: Custom copmputation
   Function CustomMetric(revenue As Double, costs As Double) As Double
     CustomMetric = (revenue - costs) / revenue * 100
   End Function
   ```
   
   ```pel
   // PEL equivalent
   var custom_metric: Fraction = (revenue - costs) / revenue
   ```

2. **Python/external scripts** for data preprocessing:
   ```python
   # preprocess.py
   import pandas as pd
   
   df = pd.read_excel('raw_data.xlsx')
   df['computed_field'] = df['revenue'] * 1.15
   df.to_csv('cleaned_data.csv')
   ```
   
   Then import CSV into PEL model.

3. **API integration** for complex external logic:
   ```bash
   # Call external service for complex calculation
   curl -X POST https://api.example.com/compute \
     -d '{"revenue": 100000}' > result.json
   
   # Use result in PEL model
   # (future: PEL may support API calls natively)
   ```

## Migration Case Studies

### Case Study 1: Revenue Forecast Model

**Original Excel** (simplified):

| Month | Customers | ARPU  | Revenue  |
|-------|-----------|-------|----------|
| Jan   | 1,000     | $50   | $50,000  |
| Feb   | =A2\*1.1  | =$50  | =B3\*C3  |
| Mar   | =A3\*1.1  | =$50  | =B4\*C4  |
| ...   | ...       | ...   | ...      |

**Migration steps**:

1. **Audit**:
   - Growth rate: 10%/month (hard-coded in formula)
   - ARPU: $50 (fixed reference)
   - No error handling, no uncertainty

2. **Extract**:
   ```pel
   model RevenueForecas

t {
     param initial_customers: Fraction = 1000.0
     param growth_rate: Probability = 0.10
     param arpu: Currency<USD> = $50
   }
   ```

3. **Type**:
   ```pel
   var customers: TimeSeries<Fraction>
   var revenue: TimeSeries<Currency<USD>>
   ```

4. **Provenance**:
   ```pel
   param initial_customers: Fraction = 1000.0 {
     source: "crm_export_jan_2026",
     method: "observed",
     confidence: 0.99
   }
   
   param growth_rate: Probability = 0.10 {
     source: "marketing_estimate",
     method: "assumption",
     confidence: 0.50,
     notes: "Based on Q4 2025 trend, but unvalidated"
   }
   
   param arpu: Currency<USD> = $50 {
     source: "billing_system_avg_jan_2026",
     method: "observed",
     confidence: 0.95
   }
   ```

5. **Validate**:
   ```pel
   customers[0] = initial_customers
   customers[t+1] = customers[t] * (1 + growth_rate)
   
   revenue[t] = customers[t] * arpu
   ```
   
   ```bash
   pel compile model.pel -o model.ir.json
   pel run model.ir.json --mode deterministic --trace revenue
   ```
   
   Compare with Excel:
   ```
   t=0: PEL=$50K, Excel=$50K ✅
   t=1: PEL=$55K, Excel=$55K ✅
   t=2: PEL=$60.5K, Excel=$60.5K ✅
   ```

6. **Enhance**:
   ```pel
   // Add uncertainty
   param growth_rate: Probability ~ Beta(alpha: 10, beta: 90) {
     source: "historical_growth_range",
     method: "fitted",
     confidence: 0.70,
     notes: "Fitted to 12 months of data: mean=10%, range=[5%, 18%]"
   }
   
   // Add constraint
   constraint reasonable_growth {
     revenue[t] <= $10_000_000
       with severity(warning)
       with message("Revenue exceeds $10M at t={t}, validate assumptions")
   }
   
   // Add churn
   param churn_rate: Probability = 0.05 {
     source: "analytics",
     method: "observed",
     confidence: 0.85
   }
   
   customers[t+1] = customers[t] * (1 + growth_rate - churn_rate)
   ```

### Case Study 2: Cash Flow Statement

**Original Excel**:

| Line Item                 | Jan     | Feb     | Mar     |
|---------------------------|---------|---------|-------|
| Revenue                   | $100K   | $105K   | $110K |
| COGS                      | $30K    | $31.5K  | $33K  |
| Gross Profit              | $70K    | $73.5K  | $77K  |
| Operating Expenses        | $60K    | $60K    | $60K  |
| EBITDA                    | $10K    | $13.5K  | $17K  |
| Cash (Beginning)          | $500K   | $510K   | $523.5K |
| Cash (Ending)             | $510K   | $523.5K | $540.5K |

**PEL migration**:

```pel
model CashFlowStatement {
  // Revenue assumption
  param initial_revenue: Currency<USD> = $100_000 {
    source: "stripe_jan_2026",
    method: "observed",
    confidence: 0.99
  }
  
  param revenue_growth: Rate per Month = 0.05 / 1mo {
    source: "sales_forecast",
    method: "assumption",
    confidence: 0.60
  }
  
  var revenue: TimeSeries<Currency<USD>>
  revenue[0] = initial_revenue
  revenue[t+1] = revenue[t] * (1 + revenue_growth)
  
  // COGS (30% of revenue)
  param cogs_margin: Probability = 0.30 {
    source: "finance_records",
    method: "observed",
    confidence: 0.95
  }
  
  var cogs: TimeSeries<Currency<USD>>
  cogs[t] = revenue[t] * cogs_margin
  
  // Gross profit
  var gross_profit: TimeSeries<Currency<USD>>
  gross_profit[t] = revenue[t] - cogs[t]
  
  // Operating expenses (fixed)
  param opex: Currency<USD> = $60_000 / 1mo {
    source: "accounting",
    method: "observed",
    confidence: 0.99
  }
  
  var operating_expenses: TimeSeries<Currency<USD>>
  operating_expenses[t] = opex
  
  // EBITDA
  var ebitda: TimeSeries<Currency<USD>>
  ebitda[t] = gross_profit[t] - operating_expenses[t]
  
  // Cash balance
  param initial_cash: Currency<USD> = $500_000 {
    source: "bank_statement_dec_2025",
    method: "observed",
    confidence: 1.0
  }
  
  var cash_balance: TimeSeries<Currency<USD>>
  cash_balance[0] = initial_cash
  cash_balance[t+1] = cash_balance[t] + ebitda[t]
  
  // Constraint: Cash never negative
  constraint solvency {
    cash_balance[t] >= $0
      with severity(fatal)
      with message("Cash negative at t={t}: {cash_balance[t]}")
  }
}
```

## Common Migration Pitfalls

### Pitfall 1: Hidden Assumptions

**Problem**: Excel formulas hide assumptions.

```excel
=B2*1.15  // What is 1.15? Growth? Markup? Tax?
```

**Solution**: Make explicit in PEL with provenance.

```pel
param growth_rate: Probability = 0.15 {
  source: "marketing_plan_q1_2026",
  method: "assumption",
  confidence: 0.60,
  notes: "15% monthly customer growth target"
}

var next_customers: Fraction = current_customers * (1 + growth_rate)
```

### Pitfall 2: Inconsistent Unit

**Problem**: Excel mixes units freely.

```excel
=A1+B1  // Is A1 in $ and B1 in %? Excel doesn't check.
```

**Solution**: PEL type system enforces correctness.

```pel
var total = $100 + 0.15  // ❌ Compilation error
var total = $100 * (1 + 0.15)  // ✅ Correct
```

### Pitfall 3: Copy-Paste Errors

**Problem**: Dragging formulas breaks references.

```excel
// Intended: =A$2*B2 (lock row 2)
// Actual after drag: =A4*B4 (oops, row isn't locked)
```

**Solution**: PEL has no copy-paste—formulas are explicit.

```pel
var revenue[t] = customers[t] * arpu  // No dragging, no errors
```

### Pitfall 4: Version Chaos

**Problem**: Excel files proliferate.

```
model_v1.xlsx
model_v2_final.xlsx
model_v2_final_UPDATED.xlsx
model_FEB_2026_approved.xlsx
```

**Solution**: Use Git.

```bash
git init
git add model.pel
git commit -m "Initial model"

# Later
git add model.pel
git commit -m "Updated growth rate to 12%"

# View history
git log --oneline
# 3a2f1b4 Updated growth rate to 12%
# c7e8d92 Initial model
```

## Migration Validation Checklist

☐ **Output Match**: PEL deterministic mode == Excel outputs (within 0.1%)
☐ **Provenance Complete**: All parameters have source/method/confidence
☐ **Types Correct**: No mixing currencies, fractions, rates
☐ **Constraints Added**: Business rules enforced (cash ≥ 0, etc.)
☐ **Git Initialized**: Model under version control
☐ **Documentation**: README explains model purpose and assumptions
☐ **Tests Written**: At least one regression test
☐ **Uncertainty Modeled**: Distributions for key uncertain parameters

## Automated Migration Tools (Future)

While not yet available, future PEL tooling may include:

```bash
# Hypothetical Excel importer
pel import model.xlsx --output model.pel --auto-type

# Would generate:
# - Parameter extraction
# - Basic type inference
# - Provenance stubs (to be filled in)
# - Time-series detection
```

Until then, migration is manual—but worth the investment for critical models.

## Practice Exercises

### Exercise 1: Migrate Simple Growth

Excel:
```
| Month | Customers |
|-------|---------- |
| Jan   | 100       |
| Feb   | =A2*1.10  |
| Mar   | =A3*1.10  |
```

**Task**: Migrate to PEL with provenance.

<details>
<summary>Solution</summary>

```pel
model CustomerGrowth {
  param initial_customers: Fraction = 100.0 {
    source: "crm_jan_2026",
    method: "observed",
    confidence: 0.99
  }
  
  param growth_rate: Probability = 0.10 {
    source: "sales_target",
    method: "assumption",
    confidence: 0.50
  }
  
  var customers: TimeSeries<Fraction>
  customers[0] = initial_customers
  customers[t+1] = customers[t] * (1 + growth_rate)
}
```
</details>

### Exercise 2: Translate VLOOKUP

Excel:
```excel
=VLOOKUP(A2, $E$2:$F$5, 2, FALSE)
```

Where lookup table is:
```
Tier   | Price
-------|-------
Basic  | $49
Pro    | $99
Enterprise | $299
```

**Task**: Implement in PEL.

<details>
<summary>Solution</summary>

```pel
param tier: String = "Pro" {
  source: "customer_record",
  method: "observed",
  confidence: 1.0
}

var price: Currency<USD> = 
  if tier == "Basic" then $49
  else if tier == "Pro" then $99
  else if tier == "Enterprise" then $299
  else $0  // Default
```
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
