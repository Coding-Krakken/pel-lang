"""
Tests for PEL Semantic Contracts System

This module tests the semantic contract framework that documents valid type
conversions beyond dimensional correctness, capturing business logic and domain
assumptions that justify conversions.
"""

import pytest
from compiler.semantic_contracts import (
    SemanticContract,
    SemanticContracts,
    ConversionReason,
    ValidConversion,
    REVENUE_PER_UNIT_TO_PRICE,
    RATE_NORMALIZATION,
    FRACTION_FROM_RATIO,
    AVERAGE_FROM_TOTAL,
    COUNT_AGGREGATION,
    QUOTIENT_NORMALIZATION,
    IDENTITY_WITH_SCALARS,
)


class TestSemanticContract:
    """Test individual semantic contract functionality."""

    def test_contract_creation(self):
        """Test creating a semantic contract."""
        contract = SemanticContract(
            name="TestContract",
            source_type="Quotient<Currency, Count>",
            target_type="Currency",
            reason=ConversionReason.NORMALIZATION,
            description="Test conversion",
        )
        assert contract.name == "TestContract"
        assert contract.source_type == "Quotient<Currency, Count>"
        assert contract.target_type == "Currency"
        assert contract.reason == ConversionReason.NORMALIZATION

    def test_contract_matches_exact(self):
        """Test exact type pattern matching."""
        contract = REVENUE_PER_UNIT_TO_PRICE
        assert contract.matches("Quotient<Currency, Count>", "Currency")
        assert not contract.matches("Quotient<Count, Count>", "Currency")
        assert not contract.matches("Currency", "Currency")

    def test_contract_matches_wildcard(self):
        """Test wildcard pattern matching."""
        contract = QUOTIENT_NORMALIZATION
        assert contract.matches("Quotient<Currency, Count>", "Fraction")
        assert contract.matches("Quotient<Count, Duration>", "Fraction")
        assert contract.matches("Quotient<Currency, Duration>", "Fraction")
        assert not contract.matches("Currency", "Fraction")

    def test_contract_str_representation(self):
        """Test string representation of contracts."""
        contract = REVENUE_PER_UNIT_TO_PRICE
        str_repr = str(contract)
        assert "Revenue" in str_repr or "Quotient" in str_repr

    def test_contract_validate_with_constraints(self):
        """Test constraint validation in contracts."""
        contract = REVENUE_PER_UNIT_TO_PRICE
        
        # Valid context
        valid_context = {
            "numerator_dimension": "Currency",
            "denominator_type": "Count",
        }
        is_valid, error = contract.validate_conversion(valid_context)
        assert is_valid
        assert error is None

    def test_contract_exception_in_constraint(self):
        """Test handling of exceptions in constraint checks."""
        contract = SemanticContract(
            name="BadConstraintContract",
            source_type="Currency",
            target_type="Count",
            reason=ConversionReason.DOMAIN_SPECIFIC,
            description="Test",
            constraints={
                "will_fail": lambda ctx: ctx["missing_key"],
            },
        )
        is_valid, error = contract.validate_conversion({})
        assert not is_valid
        assert "Error checking constraint" in error


class TestSemanticContractsRegistry:
    """Test the global semantic contracts registry."""

    def test_registry_has_builtin_contracts(self):
        """Test that built-in contracts are registered."""
        assert SemanticContracts.get("RevenuePerUnit_to_Price") is not None
        assert SemanticContracts.get("RateNormalization") is not None
        assert SemanticContracts.get("FractionFromRatio") is not None

    def test_find_conversions_single_match(self):
        """Test finding a single applicable contract."""
        contracts = SemanticContracts.find_conversions(
            "Quotient<Currency, Count>", "Currency"
        )
        assert len(contracts) > 0
        assert any(c.name == "RevenuePerUnit_to_Price" for c in contracts)

    def test_find_conversions_wildcard_match(self):
        """Test finding contracts with wildcard patterns."""
        contracts = SemanticContracts.find_conversions(
            "Quotient<Currency, Count>", "Fraction"
        )
        assert len(contracts) > 0
        assert any(c.name == "QuotientNormalization" for c in contracts)

    def test_find_conversions_no_match(self):
        """Test finding conversions when no contract exists."""
        contracts = SemanticContracts.find_conversions(
            "Currency", "Quotient"
        )
        # Should return empty list (no contracts found)
        assert len(contracts) == 0

    def test_all_contracts_accessible(self):
        """Test getting all registered contracts."""
        all_contracts = SemanticContracts.all_contracts()
        assert len(all_contracts) >= 7
        names = [c.name for c in all_contracts]
        assert "RevenuePerUnit_to_Price" in names
        assert "RateNormalization" in names
        assert "FractionFromRatio" in names

    def test_describe_conversions_single_target(self):
        """Test generating conversion description for a target type."""
        description = SemanticContracts.describe_conversions("Currency")
        assert "Currency" in description
        assert "→" in description or "->" in description

    def test_describe_conversions_no_contracts(self):
        """Test handling when no conversions exist for target."""
        description = SemanticContracts.describe_conversions("UnknownType")
        assert "UnknownType" in description


class TestBuiltinContracts:
    """Test each built-in semantic contract."""

    def test_revenue_per_unit_to_price(self):
        """Test RevenuePerUnit_to_Price contract."""
        contract = REVENUE_PER_UNIT_TO_PRICE
        assert contract.name == "RevenuePerUnit_to_Price"
        assert contract.source_type == "Quotient<Currency, Count>"
        assert contract.target_type == "Currency"
        assert contract.reason == ConversionReason.NORMALIZATION
        assert len(contract.examples) > 0

    def test_rate_normalization(self):
        """Test RateNormalization contract."""
        contract = RATE_NORMALIZATION
        assert contract.name == "RateNormalization"
        assert contract.source_type == "Quotient<Currency, Duration>"
        assert contract.target_type == "Currency"
        assert "MRR" in contract.description or "monthly" in contract.description

    def test_fraction_from_ratio(self):
        """Test FractionFromRatio contract."""
        contract = FRACTION_FROM_RATIO
        assert contract.name == "FractionFromRatio"
        assert contract.source_type == "Quotient<Count, Count>"
        assert contract.target_type == "Fraction"
        assert contract.reason == ConversionReason.COUNTING

    def test_average_from_total(self):
        """Test AverageFromTotal contract."""
        contract = AVERAGE_FROM_TOTAL
        assert contract.name == "AverageFromTotal"
        assert contract.source_type == "Quotient<Currency, Count>"
        assert contract.target_type == "Fraction"

    def test_count_aggregation(self):
        """Test CountAggregation contract."""
        contract = COUNT_AGGREGATION
        assert contract.name == "CountAggregation"
        assert contract.source_type == "Quotient<Count, Duration>"
        assert contract.target_type == "Count"
        # Check for registration or sign or example in description
        assert any(word in contract.description.lower() for word in ["registration", "signup", "example", "monthly"])

    def test_quotient_normalization(self):
        """Test QuotientNormalization contract (wildcard)."""
        contract = QUOTIENT_NORMALIZATION
        assert contract.name == "QuotientNormalization"
        assert contract.source_type == "Quotient<*>"
        assert contract.target_type == "Fraction"

    def test_identity_with_scalars(self):
        """Test IdentityWithScalars contract."""
        contract = IDENTITY_WITH_SCALARS
        assert contract.name == "IdentityWithScalars"
        assert contract.source_type == "Count"
        assert contract.target_type == "Fraction"


class TestConversionReason:
    """Test the ConversionReason enum."""

    def test_all_reasons_exist(self):
        """Test that all expected conversion reasons exist."""
        assert ConversionReason.IDENTITY.value == "identity"
        assert ConversionReason.COUNTING.value == "counting"
        assert ConversionReason.NORMALIZATION.value == "normalization"
        assert ConversionReason.DIVISION.value == "division"
        assert ConversionReason.SCALING.value == "scaling"
        assert ConversionReason.AGGREGATION.value == "aggregation"
        assert ConversionReason.NATURAL_CAST.value == "natural_cast"
        assert ConversionReason.DOMAIN_SPECIFIC.value == "domain_specific"


class TestValidConversion:
    """Test the ValidConversion data class."""

    def test_valid_conversion_creation(self):
        """Test creating a valid conversion."""
        conversion = ValidConversion(
            source_type="Quotient<Currency, Count>",
            target_type="Currency",
            reason=ConversionReason.NORMALIZATION,
            documentation="Test conversion",
        )
        assert conversion.source_type == "Quotient<Currency, Count>"
        assert conversion.target_type == "Currency"

    def test_valid_conversion_with_conditions(self):
        """Test valid conversion with conditions."""
        conversion = ValidConversion(
            source_type="Currency",
            target_type="Count",
            reason=ConversionReason.DOMAIN_SPECIFIC,
            requires_condition="value is positive",
        )
        assert conversion.requires_condition == "value is positive"


class TestSemanticContractEdgeCases:
    """Test edge cases and error handling."""

    def test_duplicate_contract_registration(self):
        """Test that duplicate contract names raise errors."""
        # Note: Contracts are initialized on module load, so we test the mechanism
        # by attempting to register a duplicate
        with pytest.raises(ValueError, match="already registered"):
            SemanticContracts.register(REVENUE_PER_UNIT_TO_PRICE)

    def test_contract_pattern_matching_edge_cases(self):
        """Test pattern matching with edge cases."""
        # Exact match
        assert SemanticContract._pattern_matches(
            "Quotient<Currency, Count>",
            "Quotient<Currency, Count>"
        )
        
        # Wildcard match
        assert SemanticContract._pattern_matches(
            "Quotient<Currency, Duration>",
            "Quotient<*>"
        )
        
        # No match
        assert not SemanticContract._pattern_matches(
            "Currency",
            "Count"
        )
        
        assert not SemanticContract._pattern_matches(
            "Currency",
            "Quotient<*>"
        )

    def test_contract_with_empty_examples(self):
        """Test contracts with no or empty examples."""
        contract = SemanticContract(
            name="MinimalContract",
            source_type="Type1",
            target_type="Type2",
            reason=ConversionReason.DOMAIN_SPECIFIC,
            description="Minimal",
            examples=[],
        )
        assert len(contract.examples) == 0
        assert str(contract)  # Should not crash

    def test_contract_documentation_generation(self):
        """Test that contract documentation is generated correctly."""
        description = SemanticContracts.describe_conversions("Currency")
        assert isinstance(description, str)
        assert len(description) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
