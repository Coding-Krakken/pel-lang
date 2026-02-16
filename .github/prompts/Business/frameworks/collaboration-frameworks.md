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