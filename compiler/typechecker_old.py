# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""PEL Type Checker - Bidirectional type checking with dimensional analysis
Simplified reference implementation
"""

from pel.compiler.ast_nodes import *
from pel.compiler.errors import dimensional_mismatch, type_mismatch, undefined_variable


class TypeChecker:
    """Type check AST with dimensional analysis."""

    def __init__(self):
        self.env = {}  # name -> Type

    def check(self, model: Model) -> Model:
        """Type check entire model."""
        # Build environment from params and vars
        for param in model.params:
            self.env[param.name] = param.type_annotation

        for var in model.vars:
            if var.type_annotation:
                self.env[var.name] = var.type_annotation
            elif var.value:
                # Infer type from value
                inferred_type = self.infer(var.value)
                var.type_annotation = inferred_type
                self.env[var.name] = inferred_type

        # Type check all expressions (stub: just validate, don't transform)
        for param in model.params:
            self.check_expr(param.value, param.type_annotation)

        for constraint in model.constraints:
            self.check_expr(constraint.condition, Type(type_kind="Bool"))

        return model  # In full implementation, return TypedModel

    def infer(self, expr: Expression) -> Type:
        """Infer type of expression (synthesis)."""
        if isinstance(expr, Literal):
            if isinstance(expr.value, (int, float)):
                return Type(type_kind="Number")
            elif isinstance(expr.value, str):
                return Type(type_kind="String")
            elif isinstance(expr.value, bool):
                return Type(type_kind="Bool")

        elif isinstance(expr, Variable):
            if expr.name not in self.env:
                raise undefined_variable(expr.name)
            return self.env[expr.name]

        elif isinstance(expr, BinaryOp):
            left_type = self.infer(expr.left)
            right_type = self.infer(expr.right)

            # Dimensional analysis (simplified)
            if expr.operator in {'+', '-'}:
                if not self.types_compatible(left_type, right_type):
                    raise dimensional_mismatch(expr.operator, str(left_type), str(right_type))
                return left_type
            elif expr.operator == '*':
                return self.multiply_dimensions(left_type, right_type)
            elif expr.operator == '/':
                return self.divide_dimensions(left_type, right_type)

        return Type(type_kind="Unknown")

    def check_expr(self, expr: Expression, expected_type: Type):
        """Check expression against expected type (checking)."""
        inferred = self.infer(expr)
        if not self.types_compatible(inferred, expected_type):
            raise type_mismatch(str(expected_type), str(inferred))

    def types_compatible(self, t1: Type, t2: Type) -> bool:
        """Check if types are compatible (stub)."""
        return t1.type_kind == t2.type_kind

    def multiply_dimensions(self, t1: Type, t2: Type) -> Type:
        """Multiply dimensions (stub)."""
        return Type(type_kind=f"{t1.type_kind}*{t2.type_kind}")

    def divide_dimensions(self, t1: Type, t2: Type) -> Type:
        """Divide dimensions (stub)."""
        return Type(type_kind=f"{t1.type_kind}/{t2.type_kind}")
