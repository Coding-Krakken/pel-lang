# 🎉 Your Complete PEL Learning Package

Everything you need to master PEL from absolute beginner to expert, all in one place!

---

## 📚 What You Have Now

### 1. **Complete Beginner Tutorial** (Start Here!)
   📖 [BEGINNER_TUTORIAL.md](BEGINNER_TUTORIAL.md)
   
   **Perfect for:** Non-programmers, business users, analysts
   
   **What you'll learn:**
   - ☕ Model a coffee shop's revenue growth
   - 📊 Build SaaS subscription forecasts
   - 🎲 Run Monte Carlo uncertainty simulations
   - 👥 Plan hiring budgets and salary costs
   
   **Time:** 60-90 minutes of hands-on learning

---

### 2. **Ready-to-Run Example Models**
   📁 [beginner_examples/](beginner_examples/)
   
   Four complete working models you can run immediately:
   - `coffee_shop.pel` - Revenue and profit forecasting
   - `saas_business.pel` - Customer growth with churn
   - `saas_uncertain.pel` - Monte Carlo with distributions
   - `hiring_plan.pel` - Team scaling and payroll
   
   **Run all at once:**
   ```bash
   ./beginner_examples/run_all_examples.sh
   ```

---

### 3. **Command Reference**
   📋 [COMMAND_CHEATSHEET.md](COMMAND_CHEATSHEET.md)
   
   Copy-paste commands for every common task:
   - Basic workflow (check → compile → run)
   - Monte Carlo simulations
   - View and analyze results
   - Troubleshooting tips

---

### 4. **Results Viewer Tool**
   🔍 [beginner_examples/view_results.py](beginner_examples/view_results.py)
   
   Beautiful formatted output from your model runs:
   ```bash
   python3 beginner_examples/view_results.py YOUR_RESULTS.json
   ```

---

## 🚀 Quick Start (Copy and Paste)

### Option 1: Run Everything (Recommended First Time)

```bash
./beginner_examples/run_all_examples.sh
```

Then view any result:
```bash
python3 beginner_examples/view_results.py beginner_examples/coffee_results.json
```

### Option 2: Try a Single Example

```bash
./pel check beginner_examples/coffee_shop.pel
./pel compile beginner_examples/coffee_shop.pel -o beginner_examples/coffee_shop.ir.json
./pel run beginner_examples/coffee_shop.ir.json --mode deterministic --seed 42 -o beginner_examples/results.json
python3 beginner_examples/view_results.py beginner_examples/results.json
```

### Option 3: Create Your Own Model

1. **Create your model file** (copy this template):
   ```bash
   nano my_business_model.pel
   ```

2. **Paste this starter template:**
   ```pel
   model MyBusiness {
     param starting_revenue: Currency<USD> = $10_000 {
       source: "current_data",
       method: "observed",
       confidence: 0.95
     }
     
     param growth_rate: Rate per Month = 0.05/1mo {
       source: "estimate",
       method: "assumption",
       confidence: 0.70
     }
     
     var revenue: TimeSeries<Currency<USD>>
     revenue[0] = starting_revenue
     revenue[t+1] = revenue[t] * (1 + growth_rate)
   }
   ```

3. **Run it:**
   ```bash
   ./pel check my_business_model.pel
   ./pel compile my_business_model.pel -o my_business_model.ir.json
   ./pel run my_business_model.ir.json --mode deterministic --seed 42 -o my_results.json
   python3 beginner_examples/view_results.py my_results.json
   ```

---

## 📖 Learning Paths

### Path 1: Complete Beginner (60-90 min)
Perfect if you've never programmed before:

1. Read [BEGINNER_TUTORIAL.md](BEGINNER_TUTORIAL.md) Part 1-4
2. Run `./beginner_examples/run_all_examples.sh`
3. View results with `view_results.py`
4. Try modifying one example and re-running it

**Outcome:** Can build basic business models

---

### Path 2: Advanced Beginner (2-3 hours)
Once you've completed Path 1:

1. Complete [docs/tutorials/your_first_model_15min.md](docs/tutorials/your_first_model_15min.md)
2. Read [docs/tutorials/02_economic_types.md](docs/tutorials/02_economic_types.md)
3. Read [docs/tutorials/03_uncertainty_distributions.md](docs/tutorials/03_uncertainty_distributions.md)
4. Build your own model from scratch

**Outcome:** Can build production-quality models

---

### Path 3: Expert (4+ hours)
For building enterprise-grade models:

1. Complete Paths 1 & 2
2. Work through all tutorials in [docs/tutorials/](docs/tutorials/)
3. Read language spec: [spec/pel_language_spec.md](spec/pel_language_spec.md)
4. Study advanced examples in [examples/](examples/)

**Outcome:** Full PEL mastery

---

## 🎯 What Can You Build?

### Business Models
- Revenue forecasting
- Customer lifetime value (LTV)
- Customer acquisition cost (CAC)
- Churn analysis
- Unit economics

### Financial Planning
- Budget forecasting
- Hiring and salary planning
- Cash flow projections
- Break-even analysis
- Investment ROI

### Operations
- Inventory planning
- Capacity planning
- Resource allocation
- Supply chain modeling

### Strategic Planning
- Market sizing
- Scenario analysis
- Risk assessment
- "What-if" simulations

---

## 💡 Key Concepts (Simple Explanations)

### Parameters (`param`)
Numbers you **input** into your model:
```pel
param price: Currency<USD> = $50 {
  source: "pricing_page",
  method: "observed",
  confidence: 1.0
}
```

### Variables (`var`)
Numbers PEL **calculates** for you:
```pel
var revenue: Currency<USD>
revenue = customers * price
```

### Time Series (`TimeSeries<T>`)
Values that change over time:
```pel
var revenue: TimeSeries<Currency<USD>>
revenue[0] = $1000        // Month 0
revenue[t+1] = revenue[t] * 1.1  // Grows 10% each month
```

### Uncertainty (`~Normal(...)`)
"I'm not 100% sure of this number":
```pel
param growth: Rate per Month = ~Normal(μ=0.10/1mo, σ=0.02/1mo)
// Likely 10%, but could be 8-12%
```

### Types (Safety!)
PEL prevents mistakes like adding dollars to percentages:
```pel
var total = $100 + 5%     // ❌ Error! Can't add money to fraction
var total = $100 * (1 + 5%)  // ✅ Correct!
```

---

## 🔍 Example Model Explained Line-by-Line

```pel
model CoffeeShop {                           // Start of model
  
  param current_revenue: Currency<USD> = $5_000 {   // Parameter (input)
    source: "bank_statement_jan_2026",              // Where did this come from?
    method: "observed",                             // How did we get it?
    confidence: 0.95                                // How sure are we? (95%)
  }
  
  param growth_rate: Rate per Month = 0.08/1mo {    // 8% growth per month
    source: "marketing_plan",
    method: "assumption",
    confidence: 0.60                                // Less certain (60%)
  }
  
  var revenue: TimeSeries<Currency<USD>>      // Variable (calculated)
  revenue[0] = current_revenue                // Start at $5,000
  revenue[t+1] = revenue[t] * (1 + growth_rate)  // Each month: grow by 8%
}
```

**What happens:**
- Month 0: $5,000
- Month 1: $5,000 × 1.08 = $5,400
- Month 2: $5,400 × 1.08 = $5,832
- Month 3: $5,832 × 1.08 = $6,298
- ...and so on for 12 months

---

## 🆘 Getting Help

### Something not working?

1. **Check the cheat sheet:** [COMMAND_CHEATSHEET.md](COMMAND_CHEATSHEET.md)
2. **Check for typos:** PEL is picky about spelling and brackets
3. **Look at examples:** [beginner_examples/](beginner_examples/)
4. **Read error messages:** They usually tell you exactly what's wrong

### Common Errors and Fixes

**"File not found"**
```bash
# Make sure you're in the right directory
ls *.pel
pwd  # Should show /path/to/PEL
```

**"Type error: Cannot add Currency and Rate"**
```pel
# Wrong
var x = $100 + 0.05/1mo

# Right
var x = $100 * (1 + 0.05)
```

**"Provenance errors"**
```pel
# Wrong (missing provenance)
param price: Currency<USD> = $100

# Right (has provenance)
param price: Currency<USD> = $100 {
  source: "pricing_team",
  method: "assumption",
  confidence: 0.80
}
```

---

## 📊 Sample Output

When you run a model, you'll see:

```
✅ Status: SUCCESS
🔢 Mode: deterministic
🎲 Seed: 42
📅 Timesteps: 12 months

📋 Input Assumptions
  • current_revenue: 5,000.00
    Source: bank_statement_jan_2026
    Confidence: 95%

📈 Calculated Results
  REVENUE
  Month 0:  $5,000.00
  Month 6:  $7,934.37
  Month 12: $12,590.85
  
  Change: $5,000.00 → $12,590.85 (+151.8%)
```

---

## 🎓 Certificate of Completion

After you complete the beginner tutorial, you'll know how to:

✅ Write PEL model syntax  
✅ Define parameters with provenance  
✅ Calculate variables over time  
✅ Model uncertainty with distributions  
✅ Run deterministic and Monte Carlo simulations  
✅ Interpret and present results  
✅ Apply models to real business problems  

**You're now a PEL modeler!** 🎉

---

## 🔗 Additional Resources

- **Main README:** [README.md](README.md)
- **All Tutorials:** [docs/tutorials/](docs/tutorials/)
- **Language Spec:** [spec/pel_language_spec.md](spec/pel_language_spec.md)
- **More Examples:** [examples/](examples/)
- **GitHub Issues:** Report bugs or ask questions

---

## ⏭️ Next Steps After Beginner Tutorial

1. **Build your own model** for your actual business
2. **Share with stakeholders** using the formatted results
3. **Learn advanced features:**
   - Constraints (business rules)
   - Policies (automated decisions)
   - Calibration (fit to real data)
4. **Explore the standard library** for pre-built functions

---

**Ready to start? Open [BEGINNER_TUTORIAL.md](BEGINNER_TUTORIAL.md) now!**

**Questions? Check [COMMAND_CHEATSHEET.md](COMMAND_CHEATSHEET.md) for quick answers.**

**Good luck, and happy modeling! 🚀**
