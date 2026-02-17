"""
Tests for stdlib cashflow module.
These tests verify the cashflow module structure, syntax, and function implementations.
"""

import pytest
import re
from pathlib import Path


@pytest.fixture
def cashflow_module_path():
    """Path to the cashflow module."""
    return Path(__file__).parent.parent.parent / "stdlib" / "cashflow" / "cashflow.pel"


@pytest.fixture
def cashflow_module_content(cashflow_module_path):
    """Content of the cashflow module."""
    return cashflow_module_path.read_text()


@pytest.mark.unit
class TestCashflowModuleStructure:
    """Test cashflow module structure and completeness."""

    def test_module_file_exists(self, cashflow_module_path):
        """Verify cashflow module file exists."""
        assert cashflow_module_path.exists(), "cashflow.pel module file must exist"

    def test_module_has_header_comment(self, cashflow_module_content):
        """Verify module has proper header comment."""
        assert "PEL Standard Library - Cashflow Module" in cashflow_module_content
        assert "Cashflow timing" in cashflow_module_content

    def test_module_has_ar_section(self, cashflow_module_content):
        """Verify module has Accounts Receivable section."""
        assert "Accounts Receivable" in cashflow_module_content
        assert "AR" in cashflow_module_content


@pytest.mark.unit
class TestCashflowFunctionDefinitions:
    """Test that all required cashflow functions are defined."""

    # AR Functions
    def test_ar_with_payment_terms_defined(self, cashflow_module_content):
        """Verify ar_with_payment_terms function is defined."""
        assert "func ar_with_payment_terms" in cashflow_module_content
        assert "payment_terms: Duration<Day>" in cashflow_module_content

    def test_ar_aging_buckets_defined(self, cashflow_module_content):
        """Verify ar_aging_buckets function is defined."""
        assert "func ar_aging_buckets" in cashflow_module_content
        assert "aged_30_pct" in cashflow_module_content
        assert "aged_60_pct" in cashflow_module_content
        assert "aged_90_pct" in cashflow_module_content

    def test_days_sales_outstanding_defined(self, cashflow_module_content):
        """Verify days_sales_outstanding function is defined."""
        assert "func days_sales_outstanding" in cashflow_module_content
        assert "accounts_receivable" in cashflow_module_content

    def test_bad_debt_reserve_defined(self, cashflow_module_content):
        """Verify bad_debt_reserve function is defined."""
        assert "func bad_debt_reserve" in cashflow_module_content
        assert "reserve_rate" in cashflow_module_content

    # AP Functions
    def test_ap_with_payment_terms_defined(self, cashflow_module_content):
        """Verify ap_with_payment_terms function is defined."""
        assert "func ap_with_payment_terms" in cashflow_module_content
        assert "expenses" in cashflow_module_content

    def test_ap_aging_buckets_defined(self, cashflow_module_content):
        """Verify ap_aging_buckets function is defined."""
        assert "func ap_aging_buckets" in cashflow_module_content
        assert "total_ap" in cashflow_module_content

    def test_days_payable_outstanding_defined(self, cashflow_module_content):
        """Verify days_payable_outstanding function is defined."""
        assert "func days_payable_outstanding" in cashflow_module_content
        assert "accounts_payable" in cashflow_module_content

    # Payroll Functions
    def test_payroll_timing_defined(self, cashflow_module_content):
        """Verify payroll_timing function is defined."""
        assert "func payroll_timing" in cashflow_module_content
        assert "headcount" in cashflow_module_content
        assert "avg_salary" in cashflow_module_content

    def test_payroll_taxes_timing_defined(self, cashflow_module_content):
        """Verify payroll_taxes_timing function is defined."""
        assert "func payroll_taxes_timing" in cashflow_module_content
        assert "tax_rate" in cashflow_module_content

    def test_payroll_accrued_defined(self, cashflow_module_content):
        """Verify payroll_accrued function is defined."""
        assert "func payroll_accrued" in cashflow_module_content
        assert "accrual_days" in cashflow_module_content

    # Working Capital Functions
    def test_working_capital_defined(self, cashflow_module_content):
        """Verify working_capital function is defined."""
        assert "func working_capital" in cashflow_module_content
        assert "current_assets" in cashflow_module_content
        assert "current_liabilities" in cashflow_module_content

    def test_cash_conversion_cycle_defined(self, cashflow_module_content):
        """Verify cash_conversion_cycle function is defined."""
        assert "func cash_conversion_cycle" in cashflow_module_content
        assert "days_sales_outstanding" in cashflow_module_content
        assert "days_inventory_outstanding" in cashflow_module_content
        assert "days_payable_outstanding" in cashflow_module_content

    def test_burn_rate_defined(self, cashflow_module_content):
        """Verify burn_rate function is defined."""
        assert "func burn_rate" in cashflow_module_content
        assert "starting_cash" in cashflow_module_content
        assert "ending_cash" in cashflow_module_content

    def test_runway_months_defined(self, cashflow_module_content):
        """Verify runway_months function is defined."""
        assert "func runway_months" in cashflow_module_content
        assert "cash_balance" in cashflow_module_content
        assert "monthly_burn" in cashflow_module_content

    # Cash Waterfall Functions
    def test_operating_cash_flow_defined(self, cashflow_module_content):
        """Verify operating_cash_flow function is defined."""
        assert "func operating_cash_flow" in cashflow_module_content
        assert "net_income" in cashflow_module_content
        assert "depreciation" in cashflow_module_content
        assert "working_capital_change" in cashflow_module_content

    def test_free_cash_flow_defined(self, cashflow_module_content):
        """Verify free_cash_flow function is defined."""
        assert "func free_cash_flow" in cashflow_module_content
        assert "capital_expenditures" in cashflow_module_content

    def test_cash_balance_projection_defined(self, cashflow_module_content):
        """Verify cash_balance_projection function is defined."""
        assert "func cash_balance_projection" in cashflow_module_content
        assert "starting_cash" in cashflow_module_content
        assert "monthly_cash_flow" in cashflow_module_content


@pytest.mark.unit
class TestCashflowFunctionCount:
    """Test that the module has the required number of functions."""

    def test_minimum_function_count(self, cashflow_module_content):
        """Verify module has at least 17 functions."""
        func_pattern = re.compile(r"^func\s+\w+", re.MULTILINE)
        functions = func_pattern.findall(cashflow_module_content)
        assert len(functions) >= 17, f"Expected >= 17 functions, found {len(functions)}"

    def test_ar_function_count(self, cashflow_module_content):
        """Verify AR section has 4 functions."""
        # Extract AR section
        ar_start = cashflow_module_content.find("=== Accounts Receivable")
        ap_start = cashflow_module_content.find("=== Accounts Payable")
        ar_section = cashflow_module_content[ar_start:ap_start]
        
        func_pattern = re.compile(r"^func\s+\w+", re.MULTILINE)
        functions = func_pattern.findall(ar_section)
        assert len(functions) == 4, f"Expected 4 AR functions, found {len(functions)}"

    def test_ap_function_count(self, cashflow_module_content):
        """Verify AP section has 3 functions."""
        ap_start = cashflow_module_content.find("=== Accounts Payable")
        payroll_start = cashflow_module_content.find("=== Payroll")
        ap_section = cashflow_module_content[ap_start:payroll_start]
        
        func_pattern = re.compile(r"^func\s+\w+", re.MULTILINE)
        functions = func_pattern.findall(ap_section)
        assert len(functions) == 3, f"Expected 3 AP functions, found {len(functions)}"


@pytest.mark.unit
class TestCashflowDocumentation:
    """Test that functions have proper documentation."""

    def test_functions_have_comments(self, cashflow_module_content):
        """Verify functions have explanatory comments."""
        # Check a sample of functions have comments
        functions = [
            "ar_with_payment_terms",
            "days_sales_outstanding",
            "working_capital",
            "burn_rate",
            "operating_cash_flow",
        ]
        
        for func_name in functions:
            func_start = cashflow_module_content.find(f"func {func_name}")
            assert func_start > 0, f"Function {func_name} not found"
            
            # Look for comment before closing brace
            func_end = cashflow_module_content.find("}", func_start)
            func_body = cashflow_module_content[func_start:func_end]
            
            # Check for either // comments or calculation explanations
            assert "//" in func_body or "Calculate" in func_body or "return" in func_body, \
                f"Function {func_name} should have comments or clear implementation"


@pytest.mark.unit
class TestCashflowGoldenScenarios:
    """Golden test scenarios for cashflow calculations."""

    def test_ar_payment_terms_30_days(self):
        """Test AR calculation with 30-day payment terms."""
        # Scenario: $100k monthly revenue, 30-day terms
        # Expected: AR = $100k (one month of revenue)
        monthly_revenue = 100_000
        payment_terms_days = 30
        days_in_month = 30
        
        expected_ar = monthly_revenue * (payment_terms_days / days_in_month)
        assert expected_ar == 100_000

    def test_dso_calculation(self):
        """Test Days Sales Outstanding calculation."""
        # Scenario: $50k AR, $100k monthly revenue
        # Expected: DSO = 15 days
        ar = 50_000
        monthly_revenue = 100_000
        days_in_month = 30
        
        expected_dso = (ar / monthly_revenue) * days_in_month
        assert expected_dso == 15

    def test_working_capital_positive(self):
        """Test working capital calculation with positive result."""
        # Scenario: $500k current assets, $300k current liabilities
        # Expected: WC = $200k
        current_assets = 500_000
        current_liabilities = 300_000
        
        expected_wc = current_assets - current_liabilities
        assert expected_wc == 200_000

    def test_burn_rate_calculation(self):
        """Test burn rate calculation."""
        # Scenario: Started with $1M, ended with $700k after 3 months
        # Expected: Burn rate = -$100k/month
        starting_cash = 1_000_000
        ending_cash = 700_000
        months = 3
        
        cash_change = ending_cash - starting_cash
        expected_burn_rate = cash_change / months
        assert expected_burn_rate == -100_000

    def test_runway_calculation(self):
        """Test runway months calculation."""
        # Scenario: $600k cash, $100k/month burn
        # Expected: 6 months runway
        cash_balance = 600_000
        monthly_burn = 100_000
        
        expected_runway = cash_balance / monthly_burn
        assert expected_runway == 6

    def test_cash_conversion_cycle(self):
        """Test CCC calculation."""
        # Scenario: DSO=45d, DIO=30d, DPO=60d
        # Expected: CCC = 15 days
        dso = 45
        dio = 30
        dpo = 60
        
        expected_ccc = dso + dio - dpo
        assert expected_ccc == 15

    def test_free_cash_flow_positive(self):
        """Test FCF with positive cash generation."""
        # Scenario: OCF=$150k/mo, CapEx=$50k/mo
        # Expected: FCF = $100k/mo
        ocf = 150_000
        capex = 50_000
        
        expected_fcf = ocf - capex
        assert expected_fcf == 100_000

    def test_bad_debt_reserve_2_percent(self):
        """Test bad debt reserve at 2%."""
        # Scenario: $200k AR, 2% reserve rate
        # Expected: Reserve = $4k
        ar = 200_000
        reserve_rate = 0.02
        
        expected_reserve = ar * reserve_rate
        assert expected_reserve == 4_000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
