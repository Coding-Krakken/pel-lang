# Optimization & Advanced Simulation

Advanced simulation and optimization techniques for complex systems and uncertainty.

**When to use**:
- Complex systems with feedback loops
- Emergent behavior modeling
- Optimization under uncertainty
- Resource allocation

================================================================================
SYSTEM DYNAMICS MODELING
================================================================================

**Purpose**: Model feedback loops and accumulations

Create: `/business/models/simulations/system_dynamics_model.yaml`

```yaml
stocks:
  - name: "Customer base"
    initial_value: 1000
    units: "customers"
  - name: "Cash"
    initial_value: $100k
    
flows:
  - name: "New customers"
    formula: "Marketing spend * conversion rate"
    into_stock: "Customer base"
  - name: "Churn"
    formula: "Customer base * churn rate"
    out_of_stock: "Customer base"
    
feedback_loops:
  reinforcing:
    - "More customers → more revenue → more marketing → more customers"
  balancing:
    - "More customers → capacity strain → worse service → more churn"
    
simulation:
  time_step: "Month"
  duration: "60 months"
  scenarios:
    - "Base case"
    - "High growth"
    - "Capacity constrained"
```

================================================================================
AGENT-BASED MODELING (ABM)
================================================================================

**Purpose**: Model emergent behavior from individual actions

Create: `/business/models/simulations/agent_based_model.yaml`

```yaml
agents:
  customers:
    count: 10000
    attributes:
      willingness_to_pay: "Normal(μ=100, σ=20)"
      price_sensitivity: "Uniform(0.5, 1.5)"
      social_influence: "Beta(2, 5)"
    behaviors:
      purchase_decision: "Logit model with price, quality, peer influence"
      churn_decision: "If satisfaction < threshold"
      
  competitors:
    count: 3
    strategies:
      pricing: "Match | Premium | Discount"
      quality: "Invest to improve"
      
environment:
  market_growth: "2% per period"
  economic_shock_probability: 0.05
  
interactions:
  word_of_mouth: "Satisfied customers influence neighbors"
  competitive_response: "Competitors react to market share"
  
simulation:
  time_steps: 100
  replications: 50
  outputs:
    market_share_distribution: "Per company"
    price_equilibrium: "Emergent pricing"
    network_formation: "Customer influence clusters"
```

================================================================================
STOCHASTIC PROGRAMMING
================================================================================

**Purpose**: Optimization with revealed uncertainty

Create: `/business/models/optimization/stochastic_program.yaml`

```yaml
two_stage_model:
  first_stage_decision:
    variables: ["Capacity to build", "Inventory to stock"]
    cost: $X
    constraints: "Budget, space"
    
  scenarios:
    - scenario: "High demand"
      probability: 0.3
      demand: 10000 units
    - scenario: "Medium demand"
      probability: 0.5
      demand: 7000 units
    - scenario: "Low demand"
      probability: 0.2
      demand: 4000 units
      
  second_stage_decision:
    variables: ["Production adjustment", "Overtime", "Lost sales"]
    recourse_cost: $Y per scenario
    
  objective: "Minimize first stage cost + expected recourse cost"
  
value_of_stochastic_solution:
  vss: "Cost(deterministic with mean) - Cost(stochastic)"
  interpretation: "Benefit of modeling uncertainty"
```

================================================================================
ROBUST OPTIMIZATION
================================================================================

**Purpose**: Worst-case protection

Create: `/business/models/optimization/robust_optimization.yaml`

```yaml
decision: "Portfolio allocation"
uncertainty_set:
  parameter: "Asset returns"
  range: "Historical min/max ± X%"
  
robustness_criterion:
  minimax: "Minimize worst-case loss"
  minimax_regret: "Minimize worst-case regret vs optimal"
  
gamma_robustness:
  gamma: "Number of parameters allowed to be at worst case"
  tradeoff: "γ=0 (nominal) to γ=N (fully robust)"
  
solution:
  robust_decision: "Works well across all scenarios in uncertainty set"
  cost_of_robustness: "X% worse in best case"
  insurance_value: "Y% better in worst case"
```

================================================================================
MONTE CARLO WITH LATIN HYPERCUBE SAMPLING
================================================================================

Create: `/business/models/simulations/monte_carlo_lhs.yaml`

```yaml
sampling_method: "Latin Hypercube (more efficient than pure random)"
iterations: 10000
seed: 42 (for reproducibility)

uncertain_variables:
  - variable: "Revenue growth rate"
    distribution: "Normal(μ=0.15, σ=0.05)"
  - variable: "Customer acquisition cost"
    distribution: "Lognormal(μ=100, σ=20)"
  - variable: "Churn rate"
    distribution: "Beta(α=2, β=18)"
    
correlation_matrix:
  rev_growth_vs_cac: -0.3
  
outputs:
  - metric: "NPV"
    percentiles: [P10, P25, P50, P75, P90]
    probability_positive: X%
  - metric: "IRR"
    distribution: "Histogram"
    var_95: "Value at Risk"
    cvar_95: "Conditional VaR"
```

================================================================================
DISCRETE EVENT SIMULATION (DES)
================================================================================

Create: `/business/models/simulations/discrete_event_sim.yaml`

```yaml
entities: "Customers, Orders"
resources:
  - resource: "Service agents"
    count: 10
    schedule: "24/7 | Business hours"
    
arrival_process:
  distribution: "Poisson(λ=50/hour)"
  
service_process:
  distribution: "Lognormal(μ=15min, σ=5min)"
  
routing:
  priority_queue: "VIP customers served first"
  
metrics:
  utilization: "Agent busy time / total time"
  wait_time: "Time in queue"
  system_time: "Wait + service"
  throughput: "Customers served / hour"
  service_level: "% served within SLA"
  
optimization:
  staffing_levels: "Minimize cost subject to service level"
```