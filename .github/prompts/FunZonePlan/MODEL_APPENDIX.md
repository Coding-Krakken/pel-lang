Model Appendix — FunZone

1) Location of models
- Business system model: [FunZonePlan/business_system_model.yaml](FunZonePlan/business_system_model.yaml)
- Capital & financial model: [FunZonePlan/capital_financial_model.yaml](FunZonePlan/capital_financial_model.yaml)
- Stress & sensitivity: [FunZonePlan/stress_sensitivity_model.yaml](FunZonePlan/stress_sensitivity_model.yaml)

2) Key reconciled assumptions (conservative defaults used in runs)
- Maintenance capex per location (steady state): $85,000
- Consolidated risk mitigation budget per location: $195,000
- Minimum cash reserve per location: $90,000

3) Simulation methodology
- Deterministic scenarios: downside/base/upside from `stress_sensitivity_model.yaml`.
- Monte‑Carlo: 5,000 iterations sampling visit volume, price, labor, fleet costs, fixed costs (see `simulate_funz0ne.py`).
- DCF: 5‑year operating cash flows + terminal enterprise value from the capital model; discount rate = 14% (model meta).

4) Outputs produced
- `FunZonePlan/output/deterministic_summary.json`
- `FunZonePlan/output/monte_carlo_summary.json`
- `FunZonePlan/output/monte_carlo_describe.csv`
- `FunZonePlan/output/dcf_summary.json`
- `FunZonePlan/output/sequential_shocks.json`

5) How to reproduce
1. Activate the workspace virtualenv (see .venv in workspace).
2. Install required Python packages: `pyyaml`, `numpy`, `pandas`, `matplotlib`.
3. Run: `python FunZonePlan/simulate_funz0ne.py` then `python FunZonePlan/tornado_analysis.py`.
