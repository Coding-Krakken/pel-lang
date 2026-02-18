"""
Semantic Type Contracts for PEL Language

This module defines semantic contracts that specify valid type conversions with explicit
justification. Contracts provide a formal mechanism for representing domain knowledge about
when and why type conversions are semantically valid, beyond dimensional correctness.

Key Principles:
- Explicit > Implicit: All conversions must be explicitly justified with a contract
- Semantic Validity: Type correctness alone is insufficient; conversions must make domain sense
- Extensible: Users can define custom contracts for domain-specific rules
- Discoverable: Contract system provides clear guidance on valid patterns
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ConversionReason(Enum):
    """Categories of semantic justification for type conversions."""
    IDENTITY = "identity"  # No actual conversion needed
    COUNTING = "counting"  # Summing/aggregating counts or items
    NORMALIZATION = "normalization"  # Converting rate/quotient to meaningful unit
    DIVISION = "division"  # Result of a division operation
    SCALING = "scaling"  # Unit conversion within same dimension
    AGGREGATION = "aggregation"  # Combining multiple values
    NATURAL_CAST = "natural_cast"  # Type coercion that loses no information
    DOMAIN_SPECIFIC = "domain_specific"  # Custom business-logic justified


@dataclass
class ValidConversion:
    """Represents a single valid conversion rule between two types."""
    source_type: str
    target_type: str
    reason: ConversionReason
    requires_condition: str | None = None
    documentation: str = ""
    examples: list = field(default_factory=list)
    constraints: dict[str, Any] = field(default_factory=dict)

    def __str__(self):
        return f"{self.source_type} → {self.target_type} ({self.reason.value})"


@dataclass
class SemanticContract:
    """
    A semantic contract defines valid type conversions with explicit justification.

    Contracts serve as a bridge between:
    1. Type System (what's dimensionally valid)
    2. Domain Knowledge (what makes semantic sense)
    3. User Intent (why this conversion is appropriate)

    Attributes:
        name: Unique identifier for this contract (e.g., "RevenuePerUnit_to_Price")
        source_type: Origin type pattern (e.g., "Quotient<Currency, Count>")
        target_type: Destination type (e.g., "Currency")
        reason: Why this conversion is semantically valid
        description: Plain English explanation of the domain logic
        constraints: Conditions that must be true for conversion to apply
        examples: Concrete use cases demonstrating this contract
        references: Links to spec sections justifying this contract
    """
    name: str
    source_type: str
    target_type: str
    reason: ConversionReason
    description: str
    constraints: dict[str, Any] = field(default_factory=dict)
    examples: list = field(default_factory=list)
    references: list = field(default_factory=list)

    def matches(self, src_type: str, tgt_type: str) -> bool:
        """Check if this contract applies to a given conversion."""
        return self._pattern_matches(src_type, self.source_type) and tgt_type == self.target_type

    @staticmethod
    def _pattern_matches(actual: str, pattern: str) -> bool:
        """Check if actual type matches pattern (with wildcard support)."""
        # Exact match
        if actual == pattern:
            return True
        # Pattern with generics like "Quotient<*>" matches "Quotient<Currency, Count>"
        if pattern.endswith("<*>"):
            base_pattern = pattern[:-3]  # Remove "<*>"
            return actual.startswith(base_pattern + "<")
        return False

    def validate_conversion(self, context: dict[str, Any]) -> tuple[bool, str | None]:
        """
        Validate that conversion constraints are satisfied in the given context.

        Returns:
            (is_valid, error_message)
        """
        for constraint_name, constraint_check in self.constraints.items():
            # Basic constraint validation
            if callable(constraint_check):
                try:
                    result = constraint_check(context)
                    if not result:
                        return False, f"Constraint '{constraint_name}' not satisfied"
                except Exception as e:
                    return False, f"Error checking constraint '{constraint_name}': {str(e)}"
        return True, None

    def __str__(self):
        return f"Contract: {self.name}\n  {self.source_type} → {self.target_type}\n  Reason: {self.reason.value}"


# ============================================================================
# Semantic Contract Registry
# ============================================================================

class SemanticContracts:
    """Global registry of semantic contracts for the PEL language."""

    # Storage for all registered contracts
    _contracts: dict[str, SemanticContract] = {}

    @classmethod
    def register(cls, contract: SemanticContract) -> None:
        """Register a new semantic contract."""
        if contract.name in cls._contracts:
            raise ValueError(f"Contract '{contract.name}' is already registered")
        cls._contracts[contract.name] = contract

    @classmethod
    def get(cls, name: str) -> SemanticContract | None:
        """Retrieve a contract by name."""
        return cls._contracts.get(name)

    @classmethod
    def find_conversions(cls, source_type: str, target_type: str) -> list:
        """Find all contracts that allow conversion from source to target type."""
        matches = []
        for contract in cls._contracts.values():
            if contract.matches(source_type, target_type):
                matches.append(contract)
        return matches

    @classmethod
    def all_contracts(cls) -> list:
        """Get all registered contracts."""
        return list(cls._contracts.values())

    @classmethod
    def describe_conversions(cls, target_type: str) -> str:
        """Generate human-readable description of how to convert TO a target type."""
        contracts = [c for c in cls._contracts.values() if c.target_type == target_type]
        if not contracts:
            return f"No conversion contracts available for {target_type}"

        description = f"\nValid conversions to {target_type}:\n"
        for contract in contracts:
            description += f"  • {contract.source_type} → {target_type}\n"
            description += f"    ({contract.reason.value})\n"
            if contract.description:
                description += f"    {contract.description}\n"
        return description


# ============================================================================
# Built-in Semantic Contracts
# ============================================================================

# Contract: Revenue per Unit -> Price
REVENUE_PER_UNIT_TO_PRICE = SemanticContract(
    name="RevenuePerUnit_to_Price",
    source_type="Quotient<Currency, Count>",
    target_type="Currency",
    reason=ConversionReason.NORMALIZATION,
    description=(
        "When revenue (Currency) is divided by unit count (Count), the result represents "
        "price or revenue per unit. This can be treated as a Currency in contexts where "
        "individual unit economics are relevant (e.g., pricing, margin analysis)."
    ),
    examples=[
        "annual_revenue / active_customers = revenue_per_customer (Currency)",
        "subscription_fee / billing_periods = price_per_period (Currency)",
    ],
    references=[
        "spec/pel_type_system.md#revenue-normalization",
        "spec/pel_benchmark_suite.md#unit-economics",
    ],
    constraints={
        "numerator_is_revenue": lambda ctx: ctx.get("numerator_dimension") == "Currency",
        "denominator_is_count": lambda ctx: ctx.get("denominator_type") == "Count",
    }
)

# Contract: Rate Normalization
RATE_NORMALIZATION = SemanticContract(
    name="RateNormalization",
    source_type="Quotient<Currency, Duration>",
    target_type="Currency",
    reason=ConversionReason.NORMALIZATION,
    description=(
        "MRR (Monthly Recurring Revenue) or other time-normalized revenue is a Currency-like "
        "value even though it results from division. The time dimension is part of the metric's "
        "definition, not a separate dimension to track."
    ),
    examples=[
        "annual_revenue / 12 = monthly_recurring_revenue (Currency)",
        "subscription_value / contract_months = price_per_month (Currency)",
    ],
    references=[
        "spec/pel_benchmark_suite.md#recurring-revenue",
        "spec/pel_type_system.md#time-normalized-metrics",
    ]
)

# Contract: Fraction from Ratio
FRACTION_FROM_RATIO = SemanticContract(
    name="FractionFromRatio",
    source_type="Quotient<Count, Count>",
    target_type="Fraction",
    reason=ConversionReason.COUNTING,
    description=(
        "When a count is divided by another count (e.g., successful transactions / total transactions), "
        "the result is naturally a Fraction representing ratio, percentage, or probability."
    ),
    examples=[
        "successful_txn / total_txn = success_rate (Fraction)",
        "active_customers / total_customers = activation_ratio (Fraction)",
        "churned_accounts / start_accounts = churn_rate (Fraction)",
    ],
    references=[
        "spec/pel_type_system.md#quotient-semantics",
    ]
)

# Contract: Average from Total
AVERAGE_FROM_TOTAL = SemanticContract(
    name="AverageFromTotal",
    source_type="Quotient<Currency, Count>",
    target_type="Fraction",
    reason=ConversionReason.COUNTING,
    description=(
        "In rare cases, revenue-per-unit can be expressed as a Fraction when modeling "
        "unit economics as a ratio (e.g., cost as fraction of revenue). Use with caution "
        "and explicit documentation."
    ),
    examples=[
        "cost_of_goods_sold / revenue_per_unit = cost_ratio (Fraction)",
    ],
    references=[
        "spec/pel_benchmark_suite.md#cost-modeling",
    ]
)

# Contract: Count Aggregation
COUNT_AGGREGATION = SemanticContract(
    name="CountAggregation",
    source_type="Quotient<Count, Duration>",
    target_type="Count",
    reason=ConversionReason.COUNTING,
    description=(
        "A rate of count per time unit can be treated as a Count in annual/periodic contexts. "
        "Example: monthly_registrations (count/month) can become annual registrations (count). "
        "Requires explicit time window specification."
    ),
    examples=[
        "monthly_signups * 12 = annual_signups (Count)",
        "daily_active_users * 30 = approx_monthly_active (Count)",
    ],
    references=[
        "spec/pel_type_system.md#temporal-aggregation",
    ]
)

# Contract: Quotient Normalization
QUOTIENT_NORMALIZATION = SemanticContract(
    name="QuotientNormalization",
    source_type="Quotient<*>",
    target_type="Fraction",
    reason=ConversionReason.NORMALIZATION,
    description=(
        "Any quotient can be normalized to a dimensionless Fraction when the semantics "
        "of division are explicitly documented. Use this sparingly."
    ),
    examples=[],
    references=[
        "spec/pel_type_system.md#quotient-semantics",
    ]
)

# Contract: Identity (type coercion with same meaning)
IDENTITY_WITH_SCALARS = SemanticContract(
    name="IdentityWithScalars",
    source_type="Count",
    target_type="Fraction",
    reason=ConversionReason.IDENTITY,
    description=(
        "Pure counts can be used where Fractions are expected if they represent "
        "dimensionless ratios (e.g., describing one item out of one item = 1.0 fraction)."
    ),
    examples=[],
    references=[]
)


# Register all built-in contracts
def _initialize_builtin_contracts():
    """Initialize all built-in semantic contracts."""
    contracts = [
        REVENUE_PER_UNIT_TO_PRICE,
        RATE_NORMALIZATION,
        FRACTION_FROM_RATIO,
        AVERAGE_FROM_TOTAL,
        COUNT_AGGREGATION,
        QUOTIENT_NORMALIZATION,
        IDENTITY_WITH_SCALARS,
    ]
    for contract in contracts:
        SemanticContracts.register(contract)


# Initialize on module load
_initialize_builtin_contracts()
