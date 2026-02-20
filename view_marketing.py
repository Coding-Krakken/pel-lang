#!/usr/bin/env python3
"""
Marketing CAC/LTV Analysis Results Viewer
Shows key metrics and channel performance
"""

import json
import sys

def view_marketing_results(filename):
    with open(filename, 'r') as f:
        results = json.load(f)
    
    print("=" * 80)
    print("📊 MARKETING PERFORMANCE ANALYSIS - CAC vs LTV")
    print("=" * 80)
    print()
    
    # Get assumptions
    assumptions = {a['name']: a['value'] for a in results['assumptions']}
    variables = results['variables']
    
    # =============================================================================
    # KEY METRICS SUMMARY
    # =============================================================================
    print("💰 KEY FINANCIAL METRICS")
    print("-" * 80)
    
    # CAC Metrics
    blended_cac = variables['blended_cac'][0] if isinstance(variables['blended_cac'], list) else variables['blended_cac']
    print(f"  Blended CAC:              ${blended_cac:>10,.2f}")
    
    # LTV Metrics
    customer_ltv = variables['customer_ltv'][0] if isinstance(variables['customer_ltv'], list) else variables['customer_ltv']
    print(f"  Customer LTV:             ${customer_ltv:>10,.2f}")
    
    # LTV:CAC Ratio
    ltv_to_cac = variables['ltv_to_cac_ratio'][0] if isinstance(variables['ltv_to_cac_ratio'], list) else variables['ltv_to_cac_ratio']
    print(f"  LTV:CAC Ratio:            {ltv_to_cac:>10,.2f}x")
    
    # Health indicator
    if ltv_to_cac >= 3.0:
        health = "✅ HEALTHY"
    elif ltv_to_cac >= 2.0:
        health = "⚠️  ACCEPTABLE"
    else:
        health = "❌ UNHEALTHY"
    print(f"  Business Health:          {health}")
    print()
    
    # Payback period
    payback = variables['cac_payback_months'][0] if isinstance(variables['cac_payback_months'], list) else variables['cac_payback_months']
    print(f"  CAC Payback Period:       {payback:>10,.1f} months")
    
    if payback <= 12:
        payback_health = "✅ Excellent (< 12 months)"
    elif payback <= 18:
        payback_health = "⚠️  Acceptable (< 18 months)"
    else:
        payback_health = "❌ Too Long (> 18 months)"
    print(f"  Payback Assessment:       {payback_health}")
    print()
    
    # Customer lifetime
    lifetime = variables['average_customer_lifetime_months'][0] if isinstance(variables['average_customer_lifetime_months'], list) else variables['average_customer_lifetime_months']
    print(f"  Avg Customer Lifetime:    {lifetime:>10,.1f} months")
    print()
    
    # =============================================================================
    # CHANNEL BREAKDOWN
    # =============================================================================
    print()
    print("📢 CHANNEL PERFORMANCE")
    print("-" * 80)
    
    total_spend = variables['total_marketing_spend'][0] if isinstance(variables['total_marketing_spend'], list) else variables['total_marketing_spend']
    total_customers = variables['total_new_customers'][0] if isinstance(variables['total_new_customers'], list) else variables['total_new_customers']
    
    print(f"  Total Monthly Spend:      ${total_spend:>10,.2f}")
    print(f"  Total New Customers:      {total_customers:>10,.0f}")
    print()
    
    # Paid Ads
    cac_paid = variables['cac_paid_ads'][0] if isinstance(variables['cac_paid_ads'], list) else variables['cac_paid_ads']
    ltv_cac_paid = variables['ltv_to_cac_paid_ads'][0] if isinstance(variables['ltv_to_cac_paid_ads'], list) else variables['ltv_to_cac_paid_ads']
    print(f"  PAID ADS:")
    print(f"    Budget:                 ${assumptions['paid_ads_budget']:>10,.2f}")
    print(f"    New Customers:          {assumptions['customers_from_paid_ads']:>10,.0f}")
    print(f"    CAC:                    ${cac_paid:>10,.2f}")
    print(f"    LTV:CAC Ratio:          {ltv_cac_paid:>10,.2f}x")
    print()
    
    # Content Marketing
    cac_content = variables['cac_content'][0] if isinstance(variables['cac_content'], list) else variables['cac_content']
    ltv_cac_content = variables['ltv_to_cac_content'][0] if isinstance(variables['ltv_to_cac_content'], list) else variables['ltv_to_cac_content']
    print(f"  CONTENT MARKETING:")
    print(f"    Budget:                 ${assumptions['content_marketing_budget']:>10,.2f}")
    print(f"    New Customers:          {assumptions['customers_from_content']:>10,.0f}")
    print(f"    CAC:                    ${cac_content:>10,.2f}")
    print(f"    LTV:CAC Ratio:          {ltv_cac_content:>10,.2f}x")
    print()
    
    # Events
    cac_events = variables['cac_events'][0] if isinstance(variables['cac_events'], list) else variables['cac_events']
    ltv_cac_events = variables['ltv_to_cac_events'][0] if isinstance(variables['ltv_to_cac_events'], list) else variables['ltv_to_cac_events']
    print(f"  EVENTS:")
    print(f"    Budget:                 ${assumptions['events_budget']:>10,.2f}")
    print(f"    New Customers:          {assumptions['customers_from_events']:>10,.0f}")
    print(f"    CAC:                    ${cac_events:>10,.2f}")
    print(f"    LTV:CAC Ratio:          {ltv_cac_events:>10,.2f}x")
    print()
    
    # Best channel
    channels = [
        ('Paid Ads', ltv_cac_paid, cac_paid),
        ('Content', ltv_cac_content, cac_content),
        ('Events', ltv_cac_events, cac_events)
    ]
    best_channel = max(channels, key=lambda x: x[1])
    print(f"  🏆 Best Channel: {best_channel[0]} (LTV:CAC = {best_channel[1]:.2f}x)")
    print()
    
    # =============================================================================
    # GROWTH PROJECTIONS  
    # =============================================================================
    print()
    print("📈 24-MONTH GROWTH PROJECTION")
    print("-" * 80)
    
    mrr = variables['mrr']
    cumulative_customers = variables['cumulative_customers']
    cumulative_profit = variables['cumulative_profit']
    
    print(f"  Month 0:")
    print(f"    MRR:                    ${mrr[0]:>10,.2f}")
    print(f"    Customers:              {cumulative_customers[0]:>10,.0f}")
    print()
    
    print(f"  Month 6:")
    print(f"    MRR:                    ${mrr[6]:>10,.2f}")
    print(f"    Customers:              {cumulative_customers[6]:>10,.0f}")
    print(f"    Cumulative Profit:      ${cumulative_profit[6]:>10,.2f}")
    print()
    
    print(f"  Month 12:")
    print(f"    MRR:                    ${mrr[12]:>10,.2f}")
    print(f"    Customers:              {cumulative_customers[12]:>10,.0f}")
    print(f"    Cumulative Profit:      ${cumulative_profit[12]:>10,.2f}")
    print()
    
    print(f"  Month 24:")
    print(f"    MRR:                    ${mrr[23]:>10,.2f}")
    print(f"    Customers:              {cumulative_customers[23]:>10,.0f}")
    print(f"    Cumulative Profit:      ${cumulative_profit[23]:>10,.2f}")
    print()
    
    mrr_growth = ((mrr[23] / mrr[0]) - 1) * 100
    print(f"  MRR Growth (24 months):   {mrr_growth:>10,.1f}%")
    print()
    
    # =============================================================================
    # RECOMMENDATIONS
    # =============================================================================
    print()
    print("💡 STRATEGIC RECOMMENDATIONS")
    print("-" * 80)
    
    if ltv_to_cac < 3.0:
        print("  ⚠️  LTV:CAC ratio is below 3:1 target")
        print("     → Consider: Improve retention (reduce churn)")
        print("     → Consider: Increase pricing")
        print("     → Consider: Reduce CAC through channel optimization")
        print()
    
    # Channel optimization
    worst_channel = min(channels, key=lambda x: x[1])
    print(f"  📊 {worst_channel[0]} has lowest LTV:CAC ({worst_channel[1]:.2f}x)")
    print(f"     → Consider: Reallocate budget to better-performing channels")
    print()
    
    if payback > 12:
        print(f"  ⏱️  Payback period of {payback:.1f} months is long")
        print("     → Consider: Optimize onboarding to reduce churn")
        print("     → Consider: Upsell/cross-sell to increase ARPU")
        print()
    
    print("=" * 80)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 view_marketing.py <marketing_results.json>")
        sys.exit(1)
    
    view_marketing_results(sys.argv[1])
