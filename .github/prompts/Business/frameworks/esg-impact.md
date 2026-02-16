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