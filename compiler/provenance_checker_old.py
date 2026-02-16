# type: ignore
# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""PEL Provenance Checker - Verify assumption completeness
"""

from pel.compiler.ast_nodes import Model
from pel.compiler.errors import (
    ProvenanceError,
    invalid_confidence,
    missing_provenance,
    missing_provenance_field,
)


class ProvenanceChecker:
    """Verify all parameters have complete provenance."""

    def __init__(self, min_completeness: float = 0.90):
        self.min_completeness = min_completeness

    def check(self, model: Model):
        """Check provenance completeness."""
        total_params = len(model.params)
        complete_params = 0

        for param in model.params:
            if param.provenance is None:
                raise missing_provenance(param.name)

            # Check required fields
            prov = param.provenance
            if not prov.source:
                raise missing_provenance_field(param.name, "source")
            if not prov.method:
                raise missing_provenance_field(param.name, "method")
            if prov.confidence is None:
                raise missing_provenance_field(param.name, "confidence")

            # Validate confidence range
            if not 0.0 <= prov.confidence <= 1.0:
                raise invalid_confidence(prov.confidence)

            # Count as complete if all required fields present
            if prov.source and prov.method and prov.confidence is not None:
                complete_params += 1

        # Check completeness threshold
        if total_params > 0:
            completeness = complete_params / total_params
            if completeness < self.min_completeness:
                raise ProvenanceError(
                    "E0400",
                    f"Assumption completeness below threshold: {completeness:.2f} < {self.min_completeness:.2f}",
                    hint=f"{complete_params} of {total_params} parameters have complete provenance"
                )
