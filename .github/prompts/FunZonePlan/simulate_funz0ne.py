"""
Simulation harness for FunZone Plan
- Loads key YAML model files from FunZonePlan/
- Runs deterministic sensitivity (base/downside/upside) and a Monte Carlo simulation
- Outputs summary CSV/JSON in FunZonePlan/output/

Run: python simulate_funz0ne.py
"""
import os
import yaml
import json
import math
import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_FILES = {
    'business': ROOT / 'business_system_model.yaml',
    'capital': ROOT / 'capital_financial_model.yaml',
    'stress': ROOT / 'stress_sensitivity_model.yaml'
}
OUTPUT_DIR = ROOT / 'output'
OUTPUT_DIR.mkdir(exist_ok=True)

def load_yaml(path):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

print('Loading models...')
models = {k: load_yaml(p) for k,p in DATA_FILES.items()}

# Base parameters
base_rev = models['business']['unit_economics']['annual_revenue']
base_costs = models['business']['unit_economics']['annual_costs']
base_ebitda = models['business']['unit_economics']['ebitda']

def numeric_from_maybe(obj):
    if isinstance(obj, (int, float)):
        return obj
    if isinstance(obj, str):
        try:
            return float(obj)
        except:
            return 0.0
    if isinstance(obj, dict):
        s = 0.0
        for v in obj.values():
            s += numeric_from_maybe(v)
        return s
    if isinstance(obj, list):
        s = 0.0
        for v in obj:
            s += numeric_from_maybe(v)
        return s
    return 0.0

print(f'Base revenue per location: {base_rev:,}')

# Deterministic scenarios from stress model (if present)
stress = models['stress']
scenarios = {}
for key in ['downside_case','base_case','upside_case']:
    if key in stress:
        sc = stress[key]
        try:
            rev = sc.get('financial_outcomes',{}).get('annual_revenue_per_location') or sc.get('revenue_assumptions',{}).get('total_revenue_per_location')
            ebitda = sc.get('financial_outcomes',{}).get('ebitda_per_location')
            scenarios[key] = {'revenue': rev, 'ebitda': ebitda}
        except Exception:
            pass

# If not present, fallback to base values
if 'base_case' not in scenarios:
    scenarios['base_case'] = {'revenue': base_rev, 'ebitda': base_ebitda}
if 'downside_case' not in scenarios:
    scenarios['downside_case'] = {'revenue': base_rev*0.82, 'ebitda': base_ebitda*0.2}
if 'upside_case' not in scenarios:
    scenarios['upside_case'] = {'revenue': base_rev*1.16, 'ebitda': base_ebitda*1.15}

# Write deterministic summary
with open(OUTPUT_DIR / 'deterministic_summary.json','w',encoding='utf-8') as f:
    json.dump(scenarios, f, indent=2)
print('Wrote deterministic_summary.json')

# Monte Carlo: sample multipliers for key drivers and compute EBITDA per location
n_iter = 5000
np.random.seed(42)

base = {
    'rev': base_rev,
    'costs': base_costs,
    'ebitda': base_ebitda
}

# Define distributions (percent std of base)
dist = {
    'visits_mul': 0.15,    # visit volume variation
    'price_mul': 0.10,     # revenue per visit / pricing
    'labor_mul': 0.12,     # labor cost pressure
    'fleet_cost_mul': 0.12,# fleet cost variation
    'fixed_costs_mul': 0.06 # fixed cost variation
}

results = []
for i in range(n_iter):
    v = np.random.normal(1, dist['visits_mul'])
    p = np.random.normal(1, dist['price_mul'])
    la = np.random.normal(1, dist['labor_mul'])
    fc = np.random.normal(1, dist['fleet_cost_mul'])
    fx = np.random.normal(1, dist['fixed_costs_mul'])

    rev = base['rev'] * v * p
    # Approximate costs: split base costs into variable and fixed using unit model
    fixed_block = models['business']['cost_structure']['fixed_costs_per_location_annual']
    fixed = numeric_from_maybe(fixed_block.get('total_fixed_annual', fixed_block)) * fx
    # variable baseline: base_costs - base fixed - fleet_network_costs
    fleet_costs_block = models['business']['cost_structure']['network_fleet_costs_per_location']
    fleet_base = numeric_from_maybe(fleet_costs_block.get('depreciation_fleet_share', 0))
    fixed_block = models['business']['cost_structure']['fixed_costs_per_location_annual']
    variable = base['costs'] - numeric_from_maybe(fixed_block.get('total_fixed_annual', fixed_block)) - fleet_base
    # scale variable by visits and labor/pricing
    variable_scaled = variable * v * ((la + p)/2)
    fleet = (numeric_from_maybe(fleet_costs_block.get('equipment_rotation_logistics', 0)) + numeric_from_maybe(fleet_costs_block.get('equipment_maintenance_distributed', 0)) + numeric_from_maybe(fleet_costs_block.get('depreciation_fleet_share', 0))) * fc

    total_costs = fixed + variable_scaled + fleet
    ebitda = rev - total_costs
    results.append({'rev': rev, 'costs': total_costs, 'ebitda': ebitda})

df = pd.DataFrame(results)

summary = {
    'ebitda_per_location': {
        'mean': float(df['ebitda'].mean()),
        'std': float(df['ebitda'].std()),
        'median': float(df['ebitda'].median()),
        'p10': float(df['ebitda'].quantile(0.1)),
        'p25': float(df['ebitda'].quantile(0.25)),
        'p50': float(df['ebitda'].quantile(0.5)),
        'p75': float(df['ebitda'].quantile(0.75)),
        'p90': float(df['ebitda'].quantile(0.9))
    },
    'rev_per_location': {
        'mean': float(df['rev'].mean()),
        'p50': float(df['rev'].median())
    }
}

with open(OUTPUT_DIR / 'monte_carlo_summary.json','w',encoding='utf-8') as f:
    json.dump(summary, f, indent=2)

# Save full sample percentiles to CSV (for detail)
df.describe().to_csv(OUTPUT_DIR / 'monte_carlo_describe.csv')
print('Monte Carlo complete. Wrote outputs to', OUTPUT_DIR)

# --- DCF / Valuation from capital model ---
cap = models['capital']
cf = cap['cash_flow_projections']
discount = cap.get('meta',{}).get('discount_rate', cap.get('dcf_method',{}).get('discount_rate', 0.14))
# gather operating cash flows years 1-5
years = ['year_1_2026','year_2_2027','year_3_2028_steady_state','year_4_2029_expansion','year_5_2030_scaled']
fcfs = []
for y in years:
    yc = cf.get(y,{})
    fcfs.append(float(yc.get('operating_cash_flow',0)))

# terminal value using enterprise value approach from file
ev_block = cap.get('cumulative_financial_summary',{}).get('enterprise_value_exit_year_5',{})
terminal_ev = float(ev_block.get('enterprise_value',0))

# PV calculation
pv = 0.0
for i,cash in enumerate(fcfs, start=1):
    pv += cash / ((1+discount)**i)
pv_terminal = terminal_ev / ((1+discount)**5)
npv_total = pv + pv_terminal

# equity value (enterprise - net debt)
net_debt = float(ev_block.get('less_net_debt',0))
equity_value = float(ev_block.get('equity_value', npv_total + net_debt))

dcf_summary = {
    'discount_rate': discount,
    'pv_operating_cashflows': pv,
    'pv_terminal_ev': pv_terminal,
    'npv_total_enterprise_equivalent': npv_total,
    'enterprise_value_reported': terminal_ev,
    'net_debt_reported': net_debt,
    'equity_value_reported': equity_value
}
with open(OUTPUT_DIR / 'dcf_summary.json','w',encoding='utf-8') as f:
    json.dump(dcf_summary, f, indent=2)

# IRR for equity: initial equity outflow and final equity value
initial_equity = float(cap.get('capital_structure',{}).get('recommended_mix',{}).get('equity_capital',{}).get('amount',2827500))
cashflows_equity = [-initial_equity] + [0,0,0,0, float(equity_value)]
try:
    irr_eq = np.irr(cashflows_equity)
except Exception:
    irr_eq = None
dcf_summary['equity_irr_from_cashflows'] = float(irr_eq) if irr_eq is not None else None
with open(OUTPUT_DIR / 'dcf_summary.json','w',encoding='utf-8') as f:
    json.dump(dcf_summary, f, indent=2)
print('DCF complete. Wrote', OUTPUT_DIR / 'dcf_summary.json')


# --- Sequential shock stress tests (compounding shocks) ---
def summarize_deterministic(models_local):
    # extract simple revenue/ebitda from business unit economics where possible
    bus = models_local.get('business', {})
    unit = bus.get('unit_economics', {})
    rev = numeric_from_maybe(unit.get('annual_revenue', unit.get('revenue_per_location', 0)))
    ebitda = numeric_from_maybe(unit.get('ebitda', unit.get('ebitda_per_location', 0)))

    # DCF quick recompute using capital block if present
    cap_local = models_local.get('capital', {})
    cf_local = cap_local.get('cash_flow_projections', {})
    discount_local = cap_local.get('meta',{}).get('discount_rate', cap_local.get('dcf_method',{}).get('discount_rate', 0.14))
    yrs = ['year_1_2026','year_2_2027','year_3_2028_steady_state','year_4_2029_expansion','year_5_2030_scaled']
    fcfs_local = []
    for y in yrs:
        yc = cf_local.get(y, {})
        fcfs_local.append(float(yc.get('operating_cash_flow', 0)))
    pv_local = 0.0
    for i,cash in enumerate(fcfs_local, start=1):
        pv_local += cash / ((1+discount_local)**i)
    ev_block_local = cap_local.get('cumulative_financial_summary',{}).get('enterprise_value_exit_year_5',{})
    terminal_ev_local = float(ev_block_local.get('enterprise_value', 0))
    pv_terminal_local = terminal_ev_local / ((1+discount_local)**5)
    npv_local = pv_local + pv_terminal_local
    return {
        'revenue': rev,
        'ebitda': ebitda,
        'pv_operating_cashflows': pv_local,
        'pv_terminal_ev': pv_terminal_local,
        'npv_total_enterprise_equivalent': npv_local
    }


def copy_models(models_src):
    import copy
    return copy.deepcopy(models_src)


def apply_percent_to_key(models_dict, path, pct):
    node = models_dict
    for p in path[:-1]:
        node = node.get(p, {})
    key = path[-1]
    if key in node:
        val = node[key]
        try:
            node[key] = numeric_from_maybe(val) * (1 + pct)
        except Exception:
            pass


def run_sequential_shocks(models_all):
    base_sum = summarize_deterministic(models_all)
    shocked = copy_models(models_all)

    # sequential shocks
    apply_percent_to_key(shocked, ['business', 'unit_economics', 'annual_revenue'], -0.25)
    apply_percent_to_key(shocked, ['business', 'unit_economics', 'avg_price_per_visit'], -0.10)
    apply_percent_to_key(shocked, ['capital', 'maintenance_capex_per_location', 'annual_steady_state'], 0.30)
    apply_percent_to_key(shocked, ['regulatory_risk', 'consolidated_risk_budget_per_location'], 0.20)

    shocked_sum = summarize_deterministic(shocked)
    return {'base': base_sum, 'sequential_shock': shocked_sum}


try:
    seq_out = run_sequential_shocks(models)
    with open(OUTPUT_DIR / 'sequential_shocks.json','w',encoding='utf-8') as f:
        json.dump(seq_out, f, indent=2)
    print('Wrote sequential_shocks.json')
except Exception as e:
    print('Sequential shock tests failed:', e)
