#!/usr/bin/env python3
"""
Historical Data Analysis for PEL Model Calibration
Extract growth rates and trends from historical data
"""

import pandas as pd
import numpy as np
from scipy import stats

# Load historical data
data = pd.read_csv('historical_ecommerce_data.csv', comment='#')

print("=" * 80)
print("📊 HISTORICAL E-COMMERCE DATA ANALYSIS")
print("=" * 80)
print()

print("Data Summary:")
print(f"  Time Period: {data['month'].iloc[0]} to {data['month'].iloc[-1]}")
print(f"  Data Points: {len(data)} months")
print()

# =============================================================================
# REVENUE ANALYSIS
# =============================================================================

print("💰 REVENUE ANALYSIS")
print("-" * 80)

initial_revenue = data['revenue'].iloc[0]
final_revenue = data['revenue'].iloc[-1]
total_growth = ((final_revenue / initial_revenue) - 1) * 100

print(f"  Starting Revenue:      ${initial_revenue:>12,.2f}")
print(f"  Ending Revenue:        ${final_revenue:>12,.2f}")
print(f"  Total Growth:          {total_growth:>12,.1f}%")
print()

# Calculate month-over-month growth rates
data['revenue_growth'] = data['revenue'].pct_change()
avg_growth_rate = data['revenue_growth'].mean()
std_growth_rate = data['revenue_growth'].std()

print(f"  Avg Monthly Growth:    {avg_growth_rate*100:>12,.2f}%")
print(f"  Std Dev Growth:        {std_growth_rate*100:>12,.2f}%")
print(f"  Min Monthly Growth:    {data['revenue_growth'].min()*100:>12,.2f}%")
print(f"  Max Monthly Growth:    {data['revenue_growth'].max()*100:>12,.2f}%")
print()

# =============================================================================
# CUSTOMER ACQUISITION ANALYSIS
# =============================================================================

print("👥 CUSTOMER ACQUISITION ANALYSIS")
print("-" * 80)

data['new_customers'] = data['customers'].diff().fillna(data['customers'].iloc[0])
avg_new_customers = data['new_customers'].mean()
std_new_customers = data['new_customers'].std()

print(f"  Avg New Customers/Mo:  {avg_new_customers:>12,.0f}")
print(f"  Std Dev:               {std_new_customers:>12,.0f}")
print(f"  Min:                   {data['new_customers'].min():>12,.0f}")
print(f"  Max:                   {data['new_customers'].max():>12,.0f}")
print()

# =============================================================================
# AVERAGE ORDER VALUE ANALYSIS
# =============================================================================

print("🛒 AVERAGE ORDER VALUE ANALYSIS")
print("-" * 80)

avg_aov = data['avg_order_value'].mean()
std_aov = data['avg_order_value'].std()
aov_trend = data['avg_order_value'].iloc[-1] - data['avg_order_value'].iloc[0]

print(f"  Mean AOV:              ${avg_aov:>12,.2f}")
print(f"  Std Dev AOV:           ${std_aov:>12,.2f}")
print(f"  AOV Trend:             ${aov_trend:>12,.2f} ({'+' if aov_trend > 0 else ''}{(aov_trend/data['avg_order_value'].iloc[0])*100:.1f}%)")
print()

# =============================================================================
# CONVERSION RATE ANALYSIS
# =============================================================================

print("📊 CONVERSION RATE ANALYSIS")
print("-" * 80)

avg_conversion = data['conversion_rate'].mean()
std_conversion = data['conversion_rate'].std()
conversion_trend = data['conversion_rate'].iloc[-1] - data['conversion_rate'].iloc[0]

print(f"  Mean Conversion:       {avg_conversion*100:>12,.2f}%")
print(f"  Std Dev:               {std_conversion*100:>12,.2f}%")
print(f"  Trend:                 {'+' if conversion_trend > 0 else ''}{conversion_trend*100:.2f}% points")
print()

# =============================================================================
# LINEAR REGRESSION FOR FORECASTING
# =============================================================================

print("📈 TREND ANALYSIS (Linear Regression)")
print("-" * 80)

# Revenue trend
months = np.arange(len(data))
slope_revenue, intercept_revenue, r_value, p_value, std_err = stats.linregress(months, data['revenue'])

print(f"  Revenue Growth Rate:   ${slope_revenue:>12,.2f}/month")
print(f"  R-squared:             {r_value**2:>12,.3f}")
print()

# Customer trend
slope_customers, intercept_customers, r_value_cust, p_value_cust, std_err_cust = stats.linregress(months, data['customers'])

print(f"  Customer Growth Rate:  {slope_customers:>12,.0f}/month")
print(f"  R-squared:             {r_value_cust**2:>12,.3f}")
print()

# =============================================================================
# DERIVED PEL PARAMETERS
# =============================================================================

print()
print("🎯 RECOMMENDED PEL MODEL PARAMETERS")
print("=" * 80)
print()

print("Based on historical data analysis:")
print()

print(f"""
model EcommerceForeecast {{
  // Historical baseline (start of 2025)
  param initial_monthly_revenue: Currency<USD> = ${initial_revenue:.0f} {{
    source: "historical_data_2025",
    method: "observed",
    confidence: 1.0
  }}
  
  // Derived from 12-month average
  param monthly_revenue_growth_rate: Rate per Month = {avg_growth_rate:.4f}/1mo {{
    source: "historical_analysis_2025",
    method: "derived",
    confidence: 0.85,
    notes: "Average {avg_growth_rate*100:.2f}% monthly growth with ±{std_growth_rate*100:.2f}% volatility"
  }}
  
  // Customer acquisition (average new customers per month)
  param avg_new_customers_per_month: Count<Customers> = {int(avg_new_customers)} {{
    source: "historical_analysis_2025",
    method: "derived",
    confidence: 0.80,
    notes: "Average {avg_new_customers:.0f} new customers/month, stddev {std_new_customers:.0f}"
  }}
  
  // Average order value
  param average_order_value: Currency<USD> = ${avg_aov:.2f} {{
    source: "historical_analysis_2025",
    method: "derived",
    confidence: 0.85,
    notes: "Mean AOV ${avg_aov:.2f}, trending {'up' if aov_trend > 0 else 'down'}"
  }}
  
  // Conversion rate
  param conversion_rate: Fraction = {avg_conversion:.4f} {{
    source: "historical_analysis_2025",
    method: "derived",
    confidence: 0.80,
    notes: "Average {avg_conversion*100:.2f}% conversion, trending {'up' if conversion_trend > 0 else 'down'}"
  }}
  
  // For Monte Carlo: add uncertainty
  // param revenue_growth_uncertain: Rate per Month = ~Normal(μ={avg_growth_rate:.4f}/1mo, σ={std_growth_rate:.4f}/1mo)
}}
""")

print()
print("=" * 80)
print()
print("💡 Next Steps:")
print("   1. Copy the PEL parameters above into your model")
print("   2. Run forecast: ./pel compile model.pel && ./pel run model.ir.json")
print("   3. Compare forecast vs actual (if you have 2026 data)")
print("   4. Adjust parameters based on business changes")
print()
