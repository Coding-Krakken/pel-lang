# PEL Real-World Usage Demo - Complete Portfolio

This document showcases realistic business modeling scenarios using PEL (Programmable Economic Language) across different industries and use cases.

---

## 📊 Models Created

### 1. **Marketing Performance Analysis** - CAC vs LTV 
**File:** [marketing_cac_ltv.pel](marketing_cac_ltv.pel)  
**Industry:** SaaS / Marketing  
**Purpose:** Optimize marketing spend across channels

**Key Features:**
- Multi-channel CAC calculation (Paid Ads, Content, Events)
- Customer Lifetime Value analysis
- LTV:CAC ratio optimization  
- Channel performance comparison
- 24-month growth projections
- ROI tracking per marketing channel

**Business Value:**
- Identify most efficient customer acquisition channels
- Optimize marketing budget allocation
- Forecast customer growth and revenue
- Track payback periods

**Run It:**
```bash
./pel compile marketing_cac_ltv.pel -o marketing_cac_ltv.ir.json
./pel run marketing_cac_ltv.ir.json --mode deterministic --seed 42 --horizon 24 -o marketing_results.json
python3 view_marketing.py marketing_results.json
```

**Key Metrics:**
- Blended CAC: Weighted average across all channels
- Customer LTV: Lifetime revenue per customer
- LTV:CAC Ratio: Should be ≥ 3:1 for healthy SaaS
- Payback Period: Target < 12 months

---

### 2. **Product Development Budget** - Constraints & Resource Allocation
**File:** [product_development.pel](product_development.pel)  
**Industry:** R&D / Product Management  
**Purpose:** Budget tracking with business constraints

**Key Features:**
- Team size projections (Engineers + Designers)
- Budget constraint enforcement (hard limits)
- Cash reserve requirements
- Team ratio optimization (3:1 to 6:1 engineer:designer)
- Monthly burn rate tracking
- 6 business constraints automated

**Constraints Implemented:**
1. ❌ **Error:** Annual budget not exceeded
2. ❌ **Error:** Maintain minimum cash reserve
3. ⚠️ **Warning:** Healthy engineer-to-designer ratio
4. ⚠️ **Warning:** Team size < 50 people
5. ⚠️ **Warning:** R&D spending < 50% of revenue
6. ⚠️ **Warning:** Positive cash flow by month 12

**Business Value:**
- Automatic budget compliance checking
- Early warning system for cash problems
- Team composition optimization
- Hire vs. freeze decision support

**Run It:**
```bash
./pel compile product_development.pel -o product_development.ir.json
./pel run product_development.ir.json --mode deterministic --seed 42 --horizon 18 -o product_dev_results.json
cat product_dev_results.json | jq '.constraint_violations' | head -50
```

---

### 3. **Manufacturing & Inventory** - Supply Chain Optimization
**File:** [manufacturing_inventory.pel](manufacturing_inventory.pel)  
**Industry:** Manufacturing / Operations  
**Purpose:** Production planning and inventory management

**Key Features:**
- Production capacity modeling
- Inventory level tracking
- Safety stock calculations
- Stockout risk analysis
- Holding cost optimization
- Capacity utilization monitoring

**Constraints Implemented:**
1. ❌ **Error:** No negative inventory (stockout prevention)
2. ❌ **Error:** Capacity not exceeded
3. ⚠️ **Warning:** Maintain 50% minimum safety stock
4. ⚠️ **Warning:** Capacity utilization 70-95% (sweet spot)
5. ⚠️ **Warning:** Monthly operations profitable
6. ⚠️ **Warning:** Inventory not excessive (working capital)

**Business Value:**
- Prevent stockouts and production bottlenecks
- Optimize working capital tied up in inventory
- Balance production efficiency with demand
- Early warning for capacity expansion needs

**Run It:**
```bash
./pel compile manufacturing_inventory.pel -o manufacturing.ir.json
./pel run manufacturing.ir.json --mode deterministic --seed 42 --horizon 12 -o manufacturing_results.json
```

**Key Metrics:**
- Effective capacity: Adjusted for OEE (Overall Equipment Effectiveness)
- Inventory days: Current inventory ÷ daily demand
- Capacity utilization: Production ÷ max capacity
- Unit economics: Margin per unit sold

---

### 4. **Historical Data Calibration** - Model Fitting
**Files:** 
- Data: [historical_ecommerce_data.csv](historical_ecommerce_data.csv)
- Analyzer: [analyze_historical_data.py](analyze_historical_data.py)

**Industry:** E-commerce / Data Analytics  
**Purpose:** Derive model parameters from historical data

**Analysis Performed:**
- Revenue growth trend analysis (linear regression)
- Customer acquisition patterns
- Average order value evolution
- Conversion rate optimization
- Month-over-month volatility
- Statistical confidence intervals

**Output:**
- PEL parameter recommendations with provenance
- Growth rate: 6.44% ± 1.56% (from 12 months of data)
- Customer acquisition: 127 new customers/month
- R-squared: 0.995 (excellent fit)

**Business Value:**
- Data-driven parameter selection (not guesswork)
- Confidence levels for each assumption
- Trend detection (improving vs. declining)
- Forecast accuracy improvement

**Run It:**
```bash
python3 analyze_historical_data.py
```

**Next Steps:**
1. Use derived parameters in your PEL model
2. Run forecast for next 12 months
3. Compare forecast vs. actual monthly
4. Refine parameters quarterly

---

### 5. **Risk Scenario Planning** - Strategic Analysis
**File:** [risk_scenarios.pel](risk_scenarios.pel)  
**Industry:** Finance / Strategic Planning  
**Purpose:** Multi-scenario executive planning

**Scenarios Modeled:**
1. **Pessimistic** (Economic downturn)
   - 2% growth rate
   - 50% churn increase
   - 15% cost inflation
   
2. **Base Case** (Business as usual)
   - 8% growth rate
   - Stable churn
   - 5% cost increase
   
3. **Optimistic** (Market expansion)
   - 15% growth rate
   - 20% churn reduction
   - 10% cost increase (economies of scale)

**Risk Indicators:**
- Cash runway monitoring
- Profitability timeline
- Fundraising triggers
- Burn rate alerts

**Constraints Implemented:**
1. ❌ **Error:** Cash runway > 3 months (critical)
2. ⚠️ **Warning:** Cash runway > 6 months (fundraising trigger)
3. ⚠️ **Warning:** Profitable by month 12
4. ❌ **Error:** Cash balance > $0 (solvency)
5. ⚠️ **Warning:** Revenue growth (not declining)

**Business Value:**
- Board-ready scenario analysis
- Fundraising timing decisions
- Risk mitigation planning
- Strategic pivot triggers

**Run It:**
```bash
# Base case
./pel compile risk_scenarios.pel -o risk_scenarios.ir.json
./pel run risk_scenarios.ir.json --mode deterministic --horizon 18 -o risk_base_case.json

# Would need to modify scenario_type parameter for other scenarios
```

---

### 6. **Personal Consulting Business** - Practical Example
**Files:**
- Model: [my_consulting_business.pel](my_consulting_business.pel)
- Uncertain: [my_consulting_uncertain.pel](my_consulting_uncertain.pel)
- Workflow: [run_my_analysis.sh](run_my_analysis.sh)
- Report: [BUSINESS_REPORT.md](BUSINESS_REPORT.md)

**Purpose:** Real user learning journey - from beginner to business insights

**Demonstrates:**
- Model creation from scratch
- Revenue and expense tracking
- Growth projections
- Cumulative profit calculation
- Uncertainty modeling (Monte Carlo ready)
- Professional reporting

**Complete Workflow:**
```bash
./run_my_analysis.sh
```

---

## 🎯 Key PEL Features Demonstrated

### ✅ Type Safety
- `Currency<USD>` prevents mixing currencies
- `Rate per Month` ensures dimensional consistency
- `Count<Customers>`, `Count<Employees>` for entity tracking
- `Fraction` for percentages and ratios

### ✅ Provenance Tracking
All parameters documented with:
- **source:** Where the data came from
- **method:** How it was derived (observed, assumed, derived)
- **confidence:** 0.0-1.0 certainty level
- **notes:** Context and assumptions

### ✅ Constraints (Business Rules)
- **Error severity:** Hard stops (budget, cash, inventory)
- **Warning severity:** Soft alerts (ratios, trends)
- Automatic constraint checking during execution
- Violation tracking in results

### ✅ Time Series Modeling
- `TimeSeries<Type>` for values that change over time
- Recursive definitions: `value[t+1] = value[t] * growth`
- Forward projections (12, 18, 24 months)
- Historical lookback: `value[t-1]`

### ✅ Monte Carlo Ready
- Distribution support: `~Normal(μ, σ)`
- `--mode monte_carlo --runs 1000`
- Uncertainty quantification
- Risk analysis

### ✅ Reproducibility
- Deterministic mode with seed
- Intermediate representation (IR) format
- Version-controlled models
- Audit trail through provenance

---

## 📈 Usage Patterns for Different Roles

### **CFO / Finance**
- Risk scenario planning ([risk_scenarios.pel](risk_scenarios.pel))
- Budget constraint enforcement ([product_development.pel](product_development.pel))
- Cash runway analysis
- Fundraising timing

### **CMO / Marketing**
- CAC/LTV optimization ([marketing_cac_ltv.pel](marketing_cac_ltv.pel))
- Channel performance analysis
- Customer acquisition forecasting
- Marketing ROI tracking

### **COO / Operations**
- Manufacturing capacity ([manufacturing_inventory.pel](manufacturing_inventory.pel))
- Inventory optimization
- Supply chain risk
- Production scheduling

### **CPO / Product**
- R&D budget tracking ([product_development.pel](product_development.pel))
- Team scaling decisions
- Feature prioritization (resource constraints)
- Roadmap planning

### **Data Analyst**
- Historical calibration ([analyze_historical_data.py](analyze_historical_data.py))
- Trend analysis
- Parameter fitting
- Forecast validation

### **Business Owner / Consultant**
- Personal business modeling ([my_consulting_business.pel](my_consulting_business.pel))
- Client projections
- Pricing analysis
- Growth planning

---

## 🚀 Quick Start Commands

```bash
# 1. Marketing Analysis
./pel compile marketing_cac_ltv.pel -o marketing.ir.json
./pel run marketing.ir.json --mode deterministic --horizon 24 -o marketing_results.json
python3 view_marketing.py marketing_results.json

# 2. Product Development (with constraint checking)
./pel compile product_development.pel -o product_dev.ir.json
./pel run product_dev.ir.json --mode deterministic --horizon 18 -o product_results.json
cat product_results.json | jq '.constraint_violations | length'

# 3. Manufacturing Planning
./pel compile manufacturing_inventory.pel -o manufacturing.ir.json
./pel run manufacturing.ir.json --mode deterministic --horizon 12 -o mfg_results.json

# 4. Historical Calibration
python3 analyze_historical_data.py

# 5. Risk Scenarios
./pel compile risk_scenarios.pel -o risk.ir.json
./pel run risk.ir.json --mode deterministic --horizon 18 -o risk_results.json

# 6. Personal Business
./run_my_analysis.sh
```

---

## 💡 Best Practices Demonstrated

1. **Document Everything**
   - Source provenance on all parameters
   - Confidence levels explicit
   - Notes capture assumptions

2. **Use Constraints Liberally**
   - Encode business rules as constraints
   - Mix error (hard) and warning (soft) constraints
   - Catch problems early

3. **Separate Concerns**
   - Parameters (inputs) vs. Variables (computed)
   - Constants vs. Time-varying values
   - Deterministic vs. Uncertain parameters

4. **Build Incrementally**
   - Start simple, add complexity
   - Test at each step
   - Validate constraints

5. **Make it Reproducible**
   - Use seeds for deterministic runs
   - Version control .pel files
   - Document workflow scripts

6. **Analyze Results Systematically**
   - Custom viewers for different analyses
   - Constraint violation reviews
   - Comparative scenario analysis

---

## 📚 Files Created

```
marketing_cac_ltv.pel              # Marketing channel optimization
view_marketing.py                   # Marketing results viewer

product_development.pel             # R&D budget with constraints
product_dev_results.json           # Results with violations

manufacturing_inventory.pel         # Supply chain & inventory
manufacturing_results.json         # Manufacturing projections

historical_ecommerce_data.csv      # 12 months of historical data
analyze_historical_data.py         # Calibration analysis script

risk_scenarios.pel                 # Multi-scenario strategic planning
risk_base_case.json               # Base case scenario results

my_consulting_business.pel         # Personal business model
my_consulting_uncertain.pel        # With uncertainty
run_my_analysis.sh                # Automated workflow
BUSINESS_REPORT.md                # Professional summary
analyze_mc.py                     # Monte Carlo analyzer
```

---

## 🎓 What I Learned (Realistic User Journey)

1. ✅ Started with beginner examples
2. ✅ Created my own business model
3. ✅ Explored uncertainty with distributions
4. ✅ Applied constraints for business rules
5. ✅ Calibrated from historical data
6. ✅ Built scenario analysis for executives
7. ✅ Created reusable analysis tools
8. ✅ Documented everything professionally

**Total Time Investment:** ~2-3 hours (realistic for a business analyst)

**Business Value Generated:**
- 6 production-ready models
- Automated constraint checking
- Data-driven parameter calibration
- Executive-ready reports
- Reusable analysis framework

---

## 🔮 Next Steps

1. **Expand Scenarios:** Add more risk scenarios (regulatory, competition, market)
2. **Add Distributions:** Convert more parameters to uncertain distributions
3. **Build Dashboards:** Visualize results over time
4. **Integrate Data:** Connect to real-time data sources
5. **Automate Reporting:** Schedule monthly model runs
6. **Share Templates:** Package models for different industries

---

**Created:** February 20, 2026  
**PEL Version:** 0.1.0  
**Purpose:** Demonstrate realistic business usage of PEL across industries
