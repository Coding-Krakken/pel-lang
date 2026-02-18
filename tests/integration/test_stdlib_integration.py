"""Integration tests demonstrating stdlib modules working together."""
# ruff: noqa: W293
import tempfile
from pathlib import Path

import pytest

from compiler.compiler import PELCompiler


def _compile_pel_model(code: str) -> dict:
    """Compile a full PEL model (not wrapped)."""
    fd, tmp = tempfile.mkstemp(suffix=".pel")
    Path(tmp).write_text(code, encoding="utf-8")
    compiler = PELCompiler(verbose=False)
    ir = compiler.compile(Path(tmp))
    return ir


@pytest.mark.integration
def test_saas_business_model_integration():
    """
    Integration test: Complete SaaS business model using funnel, retention, and cashflow modules.
    
    This model demonstrates:
    - Funnel: Visitor → Signup → Trial → Paid customer conversion
    - Retention: Customer lifetime and churn dynamics
    - Cashflow: Burn rate, runway, and cash management
    """
    model = """
// Complete SaaS Business Model
// Demonstrates integration of funnel, retention, and cashflow stdlib modules

model SaaS_Business_Complete {
    // ========================================================================
    // Funnel: Customer Acquisition
    // ========================================================================
    
    param monthly_visitors: Count<User> = 50_000 {
        source: "google_analytics",
        method: "observed",
        confidence: 0.95
    }
    
    param signup_rate: Fraction = 0.05 {
        source: "analytics",
        method: "derived",
        confidence: 0.90,
        notes: "5% of visitors sign up"
    }
    
    param activation_rate: Fraction = 0.70 {
        source: "product_analytics",
        method: "derived",
        confidence: 0.85
    }
    
    param trial_start_rate: Fraction = 0.80 {
        source: "product_analytics",
        method: "derived",
        confidence: 0.85
    }
    
    param trial_to_paid_rate: Fraction = 0.30 {
        source: "conversion_tracking",
        method: "derived",
        confidence: 0.80
    }
    
    // Calculate acquisition funnel
    var acquisition_funnel: Array<Count<User>> = saas_signup_funnel(
        monthly_visitors,
        signup_rate,
        activation_rate,
        trial_start_rate,
        trial_to_paid_rate
    )
    
    var new_customers_per_month: Count<User> = acquisition_funnel[4]
    
    // ========================================================================
    // Retention: Customer Dynamics
    // ========================================================================
    
    param monthly_churn_rate: Rate per Month = 0.06/1mo {
        source: "cohort_analysis",
        method: "fitted",
        confidence: 0.85,
        notes: "6% monthly churn"
    }
    
    param current_customer_base: Count<Customer> = 1_000 {
        source: "database",
        method: "observed",
        confidence: 1.0
    }
    
    // Calculate retention metrics
    var monthly_retention_rate: Fraction = retention_rate_from_churn(monthly_churn_rate)
    var avg_customer_lifetime: Duration<Month> = customer_lifetime_months(monthly_retention_rate)
    
    // Dollar-based retention
    param current_mrr: Currency<USD> = $100_000 {
        source: "billing_system",
        method: "observed",
        confidence: 1.0
    }
    
    param expansion_mrr: Currency<USD> = $8_000 {
        source: "billing_system",
        method: "observed",
        confidence: 1.0
    }
    
    param churned_mrr: Currency<USD> = $6_000 {
        source: "billing_system",
        method: "observed",
        confidence: 1.0
    }
    
    param contraction_mrr: Currency<USD> = $1_000 {
        source: "billing_system",
        method: "observed",
        confidence: 1.0
    }
    
    var ndr: Fraction = net_dollar_retention(current_mrr, expansion_mrr, churned_mrr, contraction_mrr)
    var gdr: Fraction = gross_dollar_retention(current_mrr, churned_mrr, contraction_mrr)
    
    // ========================================================================
    // Cashflow: Financial Health
    // ========================================================================
    
    param monthly_revenue: Currency<USD> = $100_000 {
        source: "billing_system",
        method: "observed",
        confidence: 1.0
    }
    
    param monthly_operating_expenses: Currency<USD> = $120_000 {
        source: "accounting",
        method: "observed",
        confidence: 0.95
    }
    
    param current_cash_balance: Currency<USD> = $800_000 {
        source: "bank_account",
        method: "observed",
        confidence: 1.0
    }
    
    param dso: Duration<Day> = 30d {
        source: "ar_aging_report",
        method: "derived",
        confidence: 0.90
    }
    
    // Calculate cashflow metrics
    var monthly_burn: Currency<USD> per Month = burn_rate(monthly_revenue, monthly_operating_expenses)
    var runway: Duration<Month> = runway_months(current_cash_balance, monthly_burn)
    
    var ar_balance: Currency<USD> = accounts_receivable(monthly_revenue, dso, 30d)
    
    var fcf: Currency<USD> = free_cash_flow(
        monthly_revenue - monthly_operating_expenses,  // Operating cash flow proxy
        $0  // No CapEx for SaaS
    )
    
    // ========================================================================
    // Business Health Constraints
    // ========================================================================
    
    constraint minimum_runway: runway >= 6mo {
        severity: warning,
        message: "Runway below 6 months - consider fundraising or cost reduction"
    }
    
    constraint healthy_ndr: ndr >= 1.0 {
        severity: warning,
        message: "NDR below 100% - losing revenue from existing customers"
    }
    
    constraint acceptable_churn: monthly_churn_rate <= 0.08/1mo {
        severity: warning,
        message: "Monthly churn above 8% threshold"
    }
    
    constraint positive_acquisition: new_customers_per_month >= 50 {
        severity: info,
        message: "Meeting minimum monthly customer acquisition target"
    }
}
"""
    result = _compile_pel_model(model)
    assert isinstance(result, dict)
    assert "model" in result
    assert result["model"]["name"] == "SaaS_Business_Complete"


@pytest.mark.integration
def test_ecommerce_with_cashflow_integration():
    """
    Integration test: E-commerce business with funnel and cashflow.
    
    Demonstrates:
    - Ecommerce funnel with cart abandonment
    - Working capital management (inventory + AR)
    - Cash conversion cycle
    """
    model = """
// E-commerce Business Model with Working Capital Management

model Ecommerce_Working_Capital {
    // ========================================================================
    // Funnel: Purchase Conversion
    // ========================================================================
    
    param monthly_product_views: Count<User> = 100_000 {
        source: "analytics",
        method: "observed",
        confidence: 0.95
    }
    
    param add_to_cart_rate: Fraction = 0.15 {
        source: "analytics",
        method: "derived",
        confidence: 0.90
    }
    
    param checkout_initiation_rate: Fraction = 0.60 {
        source: "analytics",
        method: "derived",
        confidence: 0.90
    }
    
    param purchase_completion_rate: Fraction = 0.75 {
        source: "analytics",
        method: "derived",
        confidence: 0.85
    }
    
    var purchase_funnel: Array<Count<User>> = ecommerce_checkout_funnel(
        monthly_product_views,
        add_to_cart_rate,
        checkout_initiation_rate,
        purchase_completion_rate
    )
    
    var monthly_purchases: Count<User> = purchase_funnel[3]
    var bottleneck_stage: Count = bottleneck_detection([
        add_to_cart_rate,
        checkout_initiation_rate,
        purchase_completion_rate
    ])
    
    // ========================================================================
    // Cashflow: Working Capital Cycle
    // ========================================================================
    
    param dso: Duration<Day> = 45d {
        source: "ar_report",
        method: "derived",
        confidence: 0.85,
        notes: "B2B customers pay on net-45 terms"
    }
    
    param inventory_days: Duration<Day> = 60d {
        source: "inventory_report",
        method: "derived",
        confidence: 0.80
    }
    
    param dpo: Duration<Day> = 30d {
        source: "ap_report",
        method: "derived",
        confidence: 0.85
    }
    
    var cash_conversion_cycle_days: Duration<Day> = cash_conversion_cycle(
        dso,
        inventory_days,
        dpo
    )
    
    // Revenue and expenses
    param monthly_revenue: Currency<USD> = $500_000 {
        source: "accounting",
        method: "observed",
        confidence: 1.0
    }
    
    param monthly_cogs: Currency<USD> = $300_000 {
        source: "accounting",
        method: "observed",
        confidence: 1.0
    }
    
    param monthly_opex: Currency<USD> = $150_000 {
        source: "accounting",
        method: "observed",
        confidence: 1.0
    }
    
    var gross_margin: Currency<USD> = monthly_revenue - monthly_cogs
    var operating_income: Currency<USD> = gross_margin - monthly_opex
    
    // AR and AP balances
    var ar_balance: Currency<USD> = accounts_receivable(monthly_revenue, dso, 45d)
    
    param daily_cogs: Currency<USD> per Day = $10_000/1d {
        source: "derived",
        method: "calculated",
        confidence: 0.90
    }
    
    var ap_balance: Currency<USD> = accounts_payable(monthly_cogs, dpo)
    
    // ========================================================================
    // Business Constraints
    // ========================================================================
    
    constraint acceptable_ccc: cash_conversion_cycle_days <= 90d {
        severity: warning,
        message: "CCC exceeding 90 days - consider improving payment terms or inventory turns"
    }
    
    constraint positive_margin: gross_margin > $0 {
        severity: fatal,
        message: "Negative gross margin - pricing below cost"
    }
    
    constraint conversion_target: monthly_purchases >= 5_000 {
        severity: info,
        message: "Meeting monthly purchase volume target"
    }
}
"""
    result = _compile_pel_model(model)
    assert isinstance(result, dict)
    assert "model" in result
    assert result["model"]["name"] == "Ecommerce_Working_Capital"


@pytest.mark.integration
def test_b2b_sales_with_retention_integration():
    """
    Integration test: B2B SaaS with sales funnel, retention, and cashflow.
    
    Demonstrates:
    - B2B sales funnel (Lead → MQL → SQL → Opp → Closed)
    - Enterprise retention dynamics
    - Runway planning with enterprise revenue
    """
    model = """
// Enterprise B2B SaaS Business Model

model Enterprise_B2B_SaaS {
    // ========================================================================
    // Funnel: Enterprise Sales Process
    // ========================================================================
    
    param monthly_leads: Count<Contact> = 500 {
        source: "marketing_automation",
        method: "observed",
        confidence: 0.95
    }
    
    param mql_rate: Fraction = 0.40 {
        source: "marketing",
        method: "derived",
        confidence: 0.85
    }
    
    param sql_rate: Fraction = 0.30 {
        source: "sales",
        method: "derived",
        confidence: 0.80
    }
    
    param opportunity_rate: Fraction = 0.50 {
        source: "sales",
        method: "derived",
        confidence: 0.75
    }
    
    param close_rate: Fraction = 0.25 {
        source: "sales",
        method: "derived",
        confidence: 0.70
    }
    
    var sales_funnel: Array<Count<Contact>> = b2b_sales_funnel(
        monthly_leads,
        mql_rate,
        sql_rate,
        opportunity_rate,
        close_rate
    )
    
    var new_customers: Count<Contact> = sales_funnel[4]
    
    // ========================================================================
    // Retention: Enterprise Customer Dynamics
    // ========================================================================
    
    param enterprise_churn_rate: Rate per Month = 0.02/1mo {
        source: "customer_success",
        method: "derived",
        confidence: 0.90,
        notes: "Lower churn for enterprise customers"
    }
    
    var enterprise_retention_rate: Fraction = retention_rate_from_churn(enterprise_churn_rate)
    var avg_enterprise_lifetime: Duration<Month> = customer_lifetime_months(enterprise_retention_rate)
    
    // Dollar retention
    param starting_arr: Currency<USD> = $2_000_000 {
        source: "finance",
        method: "observed",
        confidence: 1.0
    }
    
    param expansion_arr: Currency<USD> = $300_000 {
        source: "finance",
        method: "observed",
        confidence: 1.0,
        notes: "Strong upsell and cross-sell"
    }
    
    param churned_arr: Currency<USD> = $40_000 {
        source: "finance",
        method: "observed",
        confidence: 1.0
    }
    
    param contraction_arr: Currency<USD> = $20_000 {
        source: "finance",
        method: "observed",
        confidence: 1.0
    }
    
    var ndr: Fraction = net_dollar_retention(starting_arr, expansion_arr, churned_arr, contraction_arr)
    var gdr: Fraction = gross_dollar_retention(starting_arr, churned_arr, contraction_arr)
    
    var quick_ratio: Fraction = quick_ratio_retention(
        starting_arr / 12,  // New ARR as proxy (monthly)
        expansion_arr,
        churned_arr,
        contraction_arr
    )
    
    // ========================================================================
    // Cashflow: Enterprise Financial Management
    // ========================================================================
    
    param monthly_revenue: Currency<USD> = $200_000 {
        source: "billing",
        method: "observed",
        confidence: 1.0
    }
    
    param monthly_expenses: Currency<USD> = $280_000 {
        source: "accounting",
        method: "observed",
        confidence: 0.95
    }
    
    param cash_on_hand: Currency<USD> = $3_000_000 {
        source: "treasury",
        method: "observed",
        confidence: 1.0
    }
    
    var burn: Currency<USD> per Month = burn_rate(monthly_revenue, monthly_expenses)
    var runway: Duration<Month> = runway_months(cash_on_hand, burn)
    
    // Enterprise payment terms
    param enterprise_dso: Duration<Day> = 60d {
        source: "ar_report",
        method: "derived",
        confidence: 0.85,
        notes: "Net-60 standard for enterprise"
    }
    
    var ar_balance: Currency<USD> = accounts_receivable(monthly_revenue, enterprise_dso, 60d)
    
    // ========================================================================
    // Business Health Constraints
    // ========================================================================
    
    constraint strong_ndr: ndr >= 1.10 {
        severity: info,
        message: "Excellent NDR >110% shows strong expansion"
    }
    
    constraint sufficient_runway: runway >= 12mo {
        severity: warning,
        message: "Enterprise sales cycles require 12+ month runway"
    }
    
    constraint low_churn: enterprise_churn_rate <= 0.03/1mo {
        severity: info,
        message: "Enterprise churn within acceptable range"
    }
    
    constraint sales_efficiency: quick_ratio >= 3.0 {
        severity: warning,
        message: "Quick ratio below 3.0 indicates inefficient growth"
    }
}
"""
    result = _compile_pel_model(model)
    assert isinstance(result, dict)
    assert "model" in result
    assert result["model"]["name"] == "Enterprise_B2B_SaaS"
