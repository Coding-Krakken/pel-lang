# Process Optimization & Operational Excellence

Frameworks for improving operational efficiency, quality, and capacity.

**When to use**:
- Manufacturing and production
- Service delivery optimization
- Quality improvement
- Capacity planning

================================================================================
LEAN PRINCIPLES
================================================================================

Create: `/business/models/operations/lean_analysis.yaml`

```yaml
value_stream_map:
  current_state:
    - step: "Order received"
      value_added: No
      time: 1 hour
    - step: "Production"
      value_added: Yes
      time: 4 hours
    - step: "Wait for inspection"
      value_added: No
      time: 2 hours
      
seven_wastes:
  transportation: "Moving materials unnecessarily"
  inventory: "Excess WIP and finished goods"
  motion: "Unnecessary movement of people"
  waiting: "Idle time"
  overproduction: "Making more than needed"
  overprocessing: "More work than customer values"
  defects: "Rework and scrap"
  
metrics:
  takt_time: "Available time / customer demand"
  cycle_time: "Actual time per unit"
  lead_time: "Order to delivery"
  
future_state:
  eliminate_waste: "Reduce lead time by X%"
  one_piece_flow: "Reduce batch sizes"
  pull_system: "Produce to actual demand"
```

================================================================================
SIX SIGMA / DMAIC
================================================================================

Create: `/business/models/operations/six_sigma_project.yaml`

```yaml
define:
  problem: "Defect rate too high"
  current_performance: "15% defects"
  goal: "< 3% defects"
  financial_impact: "$Xk/year"
  
measure:
  ctq: "Critical to Quality characteristics"
  measurement_system: "Gage R&R acceptable"
  baseline: "Mean = X, Std Dev = Y"
  process_capability:
    cp: "(USL - LSL) / 6σ"
    cpk: "Min((USL - μ)/3σ, (μ - LSL)/3σ)"
    
analyze:
  root_causes:
    - "Temperature variation"
    - "Raw material quality"
  statistical_validation: "ANOVA, regression"
  pareto: "80% of defects from 20% of causes"
  
improve:
  solutions:
    - "Install temperature controls"
    - "Supplier qualification"
  pilot_results: "Defect rate = 2.5%"
  
control:
  control_plan: "SPC charts on key variables"
  reaction_plan: "If out of control, investigate"
  training: "Operators trained on new process"
```

================================================================================
QUEUEING THEORY & CAPACITY OPTIMIZATION
================================================================================

Create: `/business/models/operations/queueing_model.yaml`

```yaml
system_type: "M/M/c (Poisson arrivals, Exponential service, c servers)"

parameters:
  arrival_rate: λ = 50 per hour
  service_rate: μ = 20 per hour (per server)
  servers: c = 3
  
utilization: ρ = λ/(c*μ) = 50/(3*20) = 0.83

performance_metrics:
  average_wait_time: "W_q formula"
  average_system_time: "W = W_q + 1/μ"
  average_queue_length: "L_q = λ * W_q"
  probability_wait: "P(wait > 0)"
  
service_level:
  target: "90% served within 5 minutes"
  current: "75%"
  servers_needed: "c = 4 to meet target"
  
capacity_planning:
  scenarios:
    - peak_demand: λ = 80
      servers_needed: 5
    - promotion: λ = 120
      servers_needed: 7
```

================================================================================
SUPPLY CHAIN OPTIMIZATION
================================================================================

Create: `/business/models/operations/supply_chain_optimization.yaml`

```yaml
network_design:
  nodes:
    suppliers: ["S1", "S2", "S3"]
    warehouses: ["W1", "W2"]
    customers: ["C1", "C2", "C3", "C4"]
  arcs:
    - from: "S1"
      to: "W1"
      capacity: 1000 units
      cost: $5/unit
      lead_time: 3 days
      
optimization_problem:
  objective: "Minimize total cost"
  decision_variables: "Flow on each arc"
  constraints:
    - "Supply  capacity at sources"
    - "Demand satisfaction at customers"
    - "Capacity constraints on arcs and nodes"
    - "Service level requirements"
    
inventory_policy:
  eoq: "Optimal order quantity"
  safety_stock: "Z * σ * sqrt(L)"
  reorder_point: "Demand during lead time + safety stock"
  
risk_mitigation:
  supplier_diversification: "Don't rely on single source"
  nearshoring: "Balance cost vs resilience"
```

================================================================================
STATISTICAL PROCESS CONTROL (SPC)
================================================================================

Create: `/business/models/operations/spc_framework.yaml`

```yaml
monitored_metrics:
  - metric: "Defect rate"
    chart_type: "p-chart (proportion)"
    sample_size: 100
    sampling_frequency: "Hourly"
    
control_limits:
  centerline: "Process average"
  ucl: "Upper Control Limit = μ + 3σ"
  lcl: "Lower Control Limit = μ - 3σ"
  
out_of_control_rules:
  - "Point beyond control limits"
  - "7 consecutive points on same side of center"
  - "Trend of 7 increasing/decreasing points"
  
reaction_protocol:
  if_out_of_control:
    - "Stop process"
    - "Investigate root cause"
    - "Implement corrective action"
    - "Verify return to control"
```