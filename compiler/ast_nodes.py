# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""
PEL Abstract Syntax Tree (AST) Node Definitions
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class NodeType(Enum):
    """AST node types."""
    MODEL = "model"
    PARAM = "param"
    VAR = "var"
    FUNC = "func"
    CONSTRAINT = "constraint"
    POLICY = "policy"


@dataclass
class ASTNode:
    """Base class for all AST nodes."""
    line: int = field(default=0, kw_only=True)
    column: int = field(default=0, kw_only=True)


@dataclass
class TypeAnnotation(ASTNode):
    """Type annotation."""
    type_kind: str  # Currency, Rate, Duration, etc.
    params: dict[str, Any] = field(default_factory=dict)  # e.g., {"currency_code": "USD"}


@dataclass
class Expression(ASTNode):
    """Base class for expressions."""
    pass


@dataclass
class Statement(ASTNode):
    """Base class for statements (used in blocks and top-level model body)."""
    pass


@dataclass
class Literal(Expression):
    """Literal value."""
    value: Any
    literal_type: str | None = None


@dataclass
class Variable(Expression):
    """Variable reference."""
    name: str


@dataclass
class BinaryOp(Expression):
    """Binary operation (e.g., a + b)."""
    operator: str
    left: Expression
    right: Expression


@dataclass
class UnaryOp(Expression):
    """Unary operation (e.g., -x)."""
    operator: str
    operand: Expression


@dataclass
class FunctionCall(Expression):
    """Function call."""
    function_name: str
    arguments: list[Expression]


@dataclass
class Indexing(Expression):
    """Array/TimeSeries indexing (e.g., revenue[t])."""
    expression: Expression  # Changed from 'base' to match parser
    index: Expression


@dataclass
class ArrayLiteral(Expression):
    """Array literal expression [1, 2, 3]."""
    elements: list[Expression]


@dataclass
class Lambda(Expression):
    """Lambda expression (x: T) -> expr."""
    params: list[tuple]  # [(name, type), ...]
    body: Expression


@dataclass
class MemberAccess(Expression):
    """Member access expression (e.g., obj.field)."""
    expression: Expression
    member: str


@dataclass
class IfThenElse(Expression):
    """Conditional expression."""
    condition: Expression
    then_expr: Expression  # Changed from 'then_branch'
    else_expr: Expression  # Changed from 'else_branch'


@dataclass
class PerDurationExpression(Expression):
    """Expression for per-duration operations (e.g., $500 / 1mo)."""
    left: Expression
    duration: str


@dataclass
class Distribution(Expression):
    """Distribution expression (e.g., ~Normal(μ=0, σ=1))."""
    dist_type: str  # Changed from 'distribution_type' to match parser
    params: dict[str, Expression]  # Changed from 'parameters'


@dataclass
class Assignment(Statement):
    """Assignment statement (e.g., x = expr, ts[t] = expr)."""
    target: Expression
    value: Expression


@dataclass
class Return(Statement):
    """Return statement inside a block expression."""
    value: Expression | None = None


@dataclass
class IfStmt(Statement):
    """If statement with a block body (if cond { ... } else { ... })."""
    condition: Expression
    then_body: list[Statement] = field(default_factory=list)
    else_body: list[Statement] | None = None


@dataclass
class ForStmt(Statement):
    """For loop statement (for t in start..end { ... })."""
    var_name: str
    start: Expression
    end: Expression
    body: list[Statement] = field(default_factory=list)


@dataclass
class BlockExpr(Expression):
    """Block expression (e.g., { ... return expr })."""
    statements: list[Statement] = field(default_factory=list)


@dataclass
class Provenance(ASTNode):
    """Provenance metadata block."""
    source: str
    method: str
    confidence: float
    freshness: str | None = None
    owner: str | None = None
    correlated_with: list[tuple] = field(default_factory=list)  # [(var_name, coef), ...]
    notes: str | None = None


@dataclass
class ParamDecl(ASTNode):
    """Parameter declaration."""
    name: str
    type_annotation: TypeAnnotation
    value: Expression
    provenance: dict[str, Any] | None = None


@dataclass
class VarDecl(Statement):
    """Variable declaration."""
    name: str
    type_annotation: TypeAnnotation | None  # Can be inferred
    value: Expression | None = None
    is_mutable: bool = False


@dataclass
class FuncDecl(ASTNode):
    """Function declaration."""
    name: str
    parameters: list[tuple]  # [(name, type), ...]
    return_type: TypeAnnotation
    body: list[Statement]  # Function bodies contain statements (var, return, etc.)


@dataclass
class Scope:
    """Constraint/policy scope."""
    temporal: dict[str, Any] | None = None  # {"type": "all"} or {"type": "range", "start": 0, "end": 12}
    entity: dict[str, Any] | None = None


@dataclass
class Constraint(ASTNode):
    """Constraint declaration."""
    name: str
    condition: Expression
    severity: str  # "fatal" or "warning"
    message: str | None = None
    scope: Scope | None = None
    slack_variable: str | None = None


@dataclass
class Trigger(ASTNode):
    """Policy trigger."""
    trigger_type: str  # "time", "threshold", "event", "composite"
    condition: Expression


@dataclass
class Action(ASTNode):
    """Policy action."""
    action_type: str  # "assign", "multiply", "add", etc.
    target: str | None = None  # Variable name
    value: Expression | None = None
    statements: list['Action'] | None = None  # For block actions
    event_name: str | None = None  # For emit_event
    args: dict[str, Expression] = field(default_factory=dict)


@dataclass
class Policy(ASTNode):
    """Policy declaration."""
    name: str
    trigger: Trigger
    action: Action


@dataclass
class Model(ASTNode):
    """Top-level model."""
    name: str
    time_horizon: int | None = None
    time_unit: str = "Month"
    params: list[ParamDecl] = field(default_factory=list)
    vars: list[VarDecl] = field(default_factory=list)
    funcs: list[FuncDecl] = field(default_factory=list)
    constraints: list[Constraint] = field(default_factory=list)
    policies: list[Policy] = field(default_factory=list)
    statements: list[Statement] = field(default_factory=list)


# === Typed AST (after type checking) ===

@dataclass
class TypedExpression(Expression):
    """Expression with inferred type."""
    expr: Expression  # Original expression
    inferred_type: TypeAnnotation


@dataclass
class TypedModel(Model):
    """Model with all expressions typed."""
    # Same structure as Model, but all Expression nodes wrapped in TypedExpression
    pass
