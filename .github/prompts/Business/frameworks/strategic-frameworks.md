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

