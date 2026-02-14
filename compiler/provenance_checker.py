# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""PEL Provenance Checker - Verify assumption completeness and metadata quality
Implements governance requirements from spec/pel_governance_spec.md
"""

from compiler.ast_nodes import Model, ParamDecl
from compiler.errors import SourceLocation


class ProvenanceError(Exception):
    """Provenance validation error."""

    def __init__(self, message: str, location: SourceLocation | None = None):
        self.message = message
        self.location = location
        super().__init__(message)


class ProvenanceChecker:
    """Check provenance completeness for all parameters."""

    # Required provenance fields
    REQUIRED_FIELDS = ["source", "method", "confidence"]

    # Recommended fields
    RECOMMENDED_FIELDS = ["freshness", "owner"]

    # Valid method values
    VALID_METHODS = [
        "observed",  # Direct observation from data
        "fitted",  # Statistical fitting
        "derived",  # Calculated from other parameters
        "expert_estimate",  # Subject matter expert judgment
        "external_research",  # Published research/reports
        "assumption",  # Explicit assumption
    ]

    def __init__(self):
        self.errors: list[ProvenanceError] = []
        self.warnings: list[str] = []
        self.completeness_score = 0.0

    def check(self, model: Model) -> Model:
        """Check provenance for entire model."""
        if not model.params:
            return model

        total_fields_possible = len(model.params) * (
            len(self.REQUIRED_FIELDS) + len(self.RECOMMENDED_FIELDS)
        )
        total_fields_present = 0

        for param in model.params:
            param_score = self.check_param_provenance(param)
            total_fields_present += param_score

        # Calculate completeness score
        self.completeness_score = (
            total_fields_present / total_fields_possible if total_fields_possible > 0 else 1.0
        )

        return model

    def check_param_provenance(self, param: ParamDecl) -> float:
        """Check provenance for a single parameter. Returns score (0-1)."""
        if not param.provenance:
            self.errors.append(
                ProvenanceError(f"Parameter '{param.name}' missing provenance block")
            )
            return 0.0

        provenance = param.provenance
        fields_present = 0

        # Check required fields
        for field in self.REQUIRED_FIELDS:
            if field not in provenance:
                self.errors.append(
                    ProvenanceError(
                        f"Parameter '{param.name}' missing required provenance field: {field}"
                    )
                )
            else:
                fields_present += 1
                if field == "confidence":
                    self.check_confidence_field(param.name, provenance[field])
                elif field == "method":
                    self.check_method_field(param.name, provenance[field])

        # Check recommended fields
        for field in self.RECOMMENDED_FIELDS:
            if field in provenance:
                fields_present += 1

        return fields_present

    def check_method_field(self, param_name: str, method: any):
        """Validate method field."""
        if not isinstance(method, str) or not method.strip():
            self.errors.append(
                ProvenanceError(f"Parameter '{param_name}' method must be a non-empty string")
            )
            return

        if method not in self.VALID_METHODS:
            self.errors.append(
                ProvenanceError(
                    f"Parameter '{param_name}' method must be one of {self.VALID_METHODS}, got {method!r}"
                )
            )

    def check_confidence_field(self, param_name: str, confidence: any):
        """Validate confidence field."""
        try:
            conf_value = float(confidence)
            if not (0.0 <= conf_value <= 1.0):
                self.errors.append(
                    ProvenanceError(
                        f"Parameter '{param_name}' confidence must be in range [0.0, 1.0], got {conf_value}"
                    )
                )
        except (ValueError, TypeError):
            self.errors.append(
                ProvenanceError(f"Parameter '{param_name}' confidence must be a number")
            )

    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def get_errors(self) -> list[ProvenanceError]:
        return self.errors

    def get_completeness_score(self) -> float:
        return self.completeness_score
