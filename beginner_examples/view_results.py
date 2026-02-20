#!/usr/bin/env python3
"""
Simple results viewer for beginner tutorial
Shows model outputs in human-readable format
"""

import json
import sys
from pathlib import Path


def format_number(value):
    """Format a number with commas for readability."""
    if isinstance(value, (int, float)):
        if value >= 1000:
            return f"{value:,.2f}"
        return f"{value:.2f}"
    return str(value)


def view_results(results_file):
    """Display results in beginner-friendly format."""
    
    if not Path(results_file).exists():
        print(f"❌ File not found: {results_file}")
        print(f"\nMake sure you've run the model first:")
        print(f"  ./pel run MODEL.ir.json --mode deterministic --seed 42 -o {results_file}")
        return
    
    with open(results_file) as f:
        data = json.load(f)
    
    print("=" * 70)
    print(f"📊 PEL Model Results: {data.get('model', {}).get('name', 'Unknown')}")
    print("=" * 70)
    print()
    
    # Status
    status = data.get('status', 'unknown')
    status_icon = "✅" if status == "success" else "❌"
    print(f"{status_icon} Status: {status.upper()}")
    print(f"🔢 Mode: {data.get('mode', 'unknown')}")
    print(f"🎲 Seed: {data.get('seed', 'N/A')}")
    print(f"📅 Timesteps: {data.get('timesteps', 0)} months")
    print()
    
    # Assumptions
    if 'assumptions' in data and data['assumptions']:
        print("📋 Input Assumptions")
        print("-" * 70)
        for assumption in data['assumptions']:
            value = format_number(assumption['value'])
            confidence = int(assumption['confidence'] * 100)
            print(f"  • {assumption['name']}: {value}")
            print(f"    Source: {assumption['source']}")
            print(f"    Confidence: {confidence}%")
            print()
    
    # Variables (results)
    if 'variables' in data and data['variables']:
        print("📈 Calculated Results (over time)")
        print("-" * 70)
        
        for var_name, values in data['variables'].items():
            if not values:
                continue
                
            print(f"\n  {var_name.upper().replace('_', ' ')}")
            print(f"  {'Month':<10} {'Value':>20}")
            print(f"  {'-'*10} {'-'*20}")
            
            # Show first 3 months
            for i in range(min(3, len(values))):
                print(f"  {i:<10} {format_number(values[i]):>20}")
            
            # Show ellipsis if more than 6 months
            if len(values) > 6:
                print(f"  {'...':<10} {'...':>20}")
            
            # Show last 3 months
            if len(values) > 3:
                for i in range(max(3, len(values) - 3), len(values)):
                    print(f"  {i:<10} {format_number(values[i]):>20}")
            
            # Summary stats
            if values:
                start_val = values[0]
                end_val = values[-1]
                growth = ((end_val - start_val) / start_val * 100) if start_val != 0 else 0
                print(f"\n  📊 Change: {format_number(start_val)} → {format_number(end_val)} ({growth:+.1f}%)")
        print()
    
    # Constraint violations
    violations = data.get('constraint_violations', [])
    if violations:
        print("⚠️  Constraint Violations")
        print("-" * 70)
        for v in violations:
            print(f"  • {v.get('constraint', 'Unknown')}: {v.get('message', 'Violated')}")
            print(f"    Timestep: {v.get('timestep', 'N/A')}")
            print(f"    Severity: {v.get('severity', 'unknown').upper()}")
        print()
    else:
        print("✅ No constraint violations")
        print()
    
    # Monte Carlo summary
    if data.get('mode') == 'monte_carlo':
        print("🎲 Monte Carlo Statistics")
        print("-" * 70)
        print(f"  Runs: {data.get('num_runs', 0)}")
        aggregates = data.get('aggregates', {})
        if 'success_rate' in aggregates:
            success_pct = aggregates['success_rate'] * 100
            print(f"  Success rate: {success_pct:.1f}%")
        print()
    
    print("=" * 70)
    print()
    print("💡 Tips:")
    print("  • View raw JSON: cat", results_file)
    print("  • Edit the model: nano MODELNAME.pel")
    print("  • Re-run: ./pel compile ... && ./pel run ...")
    print()


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 view_results.py RESULTS_FILE.json")
        print()
        print("Examples:")
        print("  python3 beginner_examples/view_results.py beginner_examples/coffee_results.json")
        print("  python3 beginner_examples/view_results.py beginner_examples/saas_results.json")
        print()
        return
    
    results_file = sys.argv[1]
    view_results(results_file)


if __name__ == '__main__':
    main()
