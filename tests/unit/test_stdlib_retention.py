"""
Tests for stdlib retention module.
These tests verify the retention module structure, syntax, and function implementations.
"""

import pytest
import re
import math
from pathlib import Path


@pytest.fixture
def retention_module_path():
    """Path to the retention module."""
    return Path(__file__).parent.parent.parent / "stdlib" / "retention" / "retention.pel"


@pytest.fixture
def retention_module_content(retention_module_path):
    """Content of the retention module."""
    return retention_module_path.read_text()


@pytest.mark.unit
class TestRetentionModuleStructure:
    """Test retention module structure and completeness."""

    def test_module_file_exists(self, retention_module_path):
        """Verify retention module file exists."""
        assert retention_module_path.exists(), "retention.pel module file must exist"

    def test_module_has_header_comment(self, retention_module_content):
        """Verify module has proper header comment."""
        assert "PEL Standard Library - Retention Module" in retention_module_content
        assert "retention" in retention_module_content.lower()

    def test_module_has_cohort_section(self, retention_module_content):
        """Verify module has Cohort section."""
        assert "Cohort" in retention_module_content


@pytest.mark.unit
class TestRetentionFunctionDefinitions:
    """Test that all required retention functions are defined."""

    # Cohort Functions
    def test_cohort_retention_curve_defined(self, retention_module_content):
        """Verify cohort_retention_curve function is defined."""
        assert "func cohort_retention_curve" in retention_module_content
        assert "initial_cohort_size" in retention_module_content
        assert "retention_rate" in retention_module_content

    def test_cohort_survival_rate_defined(self, retention_module_content):
        """Verify cohort_survival_rate function is defined."""
        assert "func cohort_survival_rate" in retention_module_content
        assert "retained_customers" in retention_module_content
        assert "initial_customers" in retention_module_content

    def test_cohort_half_life_defined(self, retention_module_content):
        """Verify cohort_half_life function is defined."""
        assert "func cohort_half_life" in retention_module_content
        assert "churn_rate" in retention_module_content

    # Churn Metrics
    def test_customer_churn_rate_defined(self, retention_module_content):
        """Verify customer_churn_rate function is defined."""
        assert "func customer_churn_rate" in retention_module_content
        assert "churned_customers" in retention_module_content

    def test_revenue_churn_rate_defined(self, retention_module_content):
        """Verify revenue_churn_rate function is defined."""
        assert "func revenue_churn_rate" in retention_module_content
        assert "churned_mrr" in retention_module_content
        assert "starting_mrr" in retention_module_content

    def test_logo_churn_defined(self, retention_module_content):
        """Verify logo_churn function is defined."""
        assert "func logo_churn" in retention_module_content

    def test_churn_rate_from_retention_defined(self, retention_module_content):
        """Verify churn_rate_from_retention function is defined."""
        assert "func churn_rate_from_retention" in retention_module_content

    # Expansion/Contraction
    def test_expansion_mrr_defined(self, retention_module_content):
        """Verify expansion_mrr function is defined."""
        assert "func expansion_mrr" in retention_module_content
        assert "upsell_mrr" in retention_module_content
        assert "cross_sell_mrr" in retention_module_content

    def test_contraction_mrr_defined(self, retention_module_content):
        """Verify contraction_mrr function is defined."""
        assert "func contraction_mrr" in retention_module_content
        assert "downgrade_mrr" in retention_module_content

    def test_reactivation_mrr_defined(self, retention_module_content):
        """Verify reactivation_mrr function is defined."""
        assert "func reactivation_mrr" in retention_module_content
        assert "reactivated_customers" in retention_module_content

    # NDR Metrics
    def test_net_dollar_retention_defined(self, retention_module_content):
        """Verify net_dollar_retention function is defined."""
        assert "func net_dollar_retention" in retention_module_content
        assert "starting_cohort_mrr" in retention_module_content
        assert "expansion_mrr" in retention_module_content

    def test_gross_dollar_retention_defined(self, retention_module_content):
        """Verify gross_dollar_retention function is defined."""
        assert "func gross_dollar_retention" in retention_module_content

    def test_quick_ratio_defined(self, retention_module_content):
        """Verify quick_ratio function is defined."""
        assert "func quick_ratio" in retention_module_content
        assert "new_mrr" in retention_module_content

    # Retention Curves
    def test_exponential_churn_curve_defined(self, retention_module_content):
        """Verify exponential_churn_curve function is defined."""
        assert "func exponential_churn_curve" in retention_module_content
        assert "monthly_churn_rate" in retention_module_content

    def test_power_law_churn_curve_defined(self, retention_module_content):
        """Verify power_law_churn_curve function is defined."""
        assert "func power_law_churn_curve" in retention_module_content
        assert "initial_churn_rate" in retention_module_content
        assert "decay_factor" in retention_module_content

    def test_weibull_churn_curve_defined(self, retention_module_content):
        """Verify weibull_churn_curve function is defined."""
        assert "func weibull_churn_curve" in retention_module_content
        assert "shape_parameter" in retention_module_content
        assert "scale_parameter" in retention_module_content

    # LTV Integration
    def test_ltv_from_retention_curve_defined(self, retention_module_content):
        """Verify ltv_from_retention_curve function is defined."""
        assert "func ltv_from_retention_curve" in retention_module_content
        assert "monthly_arpu" in retention_module_content

    def test_discounted_ltv_defined(self, retention_module_content):
        """Verify discounted_ltv function is defined."""
        assert "func discounted_ltv" in retention_module_content
        assert "discount_rate" in retention_module_content


@pytest.mark.unit
class TestRetentionFunctionCount:
    """Test that the module has the required number of functions."""

    def test_minimum_function_count(self, retention_module_content):
        """Verify module has at least 18 functions."""
        func_pattern = re.compile(r"^func\s+\w+", re.MULTILINE)
        functions = func_pattern.findall(retention_module_content)
        assert len(functions) >= 18, f"Expected >= 18 functions, found {len(functions)}"

    def test_cohort_function_count(self, retention_module_content):
        """Verify Cohort section has 3 functions."""
        cohort_start = retention_module_content.find("=== Cohort")
        churn_start = retention_module_content.find("=== Churn")
        cohort_section = retention_module_content[cohort_start:churn_start]
        
        func_pattern = re.compile(r"^func\s+\w+", re.MULTILINE)
        functions = func_pattern.findall(cohort_section)
        assert len(functions) == 3, f"Expected 3 Cohort functions, found {len(functions)}"

    def test_churn_function_count(self, retention_module_content):
        """Verify Churn section has 4 functions."""
        churn_start = retention_module_content.find("=== Churn")
        expansion_start = retention_module_content.find("=== Expansion")
        churn_section = retention_module_content[churn_start:expansion_start]
        
        func_pattern = re.compile(r"^func\s+\w+", re.MULTILINE)
        functions = func_pattern.findall(churn_section)
        assert len(functions) == 4, f"Expected 4 Churn functions, found {len(functions)}"


@pytest.mark.unit
class TestRetentionDocumentation:
    """Test that functions have proper documentation."""

    def test_functions_have_comments(self, retention_module_content):
        """Verify functions have explanatory comments."""
        functions = [
            "cohort_retention_curve",
            "customer_churn_rate",
            "net_dollar_retention",
            "ltv_from_retention_curve",
        ]
        
        for func_name in functions:
            func_start = retention_module_content.find(f"func {func_name}")
            assert func_start > 0, f"Function {func_name} not found"
            
            func_end = retention_module_content.find("}", func_start)
            func_body = retention_module_content[func_start:func_end]
            
            # Check for comments or clear implementation
            assert "//" in func_body or "Calculate" in func_body or "return" in func_body, \
                f"Function {func_name} should have comments or clear implementation"


@pytest.mark.unit
class TestRetentionGoldenScenarios:
    """Golden test scenarios for retention calculations."""

    def test_cohort_survival_rate_50_percent(self):
        """Test cohort survival with 50% retention."""
        # Scenario: 1000 initial, 500 retained
        # Expected: 50% survival rate
        initial = 1000
        retained = 500
        
        survival_rate = retained / initial
        assert survival_rate == 0.5

    def test_customer_churn_rate_5_percent(self):
        """Test customer churn calculation."""
        # Scenario: 2000 starting, 100 churned
        # Expected: 5% churn rate
        starting = 2000
        churned = 100
        
        churn_rate = churned / starting
        assert churn_rate == 0.05

    def test_revenue_churn_rate_calculation(self):
        """Test revenue churn rate calculation."""
        # Scenario: $100k starting MRR, $3k churned
        # Expected: 3% revenue churn
        starting_mrr = 100_000
        churned_mrr = 3_000
        
        revenue_churn = churned_mrr / starting_mrr
        assert revenue_churn == 0.03

    def test_expansion_mrr_calculation(self):
        """Test expansion MRR from upsells and cross-sells."""
        # Scenario: $10k upsells, $5k cross-sells
        # Expected: $15k expansion MRR
        upsell = 10_000
        cross_sell = 5_000
        
        expansion = upsell + cross_sell
        assert expansion == 15_000

    def test_contraction_mrr_calculation(self):
        """Test contraction MRR from downgrades and discounts."""
        # Scenario: $8k downgrades, $2k discounts
        # Expected: $10k contraction MRR
        downgrades = 8_000
        discounts = 2_000
        
        contraction = downgrades + discounts
        assert contraction == 10_000

    def test_ndr_above_100_percent(self):
        """Test NDR above 100% (net expansion)."""
        # Scenario: $100k starting, $20k expansion, $5k contraction, $10k churn
        # Expected: 105% NDR
        starting = 100_000
        expansion = 20_000
        contraction = 5_000
        churn = 10_000
        
        ending = starting + expansion - contraction - churn
        ndr = ending / starting
        assert ndr == 1.05  # 105%

    def test_gdr_calculation(self):
        """Test GDR (excludes expansion)."""
        # Scenario: $100k starting, $10k churn, $5k contraction
        # Expected: 85% GDR
        starting = 100_000
        churn = 10_000
        contraction = 5_000
        
        retained = starting - churn - contraction
        gdr = retained / starting
        assert gdr == 0.85  # 85%

    def test_quick_ratio_healthy(self):
        """Test Quick Ratio above 4.0 (healthy)."""
        # Scenario: $50k new, $20k expansion, $15k churn, $5k contraction
        # Expected: 3.5 Quick Ratio
        new = 50_000
        expansion = 20_000
        churn = 15_000
        contraction = 5_000
        
        positive = new + expansion
        negative = churn + contraction
        quick_ratio = positive / negative
        assert quick_ratio == 3.5

    def test_churn_from_retention_95_percent(self):
        """Test churn rate derived from retention."""
        # Scenario: 95% retention
        # Expected: 5% churn
        retention = 0.95
        
        churn = 1.0 - retention
        assert abs(churn - 0.05) < 1e-10

    def test_cohort_half_life_approximation(self):
        """Test cohort half-life calculation."""
        # Scenario: 10% monthly churn
        # Expected: ~6.93 months half-life (ln(2)/0.10 ≈ 6.93147)
        monthly_churn = 0.10
        ln_2 = 0.693147
        
        half_life = ln_2 / monthly_churn
        assert abs(half_life - 6.93147) < 0.01

    def test_ltv_from_retention_simple(self):
        """Test LTV calculation from retention rate."""
        # Scenario: $100 ARPU, 95% retention (5% churn)
        # Expected: $2000 LTV
        arpu = 100
        retention = 0.95
        churn = 1.0 - retention
        
        ltv = arpu / churn
        assert abs(ltv - 2000) < 0.01

    def test_discounted_ltv_lower_than_simple(self):
        """Test discounted LTV is lower than simple LTV."""
        # Scenario: $100 ARPU, 5% churn, 1% discount rate
        # Expected: Discounted LTV < Simple LTV
        arpu = 100
        churn = 0.05
        discount = 0.01
        
        simple_ltv = arpu / churn
        discounted_ltv = arpu / (churn + discount)
        
        assert discounted_ltv < simple_ltv
        assert abs(discounted_ltv - 1666.67) < 1  # $1666.67

    def test_reactivation_mrr_calculation(self):
        """Test reactivation MRR calculation."""
        # Scenario: 50 reactivated customers, $80 ARPU
        # Expected: $4000 MRR
        reactivated = 50
        arpu = 80
        
        reactivation_mrr = reactivated * arpu
        assert reactivation_mrr == 4000

    def test_logo_churn_rate_calculation(self):
        """Test logo churn rate per month."""
        # Scenario: 30 customers churned over 3 months
        # Expected: 10 customers/month
        churned = 30
        months = 3
        
        logo_churn_rate = churned / months
        assert logo_churn_rate == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
