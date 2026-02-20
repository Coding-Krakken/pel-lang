#!/usr/bin/env python3
"""
Analyze Monte Carlo simulation results from PEL
Shows statistical distribution of outcomes
"""

import json
import sys
from statistics import mean, median, stdev

def analyze_monte_carlo(filename):
    with open(filename, 'r') as f:
        results = json.load(f)
    
    if results['mode'] != 'monte_carlo':
        print(f"❌ This is not a Monte Carlo result file (mode: {results['mode']})")
        return
    
    num_runs = results['num_runs']
    runs = results['runs']
    
    print("=" * 70)
    print(f"🎲 Monte Carlo Analysis: {num_runs} simulations")
    print("=" * 70)
    print()
    
    # Get model name from first run
    model_name = runs[0]['model']['name']
    print(f"📊 Model: {model_name}")
    print(f"✅ Successful runs: {len([r for r in runs if r['status'] == 'success'])}/{num_runs}")
    print()
    
    # Analyze each variable
    if runs[0]['variables']:
        var_names = runs[0]['variables'].keys()
        
        for var_name in var_names:
            print(f"\n{'=' * 70}")
            print(f"📈 Variable: {var_name.upper().replace('_', ' ')}")
            print(f"{'=' * 70}")
            
            # Get final values (last timestep) from all runs
            final_values = []
            for run in runs:
                if run['status'] == 'success' and var_name in run['variables']:
                    values = run['variables'][var_name]
                    if isinstance(values, list) and len(values) > 0:
                        final_values.append(values[-1])
                    elif isinstance(values, (int, float)):
                        final_values.append(values)
            
            if final_values:
                # Calculate statistics
                avg = mean(final_values)
                med = median(final_values)
                std = stdev(final_values) if len(final_values) > 1 else 0
                min_val = min(final_values)
                max_val = max(final_values)
                
                # Percentiles
                sorted_vals = sorted(final_values)
                p10 = sorted_vals[int(len(sorted_vals) * 0.10)]
                p25 = sorted_vals[int(len(sorted_vals) * 0.25)]
                p75 = sorted_vals[int(len(sorted_vals) * 0.75)]
                p90 = sorted_vals[int(len(sorted_vals) * 0.90)]
                
                print(f"\nFinal Value Statistics (Month {runs[0]['timesteps'] - 1}):")
                print(f"  Average (Mean):    {avg:>15,.2f}")
                print(f"  Median (50th %):   {med:>15,.2f}")
                print(f"  Std Deviation:     {std:>15,.2f}")
                print()
                print(f"Range:")
                print(f"  Minimum:           {min_val:>15,.2f}")
                print(f"  10th percentile:   {p10:>15,.2f}  (10% chance worse)")
                print(f"  25th percentile:   {p25:>15,.2f}  (25% chance worse)")
                print(f"  75th percentile:   {p75:>15,.2f}  (75% chance worse)")
                print(f"  90th percentile:   {p90:>15,.2f}  (90% chance worse)")
                print(f"  Maximum:           {max_val:>15,.2f}")
                print()
                print(f"Confidence Intervals:")
                print(f"  50% of outcomes:   {p25:>15,.2f} to {p75:>15,.2f}")
                print(f"  80% of outcomes:   {p10:>15,.2f} to {p90:>15,.2f}")
    
    print()
    print("=" * 70)
    print("\n💡 What this means:")
    print("   - The median is the 'typical' outcome (50% above, 50% below)")
    print("   - The 10th-90th percentile range shows likely outcomes")
    print("   - Wide ranges indicate high uncertainty")
    print()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 analyze_mc.py <monte_carlo_results.json>")
        sys.exit(1)
    
    analyze_monte_carlo(sys.argv[1])
