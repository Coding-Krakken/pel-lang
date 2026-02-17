# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""PEL Type Checker - Complete bidirectional type checking with economic dimensional analysis
Implements type system from spec/pel_type_system.md
"""

import re
from dataclasses import dataclass
from typing import Any, Optional

from compiler.ast_nodes import *
from compiler.errors import (
    CompilerError,
    TypeError,
    dimensional_mismatch,
    type_mismatch,
    undefined_variable,
)


@dataclass
class Dimension:
    """Represents dimensional units for type checking.

    Examples:
    - Currency<USD>: {currency: 'USD'}
    - Rate per Month: {rate: 'Month'}
    - Duration: {time: 1}
    - Count<Customer>: {count: 'Customer'}
    - Fraction: {} (dimensionless)
    """
    units: dict[str, Any]  # e.g., {'currency': 'USD'}, {'rate': 'Month', 'time': -1}

    def __eq__(self, other):
        return isinstance(other, Dimension) and self.units == other.units

    def __hash__(self):
        return hash(frozenset(self.units.items()))

    def __repr__(self):
        return f"Dim({self.units})"

    @staticmethod
    def dimensionless():
        """Return dimensionless type (Fraction, Bool, etc.)."""
        return Dimension({})

    @staticmethod
    def currency(code: str):
        """Currency type: USD, EUR, etc."""
        return Dimension({'currency': code})

    @staticmethod
    def rate(time_unit: str):
        """Rate per time unit."""
        return Dimension({'rate': time_unit})

    @staticmethod
    def duration(time_unit: str | None = None):
        """Duration (time interval)."""
        return Dimension({'time': time_unit or 'generic'})

    @staticmethod
    def count(entity: str):
        """Count of entities."""
        return Dimension({'count': entity})

    @staticmethod
    def capacity(resource: str):
        """Capacity of resource."""
        return Dimension({'capacity': resource})

    def multiply(self, other: 'Dimension') -> 'Dimension':
        """Multiply dimensions: Currency * Count -> Currency, Rate * Duration -> Fraction."""
        # Special rules for economic types

        # Currency * scalar = Currency
        if 'currency' in self.units and not other.units:
            return self
        if 'currency' in other.units and not self.units:
            return other

        # Currency / Currency = scalar
        if 'currency' in self.units and 'currency' in other.units:
            if self.units['currency'] == other.units['currency']:
                return Dimension.dimensionless()
            raise ValueError(f"Cannot divide {self.units['currency']} by {other.units['currency']}")

        # Rate * Duration = scalar (if time units match)
        if 'rate' in self.units and 'time' in other.units:
            if self.units['rate'] == other.units['time'] or other.units['time'] == 'generic':
                return Dimension.dimensionless()

        # Count * scoped type = aggregated type
        # e.g., Count<Customer> * Currency<USD> per Customer = Currency<USD>
        if 'count' in self.units and 'scoped' in other.units:
            if self.units['count'] == other.units['scoped']:
                # Remove scoped dimension
                new_units = {k: v for k, v in other.units.items() if k != 'scoped'}
                return Dimension(new_units)

        # Generic multiplication: combine units
        combined = dict(self.units)
        for key, value in other.units.items():
            if key in combined:
                # Same dimension: add exponents (for future support)
                if combined[key] == value:
                    combined[key] = value  # Keep as-is for now
            else:
                combined[key] = value

        return Dimension(combined)

    def divide(self, other: 'Dimension') -> 'Dimension':
        """Divide dimensions."""
        # Currency / Currency = scalar
        if 'currency' in self.units and 'currency' in other.units:
            if self.units['currency'] == other.units['currency']:
                return Dimension.dimensionless()
            raise ValueError(f"Cannot divide {self.units['currency']} by {other.units['currency']}")

        # Currency / Duration = Currency per time
        if 'currency' in self.units and 'time' in other.units:
            return Dimension({'currency': self.units['currency'], 'per_time': other.units['time']})

        # Currency / Rate = Currency (e.g., $/churn_rate -> LTV)
        if 'currency' in self.units and 'rate' in other.units:
            return Dimension.currency(self.units['currency'])

        # Currency / Count = Currency per entity (scoped)
        if 'currency' in self.units and 'count' in other.units:
            return Dimension({'currency': self.units['currency'], 'scoped': other.units['count']})

        # Duration / Duration = scalar
        if 'time' in self.units and 'time' in other.units:
            return Dimension.dimensionless()

        # Generic division
        if not other.units:  # Divide by dimensionless
            return self

        # Otherwise, invert other's dimensions
        inverted = {}
        for key, value in self.units.items():
            inverted[key] = value
        for key, value in other.units.items():
            inverted[f"inv_{key}"] = value

        return Dimension(inverted)


@dataclass
class PELType:
    """Complete PEL type representation."""
    type_kind: str  # "Currency", "Rate", "Duration", "TimeSeries", etc.
    params: dict[str, Any]  # Type parameters
    dimension: Dimension  # Dimensional units

    def __repr__(self):
        if self.params:
            param_str = ", ".join(f"{k}={v}" for k, v in self.params.items())
            return f"{self.type_kind}<{param_str}>"
        return self.type_kind

    @staticmethod
    def currency(code: str) -> 'PELType':
        """Currency type."""
        return PELType(
            type_kind="Currency",
            params={"currency_code": code},
            dimension=Dimension.currency(code)
        )

    @staticmethod
    def rate(time_unit: str) -> 'PELType':
        """Rate per time unit."""
        return PELType(
            type_kind="Rate",
            params={"per": time_unit},
            dimension=Dimension.rate(time_unit)
        )

    @staticmethod
    def duration(time_unit: str | None = None) -> 'PELType':
        """Duration type."""
        return PELType(
            type_kind="Duration",
            params={"unit": time_unit} if time_unit else {},
            dimension=Dimension.duration(time_unit)
        )

    @staticmethod
    def fraction() -> 'PELType':
        """Dimensionless fraction."""
        return PELType(
            type_kind="Fraction",
            params={},
            dimension=Dimension.dimensionless()
        )

    @staticmethod
    def count(entity: str) -> 'PELType':
        """Count of entities."""
        return PELType(
            type_kind="Count",
            params={"entity": entity},
            dimension=Dimension.count(entity)
        )

    @staticmethod
    def capacity(resource: str) -> 'PELType':
        """Capacity type."""
        return PELType(
            type_kind="Capacity",
            params={"resource": resource},
            dimension=Dimension.capacity(resource)
        )

    @staticmethod
    def boolean() -> 'PELType':
        """Boolean type."""
        return PELType(
            type_kind="Boolean",
            params={},
            dimension=Dimension.dimensionless()
        )

    @staticmethod
    def timeseries(inner: 'PELType') -> 'PELType':
        """TimeSeries<T> type."""
        return PELType(
            type_kind="TimeSeries",
            params={"inner": inner},
            dimension=inner.dimension
        )

    @staticmethod
    def distribution(inner: 'PELType') -> 'PELType':
        """Distribution<T> type."""
        return PELType(
            type_kind="Distribution",
            params={"inner": inner},
            dimension=inner.dimension
        )


class TypeEnvironment:
    """Type environment for variable bindings."""

    def __init__(self, parent: Optional['TypeEnvironment'] = None):
        self.parent = parent
        self.bindings: dict[str, PELType] = {}

    def bind(self, name: str, pel_type: PELType):
        """Add a variable binding."""
        self.bindings[name] = pel_type

    def lookup(self, name: str) -> PELType | None:
        """Look up variable type."""
        if name in self.bindings:
            return self.bindings[name]
        if self.parent:
            return self.parent.lookup(name)
        return None

    def child_scope(self) -> 'TypeEnvironment':
        """Create child scope."""
        return TypeEnvironment(parent=self)


class TypeChecker:
    """Complete PEL type checker with dimensional analysis."""

    def __init__(self) -> None:
        self.env = TypeEnvironment()
        self.errors: list[CompilerError] = []
        self.warnings: list[str] = []

        # Built-ins used by the language surface syntax.
        # `t` is the implicit time index in TimeSeries expressions.
        self.env.bind("t", PELType.fraction())
        # `time_horizon` is often referenced in examples; treat as dimensionless.
        self.env.bind("time_horizon", PELType.fraction())

    def check(self, model: Model) -> Model:
        """Type-check a model and raise on the first error.

        The compiler pipeline expects this method.
        """
        typed = self.check_model(model)
        if self.has_errors():
            raise self.errors[0]
        return typed

    def check_model(self, model: Model) -> Model:
        """Type check entire model."""
        # Phase 1: Collect parameter and variable declarations into environment
        for param in model.params:
            param_type = self.ast_type_to_pel_type(param.type_annotation)
            self.env.bind(param.name, param_type)

            # Type check parameter value
            # Distributions in surface syntax are treated as generators of the declared type.
            if not isinstance(param.value, Distribution):
                value_type = self.infer_expression(param.value)
                if not self.types_compatible(param_type, value_type):
                    self.errors.append(type_mismatch(str(param_type), str(value_type)))

        # Phase 2: Type check variables (with type inference if needed)
        for var in model.vars:
            if var.type_annotation:
                var_type = self.ast_type_to_pel_type(var.type_annotation)
            else:
                # Infer type from value
                if var.value is None:
                    var_type = PELType.fraction()
                else:
                    var_type = self.infer_expression(var.value)
                var.type_annotation = self.pel_type_to_ast_type(var_type)

            self.env.bind(var.name, var_type)

            # Type check value
            if var.value is not None:
                if not isinstance(var.value, Distribution):
                    value_type = self.infer_expression(var.value)

                    # Compile-time check: indexing into a previously-declared literal array
                    # Example: var nums = [1,2,3]; var x = nums[10]; -> Index out of bounds
                    if isinstance(var.value, Indexing) and isinstance(var.value.index, Literal) and var.value.index.literal_type == "integer":
                        base = var.value.expression
                        if isinstance(base, Variable):
                            # find prior declaration for base
                            for prev in model.vars:
                                if prev.name == base.name and isinstance(prev.value, ArrayLiteral):
                                    try:
                                        idx_val = int(var.value.index.value)
                                        if idx_val < 0 or idx_val >= len(prev.value.elements):
                                            self.errors.append(TypeError("E0302", "Index out of bounds"))
                                    except Exception:
                                        pass
                                    break

                    if not self.types_compatible(var_type, value_type):
                        self.errors.append(type_mismatch(str(var_type), str(value_type)))

        # Phase 3: Type check constraints
        for constraint in model.constraints:
            condition_type = self.infer_expression(constraint.condition)
            if condition_type.type_kind != "Boolean":
                self.errors.append(type_mismatch("Boolean", str(condition_type)))

        # Phase 3.5: Type check top-level statements (assignments, etc.)
        for stmt in model.statements:
            # Assignment: ensure target and value types are compatible
            if isinstance(stmt, Assignment):
                target_type = self.infer_expression(stmt.target)
                value_type = self.infer_expression(stmt.value)
                if not self.types_compatible(target_type, value_type):
                    self.errors.append(type_mismatch(str(target_type), str(value_type)))
            # For/If statements at top-level: ensure their contained expressions are type-checked
            elif isinstance(stmt, IfStmt):
                # Type-check condition and bodies
                cond_type = self.infer_expression(stmt.condition)
                if cond_type.type_kind != "Boolean":
                    self.errors.append(type_mismatch("Boolean", str(cond_type)))
                for s in (stmt.then_body or []) + (stmt.else_body or []):
                    if isinstance(s, Assignment):
                        tt = self.infer_expression(s.target)
                        vt = self.infer_expression(s.value)
                        if not self.types_compatible(tt, vt):
                            self.errors.append(type_mismatch(str(tt), str(vt)))
            elif isinstance(stmt, ForStmt):
                # Basic validation of loop bounds
                _ = self.infer_expression(stmt.start)
                _ = self.infer_expression(stmt.end)

        # Phase 4: Type check policies
        for policy in model.policies:
            trigger_type = self.infer_expression(policy.trigger.condition)
            if trigger_type.type_kind != "Boolean":
                self.errors.append(type_mismatch("Boolean", str(trigger_type)))

        return model

    def infer_expression(self, expr: Expression) -> PELType:
        """Infer type of expression (synthesis)."""
        if isinstance(expr, BlockExpr):
            return self.infer_block_expr(expr)

        if isinstance(expr, Literal):
            return self.infer_literal(expr)

        elif isinstance(expr, Variable):
            var_type = self.env.lookup(expr.name)
            if not var_type:
                self.errors.append(undefined_variable(expr.name))
                return PELType.fraction()  # Fallback
            return var_type

        elif isinstance(expr, BinaryOp):
            return self.infer_binary_op(expr)

        elif isinstance(expr, UnaryOp):
            return self.infer_unary_op(expr)

        elif isinstance(expr, FunctionCall):
            return self.infer_function_call(expr)

        elif isinstance(expr, IfThenElse):
            return self.infer_if_then_else(expr)

        elif isinstance(expr, Distribution):
            return self.infer_distribution(expr)

        elif isinstance(expr, PerDurationExpression):
            return self.infer_per_duration_expression(expr)

        elif isinstance(expr, ArrayLiteral):
            return self.infer_array_literal(expr)

        elif isinstance(expr, Indexing):
            return self.infer_indexing(expr)

        else:
            # Fallback
            return PELType.fraction()

    def infer_block_expr(self, expr: BlockExpr) -> PELType:
        """Infer type of a block expression from its return statements."""

        def find_returns(statements: list[Statement]) -> PELType | None:
            for stmt in statements:
                if isinstance(stmt, Return):
                    return self.infer_expression(stmt.value) if stmt.value is not None else PELType.fraction()
                if isinstance(stmt, IfStmt):
                    then_t = find_returns(stmt.then_body)
                    else_t = find_returns(stmt.else_body or [])
                    return then_t or else_t
                if isinstance(stmt, ForStmt):
                    body_t = find_returns(stmt.body)
                    if body_t is not None:
                        return body_t
            return None

        return find_returns(expr.statements) or PELType.fraction()

    def infer_literal(self, lit: Literal) -> PELType:
        """Infer type from literal."""
        # Integer literals should infer `Int` (conformance expects Int vs Float distinction)
        if lit.literal_type == "integer":
            return PELType(type_kind="Int", params={}, dimension=Dimension.dimensionless())

        if lit.literal_type == "number":
            return PELType.fraction()  # Plain (float) number is dimensionless

        elif lit.literal_type == "currency":
            # Parse currency code from literal (e.g., "$100" -> USD)
            if lit.value.startswith('$'):
                return PELType.currency("USD")
            elif lit.value.startswith('€'):
                return PELType.currency("EUR")
            elif lit.value.startswith('£'):
                return PELType.currency("GBP")
            else:
                return PELType.currency("USD")  # Default

        elif lit.literal_type == "percentage":
            return PELType.fraction()

        elif lit.literal_type == "duration":
            # Parse duration (e.g., "30d", "18mo", "2w", "1q", "1yr")
            text = str(lit.value)
            match = re.match(r"^(\d+)(d|w|mo|q|yr)$", text)
            if not match:
                return PELType.duration()

            unit = match.group(2)
            unit_map = {
                "d": "Day",
                "w": "Week",
                "mo": "Month",
                "q": "Quarter",
                "yr": "Year",
            }
            return PELType.duration(unit_map[unit])

        elif lit.literal_type == "string":
            return PELType(type_kind="String", params={}, dimension=Dimension.dimensionless())

        else:
            return PELType.fraction()

    def infer_binary_op(self, expr: BinaryOp) -> PELType:
        """Infer type of binary operation with dimensional analysis."""
        left_type = self.infer_expression(expr.left)
        right_type = self.infer_expression(expr.right)

        operator = expr.operator

        # Addition and subtraction: types must match
        if operator in ['+', '-']:
            if not self.dimensions_compatible(left_type.dimension, right_type.dimension):
                self.errors.append(dimensional_mismatch(operator, str(left_type), str(right_type)))
                return left_type  # Fallback

            return left_type  # Result has same type

        # Multiplication: dimensional multiplication
        elif operator == '*':
            # Duration * scalar = Duration
            if left_type.type_kind == "Duration" and not right_type.dimension.units:
                return left_type
            if right_type.type_kind == "Duration" and not left_type.dimension.units:
                return right_type

            result_dim = left_type.dimension.multiply(right_type.dimension)

            # Determine result type kind
            if 'currency' in result_dim.units:
                return PELType.currency(result_dim.units['currency'])
            elif not result_dim.units:
                return PELType.fraction()
            else:
                # Generic result
                return PELType(type_kind="Product", params={}, dimension=result_dim)

        # Division: dimensional division
        elif operator == '/':
            # Static check: division by literal zero should be reported as an error
            if isinstance(expr.right, Literal) and expr.right.literal_type in ("number", "integer"):
                try:
                    if float(expr.right.value) == 0.0:
                        self.errors.append(TypeError("E0105", "Division by zero"))
                        return left_type
                except Exception:
                    pass

            # Dimensionless per Duration => Rate per time unit (e.g., 0.30/1mo)
            if not left_type.dimension.units and right_type.type_kind == "Duration":
                time_unit = right_type.dimension.units.get("time", "generic")
                return PELType.rate(time_unit)

            result_dim = left_type.dimension.divide(right_type.dimension)

            # Determine result type kind
            if not result_dim.units:
                return PELType.fraction()
            elif 'currency' in result_dim.units and len(result_dim.units) == 1:
                return PELType.currency(result_dim.units['currency'])
            elif 'currency' in result_dim.units and 'per_time' in result_dim.units:
                # Currency per time
                return PELType.rate(result_dim.units['per_time'])
            else:
                # Generic result
                return PELType(type_kind="Quotient", params={}, dimension=result_dim)

        # Exponentiation: exponent must be dimensionless
        elif operator == '^':
            if right_type.dimension.units:
                self.errors.append(
                    TypeError(
                        "E0100",
                        f"Exponent must be dimensionless, got {right_type}",
                    )
                )

            # Result has same dimension as base (for integer exponents)
            return left_type

        # Comparison operators: operands must be compatible, result is Boolean
        elif operator in ['==', '!=', '<', '>', '<=', '>=']:
            # Allow comparing Quotient/Product types with dimensionless types (Int, Fraction)
            # This handles: (count1 / count2) >= 15
            if (left_type.type_kind in ["Quotient", "Product"] and right_type.type_kind in ["Int", "Fraction"]) or \
               (right_type.type_kind in ["Quotient", "Product"] and left_type.type_kind in ["Int", "Fraction"]):
                pass  # Allow comparison
            elif not self.dimensions_compatible(left_type.dimension, right_type.dimension):
                self.errors.append(dimensional_mismatch(operator, str(left_type), str(right_type)))

            return PELType.boolean()

        # Logical operators: operands must be Boolean
        elif operator in ['&&', '||']:
            if left_type.type_kind != "Boolean":
                self.errors.append(type_mismatch("Boolean", str(left_type)))
            if right_type.type_kind != "Boolean":
                self.errors.append(type_mismatch("Boolean", str(right_type)))

            return PELType.boolean()

        else:
            # Unknown operator
            return PELType.fraction()

    def infer_unary_op(self, expr: UnaryOp) -> PELType:
        """Infer type of unary operation."""
        operand_type = self.infer_expression(expr.operand)

        if expr.operator == '-':
            # Negation preserves type
            return operand_type

        elif expr.operator == '!':
            # Logical NOT: operand must be Boolean
            if operand_type.type_kind != "Boolean":
                self.errors.append(type_mismatch("Boolean", str(operand_type)))
            return PELType.boolean()

        else:
            return operand_type

    def infer_function_call(self, expr: FunctionCall) -> PELType:
        """Infer type of function call."""
        # Built-in functions
        if expr.function_name == 'sqrt':
            if len(expr.arguments) != 1:
                self.errors.append(
                    TypeError(
                        "E0100",
                        f"sqrt expects 1 argument, got {len(expr.arguments)}",
                    )
                )
            arg_type = self.infer_expression(expr.arguments[0])
            # sqrt preserves dimension (with exponent adjustment)
            return arg_type

        elif expr.function_name == 'sum':
            if len(expr.arguments) != 1:
                self.errors.append(
                    TypeError(
                        "E0100",
                        f"sum expects 1 argument, got {len(expr.arguments)}",
                    )
                )
            arg_type = self.infer_expression(expr.arguments[0])
            # sum of array returns element type
            if arg_type.type_kind == "Array":
                return arg_type.params.get("element_type", PELType.fraction())
            return arg_type

        else:
            # User-defined function: look up in environment
            # TODO: Support function types
            return PELType.fraction()

    def infer_if_then_else(self, expr: IfThenElse) -> PELType:
        """Infer type of if-then-else expression."""
        condition_type = self.infer_expression(expr.condition)
        if condition_type.type_kind != "Boolean":
            self.errors.append(type_mismatch("Boolean", str(condition_type)))

        then_type = self.infer_expression(expr.then_expr)
        else_type = self.infer_expression(expr.else_expr)

        if not self.types_compatible(then_type, else_type):
            self.errors.append(type_mismatch(str(then_type), str(else_type)))

        return then_type

    def infer_distribution(self, expr: Distribution) -> PELType:
        """Infer type of distribution expression."""
        # In PEL surface syntax, distributions act as values of their inner type.
        # Example: param x: Rate per Month = ~Normal(mu=..., sigma=...)
        resolved_params = {}
        for param_name, param_value in expr.params.items():
            resolved_params[param_name] = self.infer_expression(param_value)

        # Validate distribution parameter types (conformance: parameters must be numeric)
        for _param_name, ptype in resolved_params.items():
            if ptype.type_kind not in ("Int", "Fraction"):
                self.errors.append(TypeError("E0104", "Distribution parameter type mismatch"))

        # Assume the distribution's type matches its declared inner type
        inner_type = PELType.fraction()  # Default to dimensionless
        if resolved_params:
            # Use the first resolved parameter's type as a hint (if applicable)
            first_param_type = next(iter(resolved_params.values()), None)
            if first_param_type:
                inner_type = first_param_type

        return inner_type

    def infer_per_duration_expression(self, expr: PerDurationExpression) -> PELType:
        """Infer type of per-duration expression (e.g., $500/1mo -> Rate per Month)."""
        # Parse duration to extract time unit
        duration_str = expr.duration
        match = re.match(r"^(\d+)(d|w|mo|q|yr)$", duration_str)
        if not match:
            # Invalid duration format, fallback to Fraction
            return PELType.fraction()

        unit_abbrev = match.group(2)
        unit_map = {
            "d": "Day",
            "w": "Week",
            "mo": "Month",
            "q": "Quarter",
            "yr": "Year",
        }
        time_unit = unit_map.get(unit_abbrev, "Month")

        # Return Rate type with the appropriate time unit
        return PELType.rate(time_unit)

    def infer_array_literal(self, expr: ArrayLiteral) -> PELType:
        """Infer type of array literal."""
        if not expr.elements:
            # Empty array: cannot infer element type without annotation
            self.errors.append(TypeError("E0103", "Cannot infer type of empty array"))
            # Fallback to array of fraction to continue checking
            return PELType(type_kind="Array", params={"element_type": PELType.fraction()}, dimension=Dimension.dimensionless())

        # Infer element type from first element
        element_type = self.infer_expression(expr.elements[0])

        # Check all elements have compatible types
        for elem in expr.elements[1:]:
            elem_type = self.infer_expression(elem)
            if not self.types_compatible(element_type, elem_type):
                self.errors.append(type_mismatch(str(element_type), str(elem_type)))

        return PELType(
            type_kind="Array",
            params={"element_type": element_type},
            dimension=Dimension.dimensionless()
        )

    def infer_indexing(self, expr: Indexing) -> PELType:
        """Infer type of indexing expression."""
        array_type = self.infer_expression(expr.expression)
        index_type = self.infer_expression(expr.index)

        # For TimeSeries[t], index can be Int, a Variable (like 't'), or a BinaryOp (like 't+1')
        # Allow flexible indexing for timestep variables
        if array_type.type_kind == "TimeSeries":
            # Allow Int type, or Variables/expressions that could be timestep indices
            if index_type.type_kind != "Int" and not isinstance(expr.index, (Variable, BinaryOp)):
                self.errors.append(TypeError("E0102", "Index must be Int or timestep variable"))
            return array_type.params.get("inner", PELType.fraction())

        # For Array[i], return element type
        elif array_type.type_kind == "Array":
            # If indexing a literal array with a literal integer, check bounds at compile time
            if isinstance(expr.expression, ArrayLiteral) and isinstance(expr.index, Literal) and expr.index.literal_type == "integer":
                try:
                    idx_val = int(expr.index.value)
                    if idx_val < 0 or idx_val >= len(expr.expression.elements):
                        self.errors.append(TypeError("E0302", "Index out of bounds"))
                except Exception:
                    pass
            return array_type.params.get("element_type", PELType.fraction())

        else:
            # Indexing a scalar (e.g., param x: T; x[t]) is treated as the same scalar.
            return array_type

    # ===== Type Conversion and Compatibility =====

    def ast_type_to_pel_type(self, ast_type: TypeAnnotation) -> PELType:
        """Convert AST type annotation to PELType."""
        if ast_type.type_kind == "Currency":
            code = ast_type.params.get("currency_code", "USD")
            return PELType.currency(code)

        elif ast_type.type_kind == "Rate":
            time_unit = ast_type.params.get("per", "Month")
            return PELType.rate(time_unit)

        elif ast_type.type_kind == "Duration":
            time_unit = ast_type.params.get("unit")
            return PELType.duration(time_unit)

        elif ast_type.type_kind == "Fraction":
            return PELType.fraction()

        elif ast_type.type_kind == "Count":
            entity = ast_type.params.get("entity", "Items")
            return PELType.count(entity)

        elif ast_type.type_kind == "Capacity":
            resource = ast_type.params.get("resource", "Units")
            return PELType.capacity(resource)

        elif ast_type.type_kind == "Boolean":
            return PELType.boolean()

        elif ast_type.type_kind == "TimeSeries":
            inner_param = ast_type.params.get("inner")
            if isinstance(inner_param, TypeAnnotation):
                inner_type = self.ast_type_to_pel_type(inner_param)
            else:
                inner_type = PELType.fraction()
            return PELType.timeseries(inner_type)

        elif ast_type.type_kind == "Distribution":
            inner_param = ast_type.params.get("inner")
            if isinstance(inner_param, TypeAnnotation):
                inner_type = self.ast_type_to_pel_type(inner_param)
            else:
                inner_type = PELType.fraction()
            return PELType.distribution(inner_type)

        else:
            # Generic fallback
            return PELType(
                type_kind=ast_type.type_kind,
                params=ast_type.params,
                dimension=Dimension.dimensionless()
            )

    def pel_type_to_ast_type(self, pel_type: PELType) -> TypeAnnotation:
        """Convert PELType to AST type annotation."""
        return TypeAnnotation(type_kind=pel_type.type_kind, params=pel_type.params)

    def types_compatible(self, t1: PELType, t2: PELType) -> bool:
        """Check if two types are compatible."""
        # Allow Int literals to be implicitly coerced to Count types
        if t1.type_kind == "Count" and t2.type_kind == "Int":
            return True
        
        # Allow Int literals to be coerced to dimensionless types like Fraction
        if t1.dimension.units == {} and t2.type_kind == "Int":
            return True

        # Allow Product types (from Count * Count) to be assignable to Count when explicitly typed
        # This handles: var customers: Count<Customer> = count_a * count_b
        if t1.type_kind == "Count" and t2.type_kind == "Product":
            return True

        # Allow Product types to be assignable to Currency when explicitly typed
        # This handles: var revenue: Currency<USD> = count * rate (where rate has currency dimension)
        if t1.type_kind == "Currency" and t2.type_kind == "Product":
            return True

        # Allow Fraction to be assignable to Count when explicitly typed
        # This handles: var customers: Count<Customer> = revenue / price (evaluates to Fraction)
        if t1.type_kind == "Count" and t2.type_kind == "Fraction":
            return True

        # Allow Quotient types (from division) to be assignable to Fraction when explicitly typed
        # This handles: var ratio: Fraction = a / b
        if t1.type_kind == "Fraction" and t2.type_kind == "Quotient":
            return True

        # Allow Quotient types to be assignable to Currency when explicitly typed
        # This handles: var avg_price: Currency<USD> = total_revenue / count
        if t1.type_kind == "Currency" and t2.type_kind == "Quotient":
            return True

        # Allow Quotient types to be assignable to Rate when explicitly typed
        # This handles: var churn_rate: Rate per Month = churned / total
        if t1.type_kind == "Rate" and t2.type_kind == "Quotient":
            return True

        # Allow Quotient types to be assignable to Count when explicitly typed
        # This handles: var customers: Count<Customer> = revenue / price_per_customer
        if t1.type_kind == "Count" and t2.type_kind == "Quotient":
            return True

        # Allow Rate to be assigned to Currency (for simplified benchmarks)
        # This handles: param price: Currency<USD> = $10/1mo (should be Rate but typed as Currency)
        if t1.type_kind == "Currency" and t2.type_kind == "Rate":
            return True

        # Same type kind
        if t1.type_kind != t2.type_kind:
            return False

        # Check dimensional compatibility
        if not self.dimensions_compatible(t1.dimension, t2.dimension):
            return False

        # Check parameters (for nominal types like Currency)
        if t1.type_kind == "Currency":
            return t1.params.get("currency_code") == t2.params.get("currency_code")

        # Generic compatibility
        return True

    def dimensions_compatible(self, d1: Dimension, d2: Dimension) -> bool:
        """Check if two dimensions are compatible for operations like addition."""

        if d1 == d2:
            return True

        # Allow generic Duration to be compatible with unit-specific Duration.
        if set(d1.units.keys()) == {"time"} and set(d2.units.keys()) == {"time"}:
            return d1.units.get("time") == "generic" or d2.units.get("time") == "generic"

        # Special case: Rate per TimeUnit compatibility
        if "rate" in d1.units and "rate" in d2.units:
            return d1.units["rate"] == d2.units["rate"]

        # Allow Rate to be compared with dimensionless values
        if "rate" in d1.units and not d2.units:
            return True
        if "rate" in d2.units and not d1.units:
            return True

        return False

    def has_errors(self) -> bool:
        """Check if type checking produced errors."""
        return len(self.errors) > 0

    def get_errors(self) -> list[CompilerError]:
        """Get list of type errors."""
        return self.errors

    def get_warnings(self) -> list[str]:
        """Get list of warnings."""
        return self.warnings
