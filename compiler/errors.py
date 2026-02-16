# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""
PEL Compiler Error System
Implements error reporting with codes E0xxx from language spec
"""

from dataclasses import dataclass


@dataclass
class SourceLocation:
    """Location in source code."""
    filename: str
    line: int
    column: int

    def __str__(self) -> str:
        return f"{self.filename}:{self.line}:{self.column}"



class CompilerError(Exception):
    """Base class for all compilation errors."""

    def __init__(
        self,
        code: str,
        message: str,
        location: SourceLocation | None = None,
        hint: str | None = None
    ) -> None:
        self.code = code
        self.message = message
        self.location = location
        self.hint = hint
        super().__init__(self._format())

    def _format(self) -> str:
        """Format error message."""
        parts = [f"error[{self.code}]: {self.message}"]

        if self.location:
            parts.insert(0, f"--> {self.location}")

        if self.hint:
            parts.append(f"  = hint: {self.hint}")

        return "\n".join(parts)


# === Lexical Errors (E00xx) ===

class LexicalError(CompilerError):
    """Lexical analysis errors."""
    pass


def lexical_error(msg: str, location: SourceLocation | None = None) -> LexicalError:
    """E0001: Generic lexical error."""
    return LexicalError("E0001", msg, location)


def invalid_number(text: str, location: SourceLocation | None = None) -> LexicalError:
    """E0002: Invalid number literal."""
    return LexicalError(
        "E0002",
        f"Invalid number literal: '{text}'",
        location,
        hint="Numbers must be valid integers or decimals (e.g., 100, 3.14)"
    )


def unterminated_string(location: SourceLocation | None = None) -> LexicalError:
    """E0003: Unterminated string literal."""
    return LexicalError(
        "E0003",
        "Unterminated string literal",
        location,
        hint="Strings must be closed with matching quote"
    )


# === Type Errors (E01xx) ===

class TypeError(CompilerError):
    """Type checking errors."""
    pass


def type_mismatch(expected: str, got: str, location: SourceLocation | None = None) -> TypeError:
    """E0100: Type mismatch."""
    return TypeError(
        "E0100",
        f"Type mismatch: expected {expected}, got {got}",
        location
    )


def undefined_variable(name: str, location: SourceLocation | None = None) -> TypeError:
    """E0101: Undefined variable."""
    return TypeError(
        "E0101",
        f"Undefined variable: '{name}'",
        location,
        hint="Variables must be declared before use"
    )


# === Dimensional Errors (E02xx) ===

class DimensionalError(CompilerError):
    """Dimensional analysis errors."""
    pass


def dimensional_mismatch(op: str, left: str, right: str, location: SourceLocation | None = None) -> DimensionalError:
    """E0200: Dimensional mismatch."""
    return DimensionalError(
        "E0200",
        f"Cannot {op} incompatible dimensions: {left} and {right}",
        location,
        hint="Arithmetic requires compatible units (e.g., Currency + Currency, not Currency + Rate)"
    )


def currency_mismatch(currency1: str, currency2: str, location: SourceLocation | None = None) -> DimensionalError:
    """E0203: Currency mismatch."""
    return DimensionalError(
        "E0203",
        f"Currency mismatch: {currency1} and {currency2}",
        location,
        hint="Convert currencies explicitly before arithmetic operations"
    )


def rate_unit_mismatch(unit1: str, unit2: str, location: SourceLocation | None = None) -> DimensionalError:
    """E0204: Rate unit mismatch."""
    return DimensionalError(
        "E0204",
        f"Rate unit mismatch: per {unit1} and per {unit2}",
        location,
        hint="Convert rates to common time unit"
    )


# === Time/Causality Errors (E03xx) ===

class CausalityError(CompilerError):
    """Causality violations."""
    pass


def future_reference(var_name: str, location: SourceLocation | None = None) -> CausalityError:
    """E0300: Future reference in TimeSeries."""
    return CausalityError(
        "E0300",
        f"Future reference: '{var_name}' references t+k where k > 0",
        location,
        hint="Models cannot look into the future (violates causality)"
    )


def cyclic_dependency(var_name: str, cycle: str, location: SourceLocation | None = None) -> CausalityError:
    """E0301: Cyclic dependency."""
    return CausalityError(
        "E0301",
        f"Cyclic dependency: {cycle}",
        location,
        hint="Variables cannot depend on themselves (directly or indirectly)"
    )


# === Provenance Errors (E04xx) ===

class ProvenanceError(CompilerError):
    """Provenance/metadata errors."""
    pass


def missing_provenance(param_name: str, location: SourceLocation | None = None) -> ProvenanceError:
    """E0400: Missing provenance block."""
    return ProvenanceError(
        "E0400",
        f"Missing provenance for parameter '{param_name}'",
        location,
        hint="All parameters must have provenance block with source, method, confidence"
    )


def missing_provenance_field(param_name: str, field: str, location: SourceLocation | None = None) -> ProvenanceError:
    """E0401: Missing required provenance field."""
    return ProvenanceError(
        "E0401",
        f"Missing required field '{field}' in provenance for '{param_name}'",
        location,
        hint="Provenance must include: source, method, confidence"
    )


def invalid_confidence(value: float, location: SourceLocation | None = None) -> ProvenanceError:
    """E0402: Invalid confidence value."""
    return ProvenanceError(
        "E0402",
        f"Invalid confidence: {value} (must be in [0.0, 1.0])",
        location
    )


# === Constraint Errors (E05xx) ===

class ConstraintError(CompilerError):
    """Constraint-related errors."""
    pass


def invalid_constraint_condition(msg: str, location: SourceLocation | None = None) -> ConstraintError:
    """E0500: Invalid constraint condition."""
    return ConstraintError(
        "E0500",
        f"Invalid constraint condition: {msg}",
        location,
        hint="Constraint conditions must be boolean expressions"
    )


def contradictory_constraints(constraint1: str, constraint2: str, location: SourceLocation | None = None) -> ConstraintError:
    """E0501: Contradictory constraints."""
    return ConstraintError(
        "E0501",
        f"Contradictory constraints: '{constraint1}' conflicts with '{constraint2}'",
        location,
        hint="Constraints cannot be simultaneously satisfied"
    )


# === Distribution Errors (E06xx) ===

class DistributionError(CompilerError):
    """Distribution parameter errors."""
    pass


def invalid_distribution_param(dist_type: str, param: str, reason: str, location: SourceLocation | None = None) -> DistributionError:
    """E0600: Invalid distribution parameter."""
    return DistributionError(
        "E0600",
        f"Invalid {dist_type} parameter '{param}': {reason}",
        location
    )


def invalid_correlation(var1: str, var2: str, coef: float, location: SourceLocation | None = None) -> DistributionError:
    """E0601: Invalid correlation coefficient."""
    return DistributionError(
        "E0601",
        f"Invalid correlation between '{var1}' and '{var2}': {coef} (must be in [-1, 1])",
        location
    )


def correlation_matrix_not_psd(location: SourceLocation | None = None) -> DistributionError:
    """E0602: Correlation matrix not positive semi-definite."""
    return DistributionError(
        "E0602",
        "Correlation matrix is not positive semi-definite",
        location,
        hint="Check correlation coefficients; they may be inconsistent"
    )


# === Parser Errors (E07xx) ===

class ParseError(CompilerError):
    """Parsing errors."""
    pass


def unexpected_token(expected: str, got: str, location: SourceLocation | None = None) -> ParseError:
    """E0700: Unexpected token."""
    return ParseError(
        "E0700",
        f"Expected {expected}, got {got}",
        location
    )


def syntax_error(msg: str, location: SourceLocation | None = None) -> ParseError:
    """E0701: Generic syntax error."""
    return ParseError(
        "E0701",
        f"Syntax error: {msg}",
        location
    )


# === Internal Errors (E99xx) ===

class InternalError(CompilerError):
    """Internal compiler errors (bugs)."""

    def __init__(self, message: str, location: SourceLocation | None = None) -> None:
        super().__init__(
            "E9999",
            f"Internal compiler error: {message}",
            location,
            hint="This is a compiler bug. Please report at https://github.com/pel-lang/pel/issues"
        )
