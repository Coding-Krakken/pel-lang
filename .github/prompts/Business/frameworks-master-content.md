# BUSINESS ENGINEERING FRAMEWORKS - MASTER CONTENT FILE
# =====================================================
# This file contains all framework content for the modular copilot-instructions system
# Use the extraction script (extract-frameworks.ps1) to populate individual files
#
# FILE STRUCTURE:
# - Each framework file starts with: ### FILE: filename.md
# - Content follows until next ### FILE: marker
# - Files are extracted based on these markers

### FILE: strategic-frameworks.md

# Advanced Strategic Frameworks

This document contains advanced strategic analysis frameworks for specialized business analysis beyond core business formation.

**When to use these frameworks:**
- User explicitly requests a specific framework
- Business context clearly requires deep strategic analysis  
- Core 10-phase analysis reveals need for specialized methodology
- Platform, network effects, or competitive dynamics are critical

**How to use:**
1. Select appropriate framework based on business type and strategic question
2. Read and understand framework structure
3. Gather required data from existing models or stakeholder input
4. Apply framework systematically
5. Create framework-specific model file in `/business/models/strategy/`
6. Integrate findings into core strategic documents
7. Update risk register and decision log

================================================================================
WARDLEY MAPPING
================================================================================

**Purpose**: Situational awareness, evolution analysis, strategic positioning

**When to use**:
- Technology-intensive businesses
- Rapidly evolving markets
- Platform strategy decisions
- Build vs buy decisions
- Identifying commoditization trends

## Framework Structure

Create: `/business/models/strategy/wardley_map.yaml`

### Components

Define for each value chain component:

```yaml
component_name:
  description: "What this component does"
  user_need_served: "Which user need this addresses"
  evolution_stage: "Genesis | Custom-Built | Product | Commodity"
  visibility: "High | Medium | Low (to end users)"
  position_y: 0.0-1.0  # Value chain (user=1.0, infrastructure=0.0)
  position_x: 0.0-1.0  # Evolution (genesis=0.0, commodity=1.0)
  dependencies: ["component it depends on"]
  inertia: "Low | Medium | High"
```

### Evolution Characteristics

- **Genesis (0.0-0.25)**: Unique, rare, uncertain, high margin
- **Custom-Built (0.25-0.50)**: Bespoke, artisanal, many vendors
- **Product (0.50-0.75)**: Standardized, operational excellence, fewer players
- **Commodity (0.75-1.0)**: Ubiquitous, cost-based, dominant players

### Strategic Movements

```yaml
strategic_movements:
  - type: "Build | Buy | Partner | Outsource"
    component: "Name"
    rationale: "Why"
    timing: "When"
    risk: "Level"
```

================================================================================
7 POWERS FRAMEWORK (Hamilton Helmer)
================================================================================

**Purpose**: Identify durable competitive advantages

**When to use**: Assessing competitive moat depth, investment decisions, defensive strategy

## The Seven Powers

Create: `/business/models/strategy/seven_powers_analysis.yaml`

### 1. Scale Economies
```yaml
scale_economies:
  unit_cost_decline_rate: "% per doubling"
  minimum_efficient_scale: N units
  current_position: "Below | At | Above MES"
  barrier_strength: "Weak | Strong"
```

### 2. Network Effects
```yaml
network_effects:
  type: "Direct | Indirect | Two-Sided"
  critical_mass: N users
  multi_homing_cost: "Low | High"
  winner_take_all: Yes/No
```

### 3. Counter-Positioning
```yaml
counter_positioning:
  incumbent_model: "Description"
  alternative_model: "Your approach"
  adoption_barrier: "Cannibalization cost"
```

### 4. Switching Costs
```yaml
switching_costs:
  financial: $X
  procedural: "Migration effort"
  relational: "Relationship value"
  retention_lift: "+X%"
```

### 5. Branding
```yaml
branding:
  brand_premium: "X% price premium"
  trust_score: "1-10"
  cost_to_replicate: $X
```

### 6. Cornered Resource
```yaml
cornered_resource:
  resource: "Patents | Data | Talent | Licenses"
  exclusivity: "Legal | Contractual | Geographic"
  barrier: "Competitor cost to acquire"
```

### 7. Process Power
```yaml
process_power:
  proprietary_process: "Description"
  embedded_knowledge: "Tacit | Organizational"
  time_to_replicate: X years
```

================================================================================
JOBS-TO-BE-DONE FRAMEWORK
================================================================================

**Purpose**: Deep customer motivation modeling

Create: `/business/models/strategy/jtbd_analysis.yaml`

```yaml
job_statement: "  [Verb] + [Object] + [Context]"
job_type: "Functional | Emotional | Social"

job_steps:
  - stage: "Define | Locate | Prepare | Confirm | Execute | Monitor | Modify | Conclude"
    activities: ["activity 1", "activity 2"]

desired_outcomes:
  - outcome: "[Direction] + [Metric] + [Object]"
    importance: 1-5
    satisfaction: 1-5
    opportunity_score: "(importance + (importance - satisfaction))"
    
innovation_targets:
  underserved: "High importance + Low satisfaction"
  overserved: "Low importance + High satisfaction (simplify)"
```

================================================================================
PLAYING TO WIN (Lafley & Martin)
================================================================================

**Purpose**: Integrated strategic choice cascade

Create: `/business/models/strategy/playing_to_win.yaml`

```yaml
winning_aspiration: "What does winning mean?"
where_to_play:
  markets: ["Market 1", "Market 2"]
  segments: ["Segment A", "Segment B"]
  channels: ["Channel X"]
how_to_win:
  value_proposition: "Unique offering"
  competitive_advantage: "Source of advantage"
core_capabilities:
  - capability: "Required capability"
    gap: "Current state vs needed"
    build_buy_partner: "Build | Buy | Partner"
management_systems:
  kpis: ["Metric 1", "Metric 2"]
  incentives: "Alignment approach"
```

================================================================================
BLUE OCEAN STRATEGY
================================================================================

**Purpose**: Create uncontested market space

Create: `/business/models/strategy/blue_ocean_canvas.yaml`

```yaml
four_actions:
  eliminate: ["Factor to remove"]
  reduce: ["Factor to reduce below standard"]
  raise: ["Factor to raise above standard"]
  create: ["New factor never offered"]
  
non_customers:
  tier_1_soon_to_be: "At market edge"
  tier_2_refusing: "Consciously reject"
  tier_3_unexplored: "Distant markets"
```

================================================================================
AGGREGATION THEORY (Ben Thompson)
================================================================================

**Purpose**: Platform winner-take-most dynamics

Create: `/business/models/strategy/aggregation_model.yaml`

```yaml
aggregator_characteristics:
  direct_relationship_with_users: Yes/No
  zero_marginal_cost: Yes/No
  demand_driven_network: Yes/No

supply_commoditization:
  mechanism: "More users → suppliers compete"
  multi_homing: "Low = Winner-take-all"
  
data_advantage:
  accumulation: "User behavior data"
  feedback_loop: "More data → better algorithm → more users"
```

================================================================================
THEORY OF CONSTRAINTS (Goldratt)
================================================================================

**Purpose**: Identify and manage bottlenecks

Create: `/business/models/operations/theory_of_constraints.yaml`

```yaml
five_focusing_steps:
  1_identify: "Find bottleneck (lowest capacity)"
  2_exploit: "Maximize bottleneck output"
  3_subordinate: "Align everything to bottleneck"
  4_elevate: "Invest to expand bottleneck"
  5_repeat: "Find new constraint"

throughput_accounting:
  throughput: "Rate of generating money through sales"
  inventory: "Money in items to sell"
  operating_expense: "Money to convert inventory"
```

### FILE: financial-engineering.md

# Advanced Financial Engineering

Advanced financial modeling and analysis frameworks for capital structure, valuation, and strategic financial decisions.

**When to use**:
- Capital raising decisions
- M&A analysis
- Complex financing structures
- Tax optimization
- Strategic option valuation

================================================================================
ADVANCED CAPITAL STRUCTURE OPTIMIZATION
================================================================================

Create: `/business/models/financial/capital_structure_optimization.yaml`

```yaml
wacc_optimization:
  debt_capacity: $X
  cost_of_debt: Y%
  cost_of_equity: Z%
  optimal_debt_equity_ratio: "W:1"
  tax_shields: $T
  
credit_analysis:
  interest_coverage: "EBIT / Interest"
  debt_service_coverage: "OCF / Debt Service"
  leverage_ratios: "Debt / EBITDA"
  covenant_headroom: "X%"
```

================================================================================
REAL OPTIONS ANALYSIS
================================================================================

**Purpose**: Value strategic flexibility

Create: `/business/models/financial/real_options_model.yaml`

```yaml
option_type: "Expand | Delay | Abandon | Switch"
inputs:
  underlying_asset_value: $S
  exercise_price: $K
  time_to_expiration: T years
  volatility: σ
  risk_free_rate: r
  
valuation_method: "Black-Scholes | Binomial Tree | Monte Carlo"
option_value: $X
strategic_decision: "Exercise if value > threshold"

applications:
  delay_investment: "Wait for more information"
  expand_if_successful: "Scale up option"
  abandon_if_unsuccessful: "Exit option"
  platform_growth_options: "Initial investment unlocks future opportunities"
```

================================================================================
M&A FINANCIAL MODELING
================================================================================

Create: `/business/models/financial/ma_model.yaml`

```yaml
target_valuation:
  dcf_value: $X
  comparable_companies: $Y
  precedent_transactions: $Z
  valuation_range: "$A - $B"
  
synergies:
  revenue_synergies: $R (cross-sell, pricing power)
  cost_synergies: $C (eliminate redundancies
  capex_synergies: $K
  total_synergies: $R + $C + $K
  probability_adjusted: $S * P
  
integration:
  one_time_costs: $I
  time_to_realize: X years
  
economics:
  purchase_price: $P
  net_synergies: $S - $I
  accretion_dilution: "EPS impact"
  irr: "X%"
  payback: Y years
```

================================================================================
VENTURE CAPITAL TERM SHEET ANALYSIS
================================================================================

Create: `/business/models/financial/vc_terms_analysis.yaml`

```yaml
investment_terms:
  pre_money_valuation: $X
  investment_amount: $Y
  post_money_valuation: $X + $Y
  ownership_percentage: "$Y / ($X + $Y)"
  
preference_stack:
  liquidation_preference: "1x | 2x | 3x"
  participation: "Non-participating | Fully participating | Capped"
  seniority: "Pari passu | Senior"
  
anti_dilution:
  type: "Full ratchet | Weighted average (broad | narrow)"
  protection_threshold: "Down round > X%"
  
exit_scenarios:
  - exit_value: $100M
    preference_payout: $X
    common_payout: $Y
    investor_return: "X MOIC"
  - exit_value: $500M
    preference_payout: $X
    common_payout: $Y
    investor_return: "X MOIC"
```

================================================================================
TAX & ENTITY OPTIMIZATION
================================================================================

Create: `/business/models/financial/tax_optimization.yaml`

```yaml
entity_structure_options:
  - structure: "C-Corp | S-Corp | LLC | Partnership"
    tax_treatment: "Description"
    effective_rate: X%
    pros: ["Pro 1", "Pro 2"]
    cons: ["Con 1", "Con 2"]
    
multi_entity_structures:
  holding_company: "IP ownership, risk isolation"
  operating_companies: "By geography or product line"
  transfer_pricing: "Allocate profits optimally"
  
tax_optimization_opportunities:
  r_and_d_credits: $X
  qsbs_eligibility: "0% cap gains if qualified"
  nol_carryforwards: $Y
  accelerated_depreciation: "Bonus depreciation"
  
note: "This is structural analysis only. Consult tax professionals."
```

================================================================================
INSURANCE & RISK TRANSFER OPTIMIZATION
================================================================================

Create: `/business/models/financial/insurance_optimization.yaml`

```yaml
risk_transfer_analysis:
  - risk: "Risk description"
    expected_loss: $X * P
    retain_vs_transfer: "Cost comparison"
    decision: "Retain | Insure | Partially insure"
    
insurance_portfolio:
  - policy: "General Liability"
    coverage: $X
    deductible: $Y
    premium: $Z/year
    roi_analysis: "Premium vs expected claim"
    
self_insurance_fund:
  required_reserves: $R
  investment_return: Y%
  break_even_analysis: "Years to break even vs purchasing"
  
captive_insurance:
  feasibility: "If premiums > $Xk/year"
  structure: "Domicile, ownership"
  benefits: "Tax advantages, investment income"
```

### FILE: decision-science.md

# Advanced Decision Science Frameworks

Frameworks for decisions under uncertainty, competing objectives, and strategic interaction.

**When to use**:
- High-stakes decisions with uncertainty
- Complex decisions with multiple stakeholders
- Competitive strategy
- Learning from experiments

================================================================================
BAYESIAN DECISION ANALYSIS
================================================================================

**Purpose**: Decision-making under uncertainty with learning

Create: `/business/models/decisions/bayesian_analysis.yaml`

```yaml
prior_beliefs:
  - state: "Market is strong"
    probability: 0.6
  - state: "Market is weak"
    probability: 0.4
    
decision_alternatives:
  - "Launch now"
  - "Delay and test"
  - "Don't launch"
  
payoff_matrix:
  - decision: "Launch now"
    strong_market: $10M
    weak_market: -$2M
    expected_value: "$10M * 0.6 + (-$2M) * 0.4"
    
information_gathering:
  test_cost: $X
  likelihood_of_evidence: "P(evidence | state)"
  posterior_probabilities: "Bayes' theorem update"
  
value_of_information:
  evpi: "Expected Value of Perfect Information"
  evsi: "Expected Value of Sample Information"
  decision: "Gather info if EVSI > cost"
```

================================================================================
MULTI-CRITERIA DECISION ANALYSIS (MCDA)
================================================================================

**Purpose**: Decisions with competing objectives

Create: `/business/models/decisions/mcda_analysis.yaml`

```yaml
alternatives:
  - "Option A"
  - "Option B"
  - "Option C"
  
criteria:
  - criterion: "Cost"
    weight: 0.30
    preference: "Minimize"
  - criterion: "Speed"
    weight: 0.25
    preference: "Maximize"
  - criterion: "Quality"
    weight: 0.45
    preference: "Maximize"
    
scoring:
  option_a:
    cost: 7/10
    speed: 3/10
    quality: 9/10
    weighted_score: "0.30*7 + 0.25*3 + 0.45*9"
    
sensitivity_analysis:
  vary_weights: "How robust is decision to weight changes?"
  
methods:
  wsm: "Weighted Sum Model (simple)"
  ahp: "Analytic Hierarchy Process (pairwise comparisons)"
  topsis: "Technique for Order Preference"
```

================================================================================
GAME THEORY & STRATEGIC INTERACTION
================================================================================

**Purpose**: Model competitive dynamics

Create: `/business/models/decisions/game_theory_model.yaml`

```yaml
players:
  - "Your company"
  - "Competitor A"
  
strategies:
  your_strategies: ["Aggressive pricing", "Premium positioning"]
  competitor_strategies: ["Match price", "Maintain premium"]
  
payoff_matrix:
  - your_move: "Aggressive pricing"
    competitor_move: "Match price"
    your_payoff: $X
    competitor_payoff: $Y
    
equilibrium_analysis:
  nash_equilibrium: "Strategy pair where no one wants to deviate"
  dominant_strategy: "Best move regardless of opponent"
  
strategic_commitment:
  first_mover_advantage: "Commit to capacity before competitor"
  credibility: "Make commitment irreversible"
  
game_types:
  prisoners_dilemma: "Cooperation vs defection"
  entry_deterrence: "Incumbent threatens retaliation"
  platform_competition: "Winner-take-most dynamics"
```

================================================================================
CAUSAL INFERENCE & EXPERIMENT DESIGN
================================================================================

**Purpose**: Understand true causation

Create: `/business/models/analysis/causal_inference_framework.yaml`

```yaml
hypothesis: "X causes Y"
confounding_variables: ["Z1", "Z2"]

identification_strategy:
  method: "RCT | Natural experiment | IV | RDD | DID"
  
randomized_controlled_trial:
  treatment_group: "Receives intervention"
  control_group: "Does not receive"
  random_assignment: "Eliminates selection bias"
  sample_size: "N per group for power"
  minimum_detectable_effect: "X%"
  
instrumental_variables:
  instrument: "Variable that affects X but not Y directly"
  validity: "Relevance and exclusion restrictions"
  
analysis_plan:
  preregistered: Yes/No
  primary_outcome: "Metric Y"
  statistical_test: "t-test | regression"
  significance_level: α = 0.05
```

================================================================================
COHORT ANALYSIS & RETENTION MODELING
================================================================================

Create: `/business/models/analysis/cohort_retention_model.yaml`

```yaml
cohort_definition: "Acquisition month | Channel | Plan type"

retention_curve:
  - period: "Month 1"
    retention_rate: 90%
  - period: "Month 3"
    retention_rate: 75%
  - period: "Month 12"
    retention_rate: 60%
    
survival_analysis:
  model: "Kaplan-Meier | Weibull | Cox proportional hazards"
  hazard_rate: "Instantaneous churn probability"
  
clv_probabilistic:
  p_alive: "Probability customer hasn't churned"
  expected_transactions: "BG/NBD model"
  expected_revenue_per_transaction: "Gamma-Gamma model"
  clv: "NPV of expected future cash flows"
  
leading_indicators:
  - indicator: "Usage decline > 50%"
    churn_correlation: 0.7
    intervention: "Outreach campaign"
```

================================================================================
CONJOINT ANALYSIS & PRICING OPTIMIZATION
================================================================================

Create: `/business/models/analysis/conjoint_pricing_model.yaml`

```yaml
attributes:
  - attribute: "Price"
    levels: ["$50", "$100", "$150"]
  - attribute: "Feature A"
    levels: ["Basic", "Advanced"]
  - attribute: "Support"
    levels: ["Email", "24/7 Phone"]
    
experimental_design: "Choice-based conjoint"
respondents: N = 500

utility_estimates:
  price_50: +15
  price_100: 0 (reference)
  price_150: -20
  feature_advanced: +12
  support_24_7: +8
  
preference_shares:
  config_1: "Price=$100, Advanced, 24/7"
  share: "30%"
  
optimal_configuration:
  maximize: "Revenue | Share | Margin"
  constraints: "Cost to deliver"
  
price_elasticity:
  demand_curve: "Q = f(P)"
  optimal_price: $X (where MR = MC)
```

================================================================================
NET REVENUE RETENTION (NRR) MODELING
================================================================================

Create: `/business/models/financial/nrr_expansion_model.yaml`

```yaml
cohort_arr_dynamics:
  starting_arr: $100k
  churned_arr: -$10k
  downgrade_arr: -$5k
  upgrade_arr: +$15k
  cross_sell_arr: +$10k
  ending_arr: $110k
  
nrr: "(Ending - New) / Starting = 110%"
grr: "(Starting - Churn - Downgrade) / Starting = 85%"

expansion_drivers:
  usage_growth: "More users, more seats"
  feature_adoption: "Upgrade to premium tiers"
  cross_sell: "Additional products"
  
path_to_110_plus_nrr:
  - action: "Reduce churn to <5%"
  - action: "Increase expansion rate to 25%+"
  - action: "Land-and-expand motion"
```

### FILE: optimization-simulation.md

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

### FILE: process-optimization.md

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

### FILE: data-ml-frameworks.md

# Data, ML & Automation Frameworks

Frameworks for predictive analytics, machine learning, and process automation.

**When to use**:
- Predictive modeling needs
- Process automation opportunities
- Data-driven decision making
- Competitive intelligence

================================================================================
PREDICTIVE ANALYTICS APPLICATIONS
================================================================================

### Revenue Forecasting

Create: `/business/models/analytics/revenue_forecasting_model.yaml`

```yaml
problem: "Predict monthly revenue"
data_sources:
  - historical_revenue
  - sales_pipeline
  - marketing_spend
  - seasonality_indicators
  - macroeconomic_indicators
  
model_options:
  time_series: "ARIMA, Prophet, LSTM"
  regression: "Include exogenous variables"
  ensemble: "Combine multiple models"
  
features:
  - "Lagged revenue (1, 3, 12 months)"
  - "Pipeline coverage ratio"
  - "Marketing spend (lagged)"
  - "Month/quarter dummies"
  
validation:
  method: "Time series cross-validation"
  metrics: "RMSE, MAPE, bias"
  
output:
  point_forecast: $X
  prediction_interval: "80% and 95%"
  feature_importance: "What drives forecast"
```

### Customer Churn Prediction

Create: `/business/models/analytics/churn_prediction_model.yaml`

```yaml
problem: "Which customers will churn in next 90 days"
target: "Churned (binary)"

features:
  usage: "Declining engagement trend"
  support: "Number of tickets, sentiment"
  billing: "Payment failures, downgrades"
  lifecycle: "Days since signup, contract end"
  firmographic: "Company size, industry"
  
model: "Gradient Boosting (XGBoost, LightGBM)"

validation:
  metric: "AUC-ROC, precision-recall"
  business_metric: "Cost of false positive vs false negative"
  
output:
  churn_probability: 0.0-1.0 per customer
  risk_segments: "High (>0.7), Medium (0.3-0.7), Low (<0.3)"
  
action:
  high_risk: "SDR outreach, offer incentive"
  medium_risk: "Automated email nurture"
  
monitoring:
  model_drift: "Monthly AUC check"
  retrain_trigger: "AUC drop > 5%"
```

### Dynamic Pricing

Create: `/business/models/analytics/dynamic_pricing_model.yaml`

```yaml
problem: "Optimal price given demand elasticity"
approach: "Price optimization with demand curve"

demand_estimation:
  historical_data: "Price, volume, competitor prices, seasonality"
  model: "log(Q) = β0 + β1*log(P) + β2*X + ε"
  elasticity: "β1 (% change Q / % change P)"
  
optimization:
  objective: "Maximize revenue | profit | market share"
  constraints:
    - "Minimum margin"
    - "Competitive parity ± X%"
    - "Brand positioning"
  solution: "P* where MR = MC"
  
personalization:
  segment_pricing: "By customer segment, time, inventory"
  
ab_testing:
  test_prices: "Test ± 10% from baseline"
  measure: "Conversion, revenue, profit"
  rollout: "If statistically significant lift"
```

================================================================================
ML MODEL GOVERNANCE
================================================================================

Create: `/business/models/analytics/ml_governance.yaml`

```yaml
model_inventory:
  - model: "Churn prediction"
    owner: "Data Science"
    business_impact: "High"
    production_status: "Live"
    last_updated: "2025-01"
    
model_documentation:
  methodology: "Gradient boosting classifier"
  training_data: "Last 24 months customer data"
  features: "N=45 features"
  performance: "AUC = 0.82"
  limitations: "Doesn't account for competitor actions"
  
monitoring:
  data_drift: "Distribution shift in features"
  concept_drift: "Relationship between X and Y changes"
  performance_degradation: "AUC declining"
  alerts: "If AUC < 0.75, retrain"
  
retraining_schedule: "Quarterly or when triggered"

bias_and_fairness:
  protected_attributes: ["Demographics if applicable"]
  fairness_metrics: "Disparate impact ratio"
  audit_frequency: "Annual"
  
explainability:
  method: "SHAP values for feature importance"
  use_case: "Explain predictions to business users"
```

================================================================================
DATA PIPELINE & INTEGRATION
================================================================================

Create: `/business/models/data/integration_framework.yaml`

```yaml
data_sources:
  internal:
    - system: "CRM (Salesforce)"
      data: "Leads, opportunities, customers"
      refresh: "Real-time via webhook"
    - system: "Production DB"
      data: "Usage, transactions"
      refresh: "Hourly batch"
  external:
    - provider: "Market data API"
      data: "Industry benchmarks"
      refresh: "Daily"
      
etl_pipeline:
  extract: "Pull from sources"
  transform:
    - "Cleanse (nulls, duplicates)"
    - "Standardize (formats, units)"
    - "Join (merge datasets)"
    - "Aggregate (rollups)"
  load: "Write to data warehouse"
  orchestration: "Airflow DAG"
  schedule: "Run at 2 AM daily"
  
data_quality:
  checks:
    - "Completeness (no critical nulls)"
    - "Consistency (cross-table reconciliation)"
    - "Timeliness (data is current)"
  failure_handling: "Alert data team, halt pipeline"
  
data_lineage: "Track data provenance for audit"
```

================================================================================
AUTOMATED COMPETITIVE INTELLIGENCE
================================================================================

Create: `/business/models/market/competitive_intel_automation.yaml`

```yaml
competitors: ["Competitor A", "Competitor B", "Competitor C"]

monitoring:
  sources:
    website_changes: "Track product pages, pricing"
    job_postings: "Hiring signals (expansion, new products)"
    news_mentions: "Press releases, media coverage"
    social_media: "Sentiment, campaigns"
    sec_filings: "If public: revenue, strategy insights"
    patent_filings: "Technology investments"
    
tools:
  web_scraping: "BeautifulSoup, Scrapy"
  change_detection: "Track diffs on key pages"
  nlp: "Sentiment analysis on news"
  
alerts:
  - trigger: "Pricing change > 10%"
    action: "Notify pricing team"
  - trigger: "Major product launch announcement"
    action: "Notify product team"
    
reporting:
  weekly_digest: "Summary of competitive moves"
  monthly_deep_dive: "Strategy analysis"
  ad_hoc: "Real-time alerts for major events"
```

================================================================================
DASHBOARDS & AUTOMATED REPORTING
================================================================================

Create: `/business/models/data/dashboard_specification.yaml`

```yaml
dashboard_name: "Executive Dashboard"
audience: "C-suite"
refresh: "Daily at 6 AM"

metrics:
  - metric: "Revenue (MTD)"
    visualization: "Big number with % vs target"
  - metric: "Pipeline coverage"
    visualization: "Gauge (1x = red, 3x+ = green)"
  - metric: "Customer churn rate"
    visualization: "Line chart (12 months)"
  - metric: "Cash runway"
    visualization: "Big number (months remaining)"
    
drill_downs:
  revenue: "By product line, region, sales rep"
  churn: "By cohort, plan type"
  
alerts:
  - condition: "Revenue < 90% of target"
    notification: "Email CFO, CEO"
  - condition: "Cash runway < 6 months"
    notification: "Escalate to board"
    
access_control: "C-suite and board only"
```

### FILE: collaboration-frameworks.md

# Collaboration & Stakeholder Management Frameworks

Frameworks for structured collaboration, stakeholder management, and change management.

**When to use**:
- Complex decisions requiring diverse input
- Stakeholder alignment needed
- Organizational change initiatives
- Pre-mortem risk analysis

================================================================================
STRUCTURED EXPERT ELICITATION
================================================================================

Create: `/business/models/collaboration/expert_elicitation_framework.yaml`

```yaml
question: "What will market growth rate be in 2027?"
experts:
  - name: "Expert 1"
    expertise: "Market analyst"
    calibration_score: 0.8
  - name: "Expert 2"
    expertise: "Industry veteran"
    calibration_score: 0.9
    
elicitation_method: "Delphi (anonymous, iterative)"

round_1:
  expert_1_estimate: "15% ± 5%"
  expert_2_estimate: "10% ± 3%"
  share_results: "Show anonymized distribution"
  
round_2:
  expert_1_revised: "12% ± 4%"
  expert_2_revised: "11% ± 3%"
  convergence: "Yes, estimates closer"
  
aggregation:
  method: "Weighted by calibration score "
  final_estimate: "11.5% ± 3.5%"
  
bias_mitigation:
  anchoring: "Elicit before showing data"
  groupthink: "Anonymous submissions"
  overconfidence: "Calibration training"
```

================================================================================
SCENARIO PLANNING WORKSHOPS
================================================================================

Create: `/business/models/strategy/scenario_planning_framework.yaml`

```yaml
focal_question: "How should we position for 2030?"

key_forces:
  - "Technology adoption rate"
  - "Competitive intensity"
  - "Regulatory environment"
  - "Economic growth"
  
critical_uncertainties:
  axis_1: "Technology disruption (Low vs High)"
  axis_2: "Market growth (Slow vs Fast)"
  
four_scenarios:
  scenario_a:
    name: "Steady Progress"
    description: "Low disruption, slow growth"
    implications: "Focus on efficiency, defend share"
  scenario_b:
    name: "Innovation Boom"
    description: "High disruption, fast growth"
    implications: "Invest aggressively in R&D"
  scenario_c:
    name: "Consolidation"
    description: "Low disruption, slow growth"
    implications: "M&A opportunities, cost control"
  scenario_d:
    name: "Creative Destruction"
    description: "High disruption, slow growth"
    implications: "Nimble, pivot capability"
    
robust_strategies:
  - "Works across all scenarios"
  - "Flexible, option-rich"
  
signposts:
  - indicator: "Patent filings in category"
    scenario_implication: "High = disruption likely"
  - indicator: "GDP forecasts"
    scenario_implication: "Signals growth trajectory"
```

================================================================================
RED TEAM / BLUE TEAM EXERCISE
================================================================================

Create: `/business/models/governance/red_team_framework.yaml`

```yaml
scope: "Challenge market entry strategy for Product X"

blue_team:
  role: "Strategy proponents"
  members: ["Product VP", "Strategy lead"]
  
red_team:
  role: "Devil's advocates"
  members: ["External advisor", "Skeptical exec"]
  
process:
  round_1:
    blue_presents: "Market opportunity, strategy, financials"
  round_2:
    red_challenges:
      - "Market size assumptions too optimistic"
      - "Competitor response underestimated"
      - "Execution risk not addressed"
  round_3:
    blue_responds: "Revised assumptions, mitigation plans"
  synthesis:
    facilitator: "Identifies valid concerns and refinements"
    
outputs:
  identified_risks:
    - "Regulatory approval timeline"
    - "Key person dependency"
  refined_strategy:
    - "Phase launch to reduce risk"
    - "Pilot in smaller market first"
  confidence_adjustment: "High → Medium-High"
```

================================================================================
PRE-MORTEM ANALYSIS
================================================================================

Create: `/business/models/risk/pre_mortem_framework.yaml`

```yaml
assumption: "It's 2 years from now. The project has failed."

brainstorm_failures:
  - "Ran out of cash"
  - "Key team member left"
  - "Competitor launched first"
  - "Product-market fit was wrong"
  - "Regulatory roadblock"
  
categorize:
  execution: ["Cash", "Team"]
  market: ["PMF", "Competitor"]
  external: ["Regulatory"]
  
assess_likelihood:
  - failure: "Ran out of cash"
    likelihood: "Medium"
    preventable: "Yes"
    
design_mitigations:
  - failure: "Ran out of cash"
    mitigation: "Extend runway to 24 months, set tripwires"
  - failure: "Key person left"
    mitigation: "Cross-training, retention incentives"
    
early_warning_indicators:
  - metric: "Burn rate trend"
    red_flag: "Increasing faster than revenue"
  - metric: "Employee satisfaction"
    red_flag: "Score < 7/10"
    
circuit_breakers:
  - condition: "If 50% of pilot customers don't convert"
    action: "Pivot or shutdown"
```

================================================================================
STAKEHOLDER MAPPING  & MANAGEMENT
================================================================================

Create: `/business/models/governance/stakeholder_management.yaml`

```yaml
stakeholders:
  - name: "Investors"
    power: High
    interest: High
    attitude: "Supportive"
    quadrant: "Key Players (manage closely)"
    
  - name: "Employees"
    power: Medium
    interest: High
    attitude: "Neutral-Positive"
    quadrant: "Keep Informed"
    
  - name: "Regulator"
    power: High
    interest: Low
    attitude: "Neutral"
    quadrant: "Keep Satisfied"
    
engagement_strategy:
  investors:
    frequency: "Monthly Board meetings, quarterly updates"
    channel: "In-person, detailed reports"
    message: "Growth, risks, capital needs"
    
  employees:
    frequency: "Weekly all-hands, quarterly deep-dives"
    channel: "Slack, town halls"
    message: "Vision, progress, recognition"
    
conflict_resolution:
  competing_interests: "Employees want raises, investors want profitability"
  negotiation: "Performance-based comp, aligned with growth"
```

================================================================================
CHANGE MANAGEMENT (ADKAR)
================================================================================

Create: `/business/models/people/change_management_framework.yaml`

```yaml
change: "Migrate to new CRM system"

impacted_groups:
  - group: "Sales team"
    size: 50 people
    impact_level: "High"
    
adkar_assessment:
  awareness:
    current: "60% understand why changing"
    target: "100%"
    actions: ["Town hall explaining rationale", "FAQ document"]
    
  desire:
    current: "40% want to change"
    target: "80%+"
    actions: ["Incentives for early adoption", "Address concerns"]
    
  knowledge:
    current: "10% know how to use new system"
    target: "100%"
    actions: ["Training program", "Quick reference guides"]
    
  ability:
    current: "5% can effectively use"
    target: "90%"
    actions: ["Hands-on practice", "Support hours"]
    
  reinforcement:
    actions: ["Recognize early adopters", "Disable old system"]
    
success_metrics:
  adoption_rate: "% using new system daily"
  proficiency: "Time to complete key tasks"
  satisfaction: "User NPS"
  
resistance_mitigation:
  concern: "New system is more complex"
  response: "Streamline workflows, provide support"
```

### FILE: esg-impact.md

# ESG & Impact Measurement Frameworks

Frameworks for environmental, social, and governance measurement and sustainability.

**When to use**:
- ESG commitments and reporting
- Impact-driven businesses
- Sustainability strategy
- Stakeholder capitalism models

================================================================================
ESG MATERIALITY ASSESSMENT
================================================================================

Create: `/business/models/esg/materiality_assessment.yaml`

```yaml
industry: "Software SaaS"

environmental_factors:
  - factor: "Energy consumption"
    financial_impact: "Low (cloud-based)"
    stakeholder_importance: "Medium"
    material: No
  - factor: "E-waste from hardware"
    financial_impact: "Low"
    stakeholder_importance: "Low"
    material: No
    
social_factors:
  - factor: "Employee diversity"
    financial_impact: "Medium (talent attraction)"
    stakeholder_importance: "High"
    material: Yes
  - factor: "Data privacy"
    financial_impact: "High (regulatory, reputation)"
    stakeholder_importance: "High"
    material: Yes
    
governance_factors:
  - factor: "Board independence"
    financial_impact: "Medium"
    stakeholder_importance: "High (investors)"
    material: Yes
    
material_factors:
  - "Employee diversity"
  - "Data privacy"
  - "Board independence"
  - "Business ethics"
  
action_plan:
  - factor: "Employee diversity"
    current_state: "Baseline demographic data"
    target: "30% women in leadership by 2027"
    initiatives: ["Inclusive hiring", "Mentorship programs"]
```

================================================================================
CARBON ACCOUNTING & CLIMATE STRATEGY
================================================================================

Create: `/business/models/esg/carbon_accounting_model.yaml`

```yaml
reporting_year: 2025
boundary: "Operational control approach"

scope_1_emissions:
  - source: "Company vehicles"
    activity: "10,000 gallons gasoline"
    emission_factor: "8.89 kg CO2e/gallon"
    total: "89 tCO2e"
  total_scope_1: "89 tCO2e"
  
scope_2_emissions:
  - source: "Purchased electricity"
    activity: "500 MWh"
    emission_factor: "0.5 tCO2e/MWh (grid average)"
    total: "250 tCO2e"
  total_scope_2: "250 tCO2e (location-based)"
  
scope_3_emissions:
  category_1_purchased_goods: "500 tCO2e"
  category_6_business_travel: "200 tCO2e"
  category_7_employee_commute: "150 tCO2e"
  total_scope_3: "850 tCO2e"
  
total_emissions: "1,189 tCO2e"
intensity: "1,189 tCO2e / $10M revenue = 119 tCO2e/$M"

climate_strategy:
  target: "50% reduction by 2030 (vs 2025 baseline)"
  pathway:
    - "Switch to renewable energy (eliminate Scope 2)"
    - "Electrify vehicle fleet"
    - "Engage suppliers on emissions"
    - "Remote work policy (reduce commute)"
  residual_emissions: "Offset via verified carbon credits"
  
internal_carbon_price: "$50/tCO2e (decision-making tool)"
```

================================================================================
IMPACT MEASUREMENT & MANAGEMENT
================================================================================

Create: `/business/models/impact/impact_measurement_framework.yaml`

```yaml
mission: "Improve financial literacy for underserved populations"

theory_of_change:
  inputs: "Capital, team, technology"
  activities: "Develop app, content, deliver training"
  outputs: "N users, M training hours"
  outcomes: "Improved financial knowledge, behavior change"
  impact: "Reduced poverty, increased economic mobility"
  
impact_metrics:
  - metric: "Users reached"
    target: "100,000 by 2026"
    actual: "75,000"
    iris_indicator: "PI4556"
    
  - metric: "Financial literacy score improvement"
    baseline: "45/100"
    endline: "68/100"
    change: "+23 points"
    
  - metric: "Savings rate"
    baseline: "2% of users save regularly"
    endline: "35% of users save regularly"
    
attribution:
  approach: "Quasi-experimental (matched control group)"
  counterfactual: "What would have happened without intervention?"
  
impact_valuation:
  outcome: "Increased savings"
  monetization: "NPV of savings * social discount rate"
  total_impact_value: "$X million"
  
sroi:
  investment: "$1 million"
  social_value_created: "$4 million"
  sroi_ratio: "4:1"
  
stakeholder_feedback:
  beneficiaries: "Survey satisfaction, collect stories"
  frequency: "Quarterly"
```

================================================================================
SUSTAINABILITY REPORTING FRAMEWORKS
================================================================================

Create: `/business/models/esg/sustainability_reporting_framework.yaml`

```yaml
frameworks_adopted:
  - "GRI (Global Reporting Initiative)"
  - "SASB (Sustainability Accounting Standards Board)"
  - "TCFD (Task Force on Climate-related Financial Disclosures)"
  
gri_reporting:
  universal_standards: "GRI 2: General Disclosures"
  topic_standards:
    - "GRI 302: Energy"
    - "GRI 401: Employment"
    - "GRI 405: Diversity and Equal Opportunity"
    
sasb_reporting:
  industry: "Software & IT Services"
  material_topics:
    - "Data Privacy & Advertising Standards"
    - "Data Security"
    - "Recruiting & Managing a Global Workforce"
    
tcfd_reporting:
  governance: "Board oversight of climate risks"
  strategy:
    risks: "Regulatory risk (carbon pricing)"
    opportunities: "Energy efficiency savings"
  risk_management: "Integrated into ERM process"
  metrics_targets:
    - "Scope 1+2 emissions"
    - "Reduction target: 50% by 2030"
    
publication:
  format: "Annual Sustainability Report (standalone)"
  assurance: "Third-party limited assurance"
  distribution: "Website, investor communications"
```

================================================================================
STAKEHOLDER GOVERNANCE (B CORP / PBC)
================================================================================

Create: `/business/models/governance/stakeholder_governance_model.yaml`

```yaml
legal_structure: "Public Benefit Corporation"

purpose: "Create positive impact for customers, employees, community, environment"

stakeholder_constituencies:
  customers:
    representation: "Customer advisory board"
    rights: "Product roadmap input"
  employees:
    representation: "Employee council"
    rights: "Voice in policy decisions"
  community:
    representation: "Community partnerships"
    commitments: "X% revenue to local initiatives"
    
benefit_lock:
  mechanism: "PBC charter requires directors to consider stakeholders"
  accountability: "Annual benefit report"
  
b_corp_certification:
  status: "In progress"
  b_impact_assessment_score: "85 (target: 80+)"
  areas:
    governance: "18/50"
    workers: "25/50"
    community: "20/50"
    environment: "12/50"
    customers: "10/50"
    
transparency:
  annual_benefit_report:
    contents:
      - "Assessment methodology"
      - "Goals and progress"
      - "Stakeholder impacts"
    publication: "Website, filed with state"
```

---

**END OF FRAMEWORKS MASTER CONTENT**