#!/usr/bin/env python3
"""
PEL Real-World Usage Showcase
Demonstrates the breadth and depth of PEL capabilities
"""

import json
import os

print("=" * 80)
print("🚀 PEL REAL-WORLD USAGE SHOWCASE")
print("=" * 80)
print()
print("This demo shows PEL being used across different business scenarios,")
print("just as real analysts, executives, and business owners would use it.")
print()

# =============================================================================
# PORTFOLIO OVERVIEW
# =============================================================================

models = [
    {
        "name": "Marketing CAC/LTV",
        "file": "marketing_cac_ltv.pel",
        "industry": "SaaS / Marketing",
        "user": "CMO / Head of Growth",
        "purpose": "Optimize customer acquisition spend across channels",
        "features": ["Multi-channel CAC", "LTV calculation", "Channel ROI", "24-month forecast"],
        "constraints": 0,
        "value": "Identify best channels, optimize budget allocation"
    },
    {
        "name": "Product Development Budget",
        "file": "product_development.pel",
        "industry": "R&D / Product",
        "user": "CPO / Engineering Manager",
        "purpose": "Track R&D spending with business rule enforcement",
        "features": ["Team scaling", "Budget constraints", "Cash management", "Hiring plans"],
        "constraints": 6,
        "value": "Automatic budget compliance, early cash warnings"
    },
    {
        "name": "Manufacturing & Inventory",
        "file": "manufacturing_inventory.pel",
        "industry": "Manufacturing / Operations",
        "user": "COO / Operations Manager",
        "purpose": "Production planning and inventory optimization",
        "features": ["Capacity planning", "Inventory tracking", "Stockout prevention", "Cost optimization"],
        "constraints": 6,
        "value": "Prevent stockouts, optimize working capital"
    },
    {
        "name": "Historical Calibration",
        "file": "analyze_historical_data.py",
        "industry": "E-commerce / Analytics",
        "user": "Data Analyst / Finance",
        "purpose": "Derive model parameters from real data",
        "features": ["Trend analysis", "Statistical fitting", "Confidence intervals", "Growth rates"],
        "constraints": 0,
        "value": "Data-driven parameters, not guesswork"
    },
    {
        "name": "Risk Scenario Planning",
        "file": "risk_scenarios.pel",
        "industry": "Finance / Strategy",
        "user": "CFO / CEO / Board",
        "purpose": "Multi-scenario strategic planning",
        "features": ["3 scenarios", "Cash runway", "Fundraising triggers", "Risk indicators"],
        "constraints": 5,
        "value": "Board-ready analysis, strategic decisions"
    },
    {
        "name": "Personal Consulting Business",
        "file": "my_consulting_business.pel",
        "industry": "Consulting / Freelance",
        "user": "Business Owner / Consultant",
        "purpose": "Personal business planning and forecasting",
        "features": ["Revenue projection", "Expense tracking", "Profitability", "Growth planning"],
        "constraints": 0,
        "value": "Real-world learning example, practical application"
    }
]

print("📊 MODEL PORTFOLIO")
print("-" * 80)
print(f"Total Models Created: {len(models)}")
print()

for i, model in enumerate(models, 1):
    print(f"{i}. {model['name']}")
    print(f"   Industry: {model['industry']}")
    print(f"   User: {model['user']}")
    print(f"   Purpose: {model['purpose']}")
    if model['constraints'] > 0:
        print(f"   Constraints: {model['constraints']} business rules enforced")
    print(f"   Value: {model['value']}")
    print()

# =============================================================================
# KEY FEATURES DEMONSTRATED
# =============================================================================

print()
print("✨ PEL FEATURES DEMONSTRATED")
print("=" * 80)
print()

features = {
    "Type Safety": [
        "Currency<USD> prevents mixing currencies",
        "Rate per Month ensures dimensional consistency",
        "Count<Customers>, Count<Employees> for entity tracking",
        "Fraction for percentages and ratios"
    ],
    "Provenance Tracking": [
        "source: Where data came from",
        "method: How derived (observed, assumed, fitted)",
        "confidence: 0.0-1.0 certainty level",
        "notes: Context and assumptions"
    ],
    "Business Constraints": [
        "Error severity: Hard stops (budget, cash)",
        "Warning severity: Soft alerts (ratios, trends)",
        "Automatic checking during execution",
        "Violation tracking in results"
    ],
    "Time Series": [
        "TimeSeries<Type> for dynamic values",
        "Recursive definitions: value[t+1] = f(value[t])",
        "12-24 month projections",
        "Historical lookback"
    ],
    "Uncertainty & Risk": [
        "Distribution support: ~Normal(μ, σ)",
        "Monte Carlo: --mode monte_carlo --runs 1000",
        "Scenario planning (pessimistic/base/optimistic)",
        "Risk quantification"
    ],
    "Reproducibility": [
        "Deterministic mode with seeds",
        "Intermediate representation (IR)",
        "Version-controlled models",
        "Audit trail via provenance"
    ]
}

for feature, items in features.items():
    print(f"✅ {feature}")
    for item in items:
        print(f"   • {item}")
    print()

# =============================================================================
# USAGE BY ROLE
# =============================================================================

print()
print("👥 WHO USES THESE MODELS")
print("=" * 80)
print()

roles = {
    "CFO / Finance": [
        "Risk scenario planning",
        "Budget constraint enforcement",
        "Cash runway analysis",
        "Fundraising timing"
    ],
    "CMO / Marketing": [
        "CAC/LTV optimization",
        "Channel performance",
        "Customer acquisition forecasting",
        "Marketing ROI"
    ],
    "COO / Operations": [
        "Manufacturing capacity",
        "Inventory optimization",
        "Supply chain risk",
        "Production scheduling"
    ],
    "CPO / Product": [
        "R&D budget tracking",
        "Team scaling decisions",
        "Resource constraints",
        "Roadmap planning"
    ],
    "Data Analyst": [
        "Historical calibration",
        "Trend analysis",
        "Parameter fitting",
        "Forecast validation"
    ],
    "Business Owner": [
        "Personal business modeling",
        "Client projections",
        "Pricing analysis",
        "Growth planning"
    ]
}

for role, use_cases in roles.items():
    print(f"👤 {role}")
    for use_case in use_cases:
        print(f"   → {use_case}")
    print()

# =============================================================================
# QUICK START
# =============================================================================

print()
print("🚀 QUICK START GUIDE")
print("=" * 80)
print()

print("Try these models:")
print()

commands = [
    ("Marketing Analysis", "./pel compile marketing_cac_ltv.pel -o out.ir.json && ./pel run out.ir.json --horizon 24 -o results.json"),
    ("Product Development", "./pel compile product_development.pel -o out.ir.json && ./pel run out.ir.json --horizon 18 -o results.json"),
    ("Manufacturing", "./pel compile manufacturing_inventory.pel -o out.ir.json && ./pel run out.ir.json --horizon 12 -o results.json"),
    ("Historical Analysis", "python3 analyze_historical_data.py"),
    ("Risk Scenarios", "./pel compile risk_scenarios.pel -o out.ir.json && ./pel run out.ir.json --horizon 18 -o results.json"),
    ("Personal Business", "./run_my_analysis.sh")
]

for i, (name, cmd) in enumerate(commands, 1):
    print(f"{i}. {name}:")
    print(f"   {cmd}")
    print()

# =============================================================================
# RESULTS SUMMARY
# =============================================================================

print()
print("📈 WHAT YOU'LL GET")
print("=" * 80)
print()

results = [
    "✅ 6 production-ready business models",
    "✅ Automatic constraint checking (17 total constraints)",
    "✅ Multi-scenario risk analysis",
    "✅ Data-driven parameter calibration",
    "✅ Professional reports and analysis",
    "✅ Reusable templates for your business",
    "✅ Complete audit trail via provenance",
    "✅ Type-safe, validated projections"
]

for result in results:
    print(f"  {result}")

print()
print("=" * 80)
print()
print("📚 Full Documentation: REAL_WORLD_USAGE_PORTFOLIO.md")
print()
print("🎯 This demonstrates PEL's full potential:")
print("   • Multi-industry applications")
print("   • Executive-ready analysis")
print("   • Constraint-based decision making")
print("   • Data-driven calibration")
print("   • Risk & scenario planning")
print()
print("✨ PEL = Programmable Economic Language for serious business modeling")
print()
