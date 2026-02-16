**Business Modeling — README**

This document describes the full, model-first process for creating, validating, reconciling, and stress-testing canonical business models in this folder. It maps the phases in `designModel.prompt.md`, the automated validation/reconciliation pipeline, and the simulation/stress-test suite the agent will run once models are created.

**Quick Start**
- **Location:** Business modelling prompt: [Business/designModel.prompt.md](Business/designModel.prompt.md)
- **Primary goal:** Produce canonical YAML models for the business, industry, capital, risk, competitive dynamics, scalability, and stress scenarios, then validate, reconcile with synthesis, and run simulations.
- **Workflow:** Model → Validate → Reconcile → Simulate → Synthesize.

**Process Overview**
- **Phase -1 (Meta):** Domain classification and complexity budget. Output: classification metadata.
- **Phase 0 (Business System Model):** Produce canonical YAML with core offering, customers, revenue streams, cost structure, unit economics, invariants, and failure conditions.
- **Phase 1 (Industry Structure):** Produce canonical YAML describing TAM/SAM/SOM, entry barriers, supplier/buyer power, and industry norms.
- **Phase 2 (Economic Environment):** Macro drivers, interest/inflation exposure, labor and currency sensitivity.
- **Phase 3 (Capital & Financial):** Startup capital, working capital, cashflow projection skeletons, capex cycles, valuation framework.
- **Phase 4 (Competitive Dynamics):** Positioning, moat analysis, network effects, price/volume levers.
- **Phase 5 (Regulatory & Risk):** Licensing, compliance, liability, political/regulatory change vectors.
- **Phase 6 (Scalability):** Replication model, marginal returns, geographic constraints.
- **Phase 7 (Stress & Sensitivity):** Define base/downside/upside scenarios and stress cases.
- **Phase 8 (Validation — automated):** Programmatic checks for cash-flow reconciliation, unit economics, capacity constraints, invariants. Produces a validation report and blocks progress on failures.
- **Phase 9 (Synthesis):** After green validation/reconciliation, produce executive summary, capital recommendation, scaling roadmap, and timing guidance.

**File & Artifact Conventions**
- **Model canonical files:** place YAML models in Business/model/ (one file per phase, e.g., `business_system_model.yaml`).
- **Validation report:** `/business/model/validation_report.json` (machine-readable list of failures, keys, and severities).
- **Reconciliation report:** `/business/model/reconciliation_report.md` (human readable mismatches and corrective suggestions).
- **Simulations directory:** `/business/simulations/<timestamp>/` — stores seeds, inputs, raw outputs, and consolidated report.
- **Final synthesis:** write the Phase 9 executive synthesis next to the models as `business_synthesis.md`.

**Automated Validation & Reconciliation (Detailed)**
- **Blocking checks:** cash flows reconcile (inflows = outflows + ending balances), unit economics internal consistency (LTV, CAC, contribution margin), capacity vs demand constraints, and mandatory invariants.
- **Output:** `validation_report.json` with record entries: {file, yaml_path, check_id, severity, message}.
- **Reconciliation step:** compare numeric values and named state-variables in the Phase 9 synthesis against canonical YAML values. Output `reconciliation_report.md` with suggested minimal fixes and confidence levels.
- **Blocking behavior:** pipeline must halt on any `severity: high` validation failures; user decision required to continue.

**Simulation & Stress‑Testing Suite (Detailed)**
- **A. Deterministic Scenarios:** run Base / Downside / Upside with fixed parameter vectors. Produce cashflow timelines, IRR, MOIC, solvency flag, and 1‑page summary per case.
- **B. Multi‑way Sensitivity:** compute top drivers by delta-IRR, produce tornado charts and two‑way tables for the top 4 drivers (CSV + PNG/SVG outputs).
- **C. Monte‑Carlo (Probabilistic):** default distribution suggestions and iterations:
  - `visit_frequency` ~ Normal(mu, sigma)
  - `price` ~ Triangular(min, mode, max)
  - `labor_cost` ~ Lognormal(mu, sigma)
  - Default iterations: `10000` (configurable; allowed range 5000–20000)
  - Outputs: IRR distribution, MOIC distribution, insolvency probability, 95%/99% VaR, percentile bands, and plots (histograms, CDFs).
- **D. Sequential Shock Tests:** apply ordered shocks (e.g., recession → rate spike → insurance cost jump) and record covenant breach timing, liquidity shortfall, and suggested remedial capital.
- **E. Operational Event/Queue Simulation:** discrete-event simulation of arrivals vs service capacity (Poisson arrivals or empirical trace). Outputs: utilization, queue lengths, wait-time percentiles, and staff-scheduling recommendations.
- **F. Catastrophic Failure Mode:** single-event simulation of safety incident modeling cash burn, legal exposure, insurer reaction, and reputational revenue loss. Output tolerances and worst-case runway.

**Outputs & Reporting**
- **Machine-readable:** JSON/CSV for all numeric outputs. Example: `montecarlo_summary.json`, `sensitivity_table.csv`.
- **Visuals:** PNG/SVG charts for tornado, histograms, CDFs, time-series traces.
- **Human summaries:** `report.pdf` and `report.md` in the simulations folder with executive takeaways, top drivers, insolvency probability, recommended liquidity buffer, and prioritized mitigations.

**Reproducibility & Auditability**
- **Seeds & provenance:** record RNG seed, software version, and parameter set used for every simulation in the simulations folder.
- **Config file:** provide a single `sim_config.yaml` alongside each run with distribution definitions, fixed parameters, and run-size.
- **Confidence levels:** each simulated assumption should include a confidence tag: high/medium/low; low-confidence results must be flagged in executive summary.

**Recommended Tools & Libraries**
- **Data & numerics:** `numpy`, `pandas`, `scipy`.
- **Monte‑Carlo / stats:** `scipy.stats`, or `chaospy` for advanced distributions.
- **Plotting:** `matplotlib`, `seaborn`, or `plotly` for interactive charts.
- **Simulations:** `simpy` (Python) for discrete event simulation, or lightweight custom event queues for speed.
- **Reporting:** `pandoc` or `wkhtmltopdf` to build PDF reports from markdown.

**Example CLI (illustrative)**
```bash
# Run validation and reconciliation only
python tools/run_pipeline.py --models Business/model --validate --reconcile

# Run full pipeline including Monte‑Carlo (10k iterations)
python tools/run_pipeline.py --models Business/model --simulate --montecarlo 10000 --out Business/simulations
```

**Compute Considerations & Defaults**
- **Default MC iterations:** `10000` (good balance of precision and runtime). Reduce to `1000` for a quick pilot.
- **Parallelization:** recommend using joblib or multiprocessing for MC runs if CPU cores available.
- **Approximations:** if compute constrained, run moment-matching or lower iteration pilots and mark their confidence as `low`.

**Next Steps / How to use this folder**
- **1:** Author canonical YAML models following Phase 0–7 and place them in `Business/model/`.
- **2:** Run the validation pipeline. Fix high-severity validation failures.
- **3:** Reconcile the Phase 9 synthesis with the canonical YAML values.
- **4:** Run simulations (deterministic → sensitivity → Monte‑Carlo → shocks → operational → catastrophic).
- **5:** Review `Business/simulations/<t>/report.md` and iterate the model or assumptions as needed.

If you want, I can scaffold `Business/model/` with starter YAML files and create a small `tools/run_pipeline.py` prototype to run the validation + Monte‑Carlo pipeline.

---
Generated by the modeling assistant — concise, reproducible, and audit-ready.
