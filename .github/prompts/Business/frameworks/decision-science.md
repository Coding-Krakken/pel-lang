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