# PEL for Complete Beginners - Interactive Tutorial

**No programming experience needed!** This guide teaches you economic modeling step-by-step with real business examples.

---

## What You'll Learn

By the end of this tutorial, you'll be able to:
- ✅ Model your business revenue and costs
- ✅ Forecast hiring and salary budgets
- ✅ Simulate "what if" scenarios with uncertainty
- ✅ Generate professional reports for stakeholders

**Time required:** 60-90 minutes  
**Prerequisites:** None - just copy and paste the commands!

---

## Quick Setup Check

First, let's make sure everything works. Copy and paste this command:

```bash
./pel --version
```

**Expected output:** `PEL 0.1.0`

✅ If you see this, you're ready to go!  
❌ If not, run the setup commands first (see end of this file).

---

## Part 1: Your First Model - A Coffee Shop 🍵

### The Business Scenario

Imagine you own a small coffee shop:
- You currently make **$5,000/month** in revenue
- Your costs are **$3,500/month** (rent, supplies, staff)
- You think you can grow by **8% per month** by getting more customers

**Question:** Will you be profitable in 6 months? In 12 months?

Let's use PEL to find out!

---

### Step 1: Create Your Model File

Copy this entire block and paste it into a new file called `coffee_shop.pel`:

```pel
model CoffeeShop {
  // How much money you make right now
  param current_revenue: Currency<USD> = $5_000 {
    source: "bank_statement_jan_2026",
    method: "observed",
    confidence: 0.95
  }
  
  // Your monthly expenses
  param monthly_costs: Currency<USD> = $3_500 {
    source: "expense_tracker",
    method: "observed",
    confidence: 0.90
  }
  
  // How fast you expect to grow each month
  param growth_rate: Rate per Month = 0.08/1mo {
    source: "marketing_plan",
    method: "assumption",
    confidence: 0.60
  }
  
  // Calculate revenue over time
  var revenue: TimeSeries<Currency<USD>>
  revenue[0] = current_revenue
  revenue[t+1] = revenue[t] * (1 + growth_rate)
  
  // Calculate profit each month
  var profit: TimeSeries<Currency<USD>>
  profit[t] = revenue[t] - monthly_costs
}
```

**What does this mean?**

- `param` = Input numbers you know or estimate
- `var` = Calculated values PEL computes for you
- `Currency<USD>` = Dollar amounts (PEL won't let you accidentally mix currencies!)
- `Rate per Month` = Growth rate (8% = 0.08)
- `TimeSeries` = Values that change over time
- `{source: ...}` = Where this number came from (for audit trail)

---

### Step 2: Check Your Model

Copy and paste this command to check if your model has any typos or errors:

```bash
./pel check coffee_shop.pel
```

**Expected output:**
```
✓ Model 'CoffeeShop' is valid
  Type errors: 0
  Type warnings: 0
  Provenance errors: 0
```

✅ **If you see this:** Great! Move to Step 3.  
❌ **If you see errors:** Check that you copied the model exactly (spelling, brackets, etc.)

---

### Step 3: Compile Your Model

This turns your model into a format the computer can run:

```bash
./pel compile coffee_shop.pel -o coffee_shop.ir.json
```

**Expected output:**
```
✓ Compilation successful!
  Output: coffee_shop.ir.json
  Parameters: 3
  Variables: 2
```

You now have a file called `coffee_shop.ir.json` - this is your compiled model!

---

### Step 4: Run Your Forecast

Let's see what happens over 12 months:

```bash
./pel run coffee_shop.ir.json --mode deterministic --seed 42 -o coffee_results.json
```

**What this does:**
- `--mode deterministic` = Use your exact growth rate (no randomness)
- `--seed 42` = Makes results reproducible
- `-o coffee_results.json` = Saves results to a file

**Expected output:**
```
✓ Execution complete
  Status: success
  Timesteps: 12
```

---

### Step 5: View Your Results

Open the file `coffee_results.json` in any text editor. Look for the `"variables"` section:

```json
"variables": {
  "revenue": [
    5000.0,    // Month 0 (today)
    5400.0,    // Month 1
    5832.0,    // Month 2
    6298.56,   // Month 3
    ...
    10007.92   // Month 12
  ],
  "profit": [
    1500.0,    // Month 0 profit
    1900.0,    // Month 1 profit
    2332.0,    // Month 2 profit
    ...
    6507.92    // Month 12 profit
  ]
}
```

**What you learned:**
- Starting at $5,000/month revenue
- After 12 months at 8% growth: **$10,000/month** revenue
- Your profit grows from $1,500 to **$6,500/month**!

🎉 **Congratulations!** You just built and ran your first economic model!

---

## Part 2: Real World - Subscription Business 📊

### The Business Scenario

You're launching a SaaS (Software as a Service) product:
- **Price:** $50/month per customer
- **Starting customers:** 100
- **Growth:** You expect to add 20 new customers/month
- **Churn:** 5% of customers cancel each month
- **Costs:** $2,000/month in server and support costs

**Question:** How many customers will you have in 6 months? Will you be profitable?

---

### Step 1: Create the Model

Create a file called `saas_business.pel`:

```pel
model SaasGrowth {
  // Price per customer per month
  param price_per_customer: Currency<USD> = $50 {
    source: "pricing_page",
    method: "observed",
    confidence: 1.0
  }
  
  // How many customers you start with
  param initial_customers: Count<Customers> = 100 {
    source: "dashboard_feb_2026",
    method: "observed",
    confidence: 1.0
  }
  
  // New customers each month
  param new_customers_per_month: Count<Customers> = 20 {
    source: "marketing_forecast",
    method: "assumption",
    confidence: 0.70
  }
  
  // Percentage who cancel each month
  param churn_rate: Rate per Month = 0.05/1mo {
    source: "industry_benchmark",
    method: "assumption",
    confidence: 0.60
  }
  
  // Your operating costs
  param monthly_costs: Currency<USD> = $2_000 {
    source: "budget",
    method: "assumption",
    confidence: 0.80
  }
  
  // Calculate customer count over time
  var customers: TimeSeries<Count<Customers>>
  customers[0] = initial_customers
  customers[t+1] = customers[t] + new_customers_per_month - (customers[t] * churn_rate)
  
  // Calculate monthly revenue
  var revenue: TimeSeries<Currency<USD>>
  revenue[t] = customers[t] * price_per_customer
  
  // Calculate profit
  var profit: TimeSeries<Currency<USD>>
  profit[t] = revenue[t] - monthly_costs
}
```

---

### Step 2: Check, Compile, and Run

Copy and paste these three commands one at a time:

**Check:**
```bash
./pel check saas_business.pel
```

**Compile:**
```bash
./pel compile saas_business.pel -o saas_business.ir.json
```

**Run:**
```bash
./pel run saas_business.ir.json --mode deterministic --seed 42 -o saas_results.json
```

---

### Step 3: Analyze Results

Open `saas_results.json` and find:

```json
"customers": [
  100.0,   // Month 0
  115.0,   // Month 1: 100 + 20 new - 5 churned
  129.25,  // Month 2
  142.79,  // Month 3
  ...
]
```

**Key insight:** Even though you lose 5% of customers each month, you're still growing because you add 20 new ones!

---

## Part 3: Adding Uncertainty - "What If" Scenarios 🎲

### The Problem with Fixed Numbers

In the real world, you don't know EXACTLY how many customers you'll get. Maybe you'll get 15, maybe 25. Let's model this **uncertainty**.

---

### Step 1: Model with Uncertainty

Create `saas_uncertain.pel`:

```pel
model SaasWithUncertainty {
  param price_per_customer: Currency<USD> = $50 {
    source: "pricing_page",
    method: "observed",
    confidence: 1.0
  }
  
  param initial_customers: Count<Customers> = 100 {
    source: "dashboard",
    method: "observed",
    confidence: 1.0
  }
  
  // NEW: Uncertain customer acquisition
  // Instead of exactly 20, we think it's between 15-25
  // Most likely 20
  param new_customers_per_month: Count<Customers> = ~Normal(μ=20, σ=3) {
    source: "marketing_forecast",
    method: "fitted",
    confidence: 0.70,
    notes: "Historical data shows average 20, stddev 3"
  }
  
  // NEW: Churn rate with uncertainty
  // We think 5%, but could be 3-7%
  param churn_rate: Rate per Month = ~Normal(μ=0.05/1mo, σ=0.01/1mo) {
    source: "cohort_analysis",
    method: "fitted",
    confidence: 0.65
  }
  
  param monthly_costs: Currency<USD> = $2_000 {
    source: "budget",
    method: "assumption",
    confidence: 0.80
  }
  
  var customers: TimeSeries<Count<Customers>>
  customers[0] = initial_customers
  customers[t+1] = customers[t] + new_customers_per_month - (customers[t] * churn_rate)
  
  var revenue: TimeSeries<Currency<USD>>
  revenue[t] = customers[t] * price_per_customer
  
  var profit: TimeSeries<Currency<USD>>
  profit[t] = revenue[t] - monthly_costs
}
```

**What's new:**
- `~Normal(μ=20, σ=3)` = "Normally distributed around 20, with standard deviation 3"
- This means: 68% chance between 17-23, 95% chance between 14-26

---

### Step 2: Run Monte Carlo Simulation

This runs your model 1,000 times with different random values:

```bash
./pel check saas_uncertain.pel
```

```bash
./pel compile saas_uncertain.pel -o saas_uncertain.ir.json
```

```bash
./pel run saas_uncertain.ir.json --mode monte_carlo --runs 1000 --seed 42 -o saas_monte_carlo.json
```

**What this does:**
- Runs your model 1,000 different times
- Each time uses different random values for new customers and churn
- Shows you the range of possible outcomes

---

### Step 3: Understand the Results

Open `saas_monte_carlo.json`. You'll see it ran 1,000 simulations. This shows you:

- **Best case scenario** (if things go well)
- **Worst case scenario** (if things go poorly)  
- **Most likely outcome** (middle of the range)

---

## Part 4: Real Business Use Case - Hiring Plan 👥

### The Scenario

You're planning to hire engineers for your startup:
- **Current team:** 5 engineers
- **Starting salary:** $120,000/year per engineer
- **Plan:** Hire 2 engineers per quarter (every 3 months)
- **Salary growth:** 3% annual raises
- **Question:** What's your salary budget for next year?

---

### Create the Hiring Model

Create `hiring_plan.pel`:

```pel
model HiringPlan {
  // Current team size
  param initial_engineers: Count<Employees> = 5 {
    source: "hr_system",
    method: "observed",
    confidence: 1.0
  }
  
  // Average starting salary
  param starting_salary: Currency<USD> = $120_000 {
    source: "offer_letters_2026",
    method: "observed",
    confidence: 0.95
  }
  
  // Hiring rate (per month, so 0.67 = 2 per quarter)
  param hiring_rate: Count<Employees> = 0.67 {
    source: "hiring_plan_2026",
    method: "assumption",
    confidence: 0.70,
    notes: "Target: 2 engineers per quarter"
  }
  
  // Annual raise percentage (3% per year = 0.25% per month)
  param monthly_raise_rate: Rate per Month = 0.0025/1mo {
    source: "compensation_policy",
    method: "assumption",
    confidence: 0.90
  }
  
  // Calculate headcount over time
  var headcount: TimeSeries<Count<Employees>>
  headcount[0] = initial_engineers
  headcount[t+1] = headcount[t] + hiring_rate
  
  // Calculate average salary (grows with raises)
  var avg_salary: TimeSeries<Currency<USD>>
  avg_salary[0] = starting_salary
  avg_salary[t+1] = avg_salary[t] * (1 + monthly_raise_rate)
  
  // Calculate total monthly payroll
  var monthly_payroll: TimeSeries<Currency<USD>>
  monthly_payroll[t] = headcount[t] * avg_salary[t]
  
  // Calculate annual salary budget (payroll * 12)
  var annual_budget: TimeSeries<Currency<USD>>
  annual_budget[t] = monthly_payroll[t] * 12
}
```

---

### Run the Hiring Forecast

```bash
./pel check hiring_plan.pel
```

```bash
./pel compile hiring_plan.pel -o hiring_plan.ir.json
```

```bash
./pel run hiring_plan.ir.json --mode deterministic --seed 42 -o hiring_results.json
```

---

### Interpret Results

Open `hiring_results.json`:

```json
"headcount": [
  5.0,      // Month 0: 5 engineers
  5.67,     // Month 1
  6.34,     // Month 2
  7.01,     // Month 3 (2 added)
  ...
  13.04     // Month 12: ~13 engineers
],
"monthly_payroll": [
  600000,    // Month 0: $600k total
  ...
  1_565_000  // Month 12: $1.56M total
]
```

**Business insight:** 
- You'll grow from 5 to ~13 engineers in a year
- Your monthly payroll will go from $600k to $1.56M
- Annual budget needed: **~$18.7M** for salaries

---

## Part 5: Pro Tips for Business Users 💡

### Tip 1: Document Your Assumptions

Always fill in the provenance blocks:
```pel
param customer_growth: Rate per Month = 0.15/1mo {
  source: "marketing_forecast_q1_2026",
  method: "assumption",
  confidence: 0.60,
  notes: "Based on new ad campaign launch"
}
```

**Why?** Six months from now, you'll forget where "0.15" came from!

---

### Tip 2: Use Realistic Confidence Scores

- `confidence: 1.0` = You're 100% certain (rare!)
- `confidence: 0.95` = Observed data from your systems
- `confidence: 0.70` = Educated guess based on data
- `confidence: 0.50` = Wild guess, needs validation

**Example:**
```pel
// You KNOW your current price (1.0 confidence)
param price: Currency<USD> = $99 {
  source: "website",
  method: "observed",
  confidence: 1.0
}

// You're GUESSING at churn rate (0.50 confidence)
param churn: Rate per Month = 0.04/1mo {
  source: "industry_report",
  method: "assumption",
  confidence: 0.50,
  notes: "Need to measure actual churn ASAP"
}
```

---

### Tip 3: Start Simple, Add Complexity

**Version 1 (Simple):**
```pel
var revenue: TimeSeries<Currency<USD>>
revenue[t] = customers * price
```

**Version 2 (Add churn):**
```pel
var customers: TimeSeries<Count<Customers>>
customers[t+1] = customers[t] * (1 - churn_rate) + new_customers
```

**Version 3 (Add seasonality):**
```pel
var seasonal_multiplier: Array<Fraction> = [1.2, 1.0, 0.8, 1.1, ...]
var revenue: TimeSeries<Currency<USD>>
revenue[t] = customers[t] * price * seasonal_multiplier[t]
```

---

### Tip 4: Use Descriptive Names

❌ **Bad:**
```pel
param x: Currency<USD> = $5000
param r: Rate per Month = 0.05/1mo
```

✅ **Good:**
```pel
param monthly_rent: Currency<USD> = $5000
param customer_churn_rate: Rate per Month = 0.05/1mo
```

---

## Part 6: Common Business Scenarios 📈

### Scenario 1: Break-Even Analysis

"When will my startup become profitable?"

```pel
model BreakEven {
  param monthly_revenue: Currency<USD> = $8_000 {
    source: "current_mrr",
    method: "observed",
    confidence: 0.95
  }
  
  param revenue_growth: Rate per Month = 0.15/1mo {
    source: "sales_plan",
    method: "assumption",
    confidence: 0.60
  }
  
  param fixed_costs: Currency<USD> = $12_000 {
    source: "budget",
    method: "observed",
    confidence: 0.90
  }
  
  var revenue: TimeSeries<Currency<USD>>
  revenue[0] = monthly_revenue
  revenue[t+1] = revenue[t] * (1 + revenue_growth)
  
  var profit: TimeSeries<Currency<USD>>
  profit[t] = revenue[t] - fixed_costs
  
  // Add a constraint: warn when we break even
  constraint break_even {
    condition: profit[t] >= $0,
    severity: warning,
    message: "Profitable!"
  }
}
```

---

### Scenario 2: Inventory Planning

"How many units should I stock?"

```pel
model InventoryPlanning {
  param weekly_sales: Count<Units> = 50 {
    source: "pos_system",
    method: "observed",
    confidence: 0.85
  }
  
  param lead_time_weeks: Duration = 2w {
    source: "supplier_contract",
    method: "observed",
    confidence: 0.90
  }
  
  param safety_stock_multiplier: Fraction = 1.5 {
    source: "inventory_policy",
    method: "assumption",
    confidence: 0.70,
    notes: "50% buffer for demand spikes"
  }
  
  var reorder_point: Count<Units>
  reorder_point = weekly_sales * 2 * safety_stock_multiplier
}
```

Run with:
```bash
./pel check inventory.pel && ./pel compile inventory.pel -o inventory.ir.json && ./pel run inventory.ir.json --mode deterministic --seed 42 -o inventory_results.json
```

---

### Scenario 3: Marketing Budget ROI

"What return will I get on ad spend?"

```pel
model MarketingROI {
  param ad_spend: Currency<USD> = $10_000 {
    source: "marketing_budget_march",
    method: "assumption",
    confidence: 0.95
  }
  
  param cost_per_click: Currency<USD> = $2.50 {
    source: "google_ads_dashboard",
    method: "observed",
    confidence: 0.80
  }
  
  param conversion_rate: Fraction = 0.03 {
    source: "landing_page_analytics",
    method: "observed",
    confidence: 0.75
  }
  
  param customer_lifetime_value: Currency<USD> = $500 {
    source: "cohort_analysis",
    method: "fitted",
    confidence: 0.70
  }
  
  var total_clicks: Count<Clicks>
  total_clicks = ad_spend / cost_per_click
  
  var new_customers: Count<Customers>
  new_customers = total_clicks * conversion_rate
  
  var total_revenue: Currency<USD>
  total_revenue = new_customers * customer_lifetime_value
  
  var roi: Fraction
  roi = (total_revenue - ad_spend) / ad_spend
}
```

---

## Part 7: Troubleshooting 🔧

### Error: "File not found"

**Problem:**
```bash
./pel check my_model.pel
Error: File not found: my_model.pel
```

**Solution:** Make sure you're in the correct directory and the file exists:
```bash
ls *.pel
```

---

### Error: "Type error: Cannot add Currency<USD> and Rate"

**Problem:**
```pel
var total = revenue + growth_rate  // ❌ Wrong!
```

**Solution:** You can't add dollars to a percentage. Multiply instead:
```pel
var new_revenue = revenue * (1 + growth_rate)  // ✅ Correct!
```

---

### Error: "Provenance errors found"

**Problem:**
```pel
param price: Currency<USD> = $100  // Missing provenance!
```

**Solution:** Add the provenance block:
```pel
param price: Currency<USD> = $100 {
  source: "pricing_team",
  method: "assumption",
  confidence: 0.80
}
```

---

### Warning: "Provenance completeness: 60%"

This means some parameters are missing provenance. It's not an error, but you should add documentation for all parameters.

---

## Part 8: Next Steps 🚀

Congratulations! You now know how to:

✅ Create economic models from scratch  
✅ Compile and run forecasts  
✅ Model uncertainty with Monte Carlo  
✅ Apply models to real business scenarios  

### Continue Learning

1. **Tutorial 2: Economic Types** - Learn about currencies, rates, and durations
   ```bash
   cat docs/tutorials/02_economic_types.md
   ```

2. **Tutorial 3: Distributions** - Master uncertainty modeling
   ```bash
   cat docs/tutorials/03_uncertainty_distributions.md
   ```

3. **Browse Examples** - See more complex models
   ```bash
   ls examples/
   ```

4. **Read the Spec** - Deep dive into language features
   ```bash
   cat spec/pel_language_spec.md
   ```

---

## Quick Reference Card 📋

### File Extensions
- `.pel` = Your model source code
- `.ir.json` = Compiled model (don't edit manually)
- `_results.json` = Simulation output

### Common Commands

**Check a model:**
```bash
./pel check FILENAME.pel
```

**Compile a model:**
```bash
./pel compile FILENAME.pel -o OUTPUT.ir.json
```

**Run deterministic:**
```bash
./pel run MODEL.ir.json --mode deterministic --seed 42 -o results.json
```

**Run Monte Carlo (1000 scenarios):**
```bash
./pel run MODEL.ir.json --mode monte_carlo --runs 1000 --seed 42 -o mc_results.json
```

### Model Structure Template

```pel
model YourModelName {
  // Inputs (what you know or assume)
  param input_name: Type = value {
    source: "where_it_came_from",
    method: "observed or assumption",
    confidence: 0.0-1.0
  }
  
  // Calculations (what PEL computes)
  var output_name: Type
  output_name = input_name * 2
  
  // Time series calculations
  var timeseries_var: TimeSeries<Type>
  timeseries_var[0] = starting_value
  timeseries_var[t+1] = timeseries_var[t] * growth_factor
}
```

---

## Setup Commands (If Needed)

If `./pel --version` didn't work, run these setup commands:

```bash
python3 -m venv .venv
```

```bash
source .venv/bin/activate
```

```bash
pip install -e ".[dev]"
```

```bash
./pel --version
```

---

## Getting Help

- **Documentation:** `docs/` folder
- **Examples:** `examples/` folder  
- **Language Spec:** `spec/pel_language_spec.md`
- **GitHub Issues:** https://github.com/Coding-Krakken/pel-lang/issues

---

**Happy Modeling! 🎉**

Remember: Every successful business model started as a simple spreadsheet. You're now building something better: reproducible, auditable, and type-safe economic models.
