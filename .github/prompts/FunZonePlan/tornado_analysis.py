"""Tornado sensitivity analysis for FunZone
Produces a horizontal bar chart showing NPV sensitivity to +/-10% changes
in top drivers and writes `output/tornado_data.csv` and `output/tornado.png`.
"""
from pathlib import Path
import yaml
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / 'output'
OUTPUT.mkdir(exist_ok=True)

def load_yaml(p):
    with open(p,'r',encoding='utf-8') as f:
        return yaml.safe_load(f)

def numeric_from_maybe(obj):
    if isinstance(obj,(int,float)):
        return obj
    if isinstance(obj,str):
        try:
            return float(obj)
        except:
            return 0.0
    if isinstance(obj,dict):
        s=0.0
        for v in obj.values():
            s+=numeric_from_maybe(v)
        return s
    if isinstance(obj,list):
        s=0.0
        for v in obj:
            s+=numeric_from_maybe(v)
        return s
    return 0.0

def compute_enterprise_npv(models):
    cap = models.get('capital',{})
    cf = cap.get('cash_flow_projections',{})
    discount = cap.get('meta',{}).get('discount_rate', cap.get('dcf_method',{}).get('discount_rate',0.14))
    years = ['year_1_2026','year_2_2027','year_3_2028_steady_state','year_4_2029_expansion','year_5_2030_scaled']
    pv=0.0
    for i,y in enumerate(years, start=1):
        cash = float(cf.get(y,{}).get('operating_cash_flow',0))
        pv += cash/((1+discount)**i)
    ev_block = cap.get('cumulative_financial_summary',{}).get('enterprise_value_exit_year_5',{})
    terminal_ev = float(ev_block.get('enterprise_value',0))
    pv_terminal = terminal_ev/((1+discount)**5)
    return pv+pv_terminal

def copy_models(m):
    import copy
    return copy.deepcopy(m)

def apply_percent(models, path, pct):
    node = models
    for p in path[:-1]:
        node = node.get(p, {})
    k = path[-1]
    if k in node:
        node[k] = numeric_from_maybe(node[k])*(1+pct)

if __name__=='__main__':
    # load models
    models = {
        'business': load_yaml(ROOT/'business_system_model.yaml'),
        'capital': load_yaml(ROOT/'capital_financial_model.yaml'),
        'stress': load_yaml(ROOT/'stress_sensitivity_model.yaml')
    }

    base_npv = compute_enterprise_npv(models)

    drivers = {
        'visit_volume': (['business','unit_economics','annual_revenue'], True),
        'price_per_visit': (['business','unit_economics','avg_price_per_visit'], True),
        'labor_costs': (['business','cost_structure','labor_costs_per_location_annual'], False),
        'fleet_maintenance': (['capital','maintenance_capex_per_location','annual_steady_state'], False),
        'fixed_costs': (['business','cost_structure','fixed_costs_per_location_annual','total_fixed_annual'], False),
        'risk_budget': (['regulatory_risk','consolidated_risk_budget_per_location'], False),
        'discount_rate': (['capital','meta','discount_rate'], False)
    }

    records = []
    for name,(path,is_revenue) in drivers.items():
        m_up = copy_models(models)
        m_down = copy_models(models)

        pct = 0.10
        # For discount rate, invert direction meaningfully
        if name=='discount_rate':
            # +10% on discount rate means increase rate
            apply_percent(m_up, path, pct)
            apply_percent(m_down, path, -pct)
        else:
            apply_percent(m_up, path, pct)
            apply_percent(m_down, path, -pct)

        npv_up = compute_enterprise_npv(m_up)
        npv_down = compute_enterprise_npv(m_down)
        impact = (npv_up - npv_down)/2.0
        records.append({'driver': name, 'npv_base': base_npv, 'npv_up': npv_up, 'npv_down': npv_down, 'impact_abs': abs(impact)})

    df = pd.DataFrame(records).sort_values('impact_abs', ascending=True)
    df.to_csv(OUTPUT/'tornado_data.csv', index=False)

    # Plot
    try:
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(8,4))
        ax.barh(df['driver'], df['impact_abs'], color='C0')
        ax.set_xlabel('Absolute NPV impact (average of +/-10%)')
        ax.set_title('Tornado — Top drivers (10% shock)')
        plt.tight_layout()
        plt.savefig(OUTPUT/'tornado.png', dpi=150)
        print('Wrote tornado.png and tornado_data.csv')
    except Exception as e:
        print('Plotting failed:', e)
        print('Wrote tornado_data.csv')
