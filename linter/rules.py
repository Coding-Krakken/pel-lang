# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""Built-in lint rules for PEL."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from compiler.ast_nodes import (
    ArrayLiteral,
    Assignment,
    BinaryOp,
    BlockExpr,
    Distribution,
    Expression,
    ForStmt,
    FunctionCall,
    IfStmt,
    IfThenElse,
    Indexing,
    Lambda,
    Literal,
    MemberAccess,
    Model,
    PerDurationExpression,
    Return,
    Statement,
    UnaryOp,
    VarDecl,
    Variable,
)
from compiler.typechecker import TypeChecker
from linter.types import LintContext, LintViolation


@dataclass
class LintRule:
    code: str
    description: str
    default_severity: str = "warning"

    def run(self, context: LintContext) -> list[LintViolation]:
        raise NotImplementedError


def _collect_expression_uses(expr: Expression, uses: set[str], bound: set[str]) -> None:
    if isinstance(expr, Variable):
        if expr.name not in bound:
            uses.add(expr.name)
        return
    if isinstance(expr, Literal):
        return
    if isinstance(expr, BinaryOp):
        _collect_expression_uses(expr.left, uses, bound)
        _collect_expression_uses(expr.right, uses, bound)
        return
    if isinstance(expr, UnaryOp):
        _collect_expression_uses(expr.operand, uses, bound)
        return
    if isinstance(expr, FunctionCall):
        for arg in expr.arguments:
            _collect_expression_uses(arg, uses, bound)
        return
    if isinstance(expr, Indexing):
        _collect_expression_uses(expr.expression, uses, bound)
        _collect_expression_uses(expr.index, uses, bound)
        return
    if isinstance(expr, ArrayLiteral):
        for item in expr.elements:
            _collect_expression_uses(item, uses, bound)
        return
    if isinstance(expr, Lambda):
        lambda_bound = bound | {name for name, _ in expr.params}
        _collect_expression_uses(expr.body, uses, lambda_bound)
        return
    if isinstance(expr, MemberAccess):
        _collect_expression_uses(expr.expression, uses, bound)
        return
    if isinstance(expr, IfThenElse):
        _collect_expression_uses(expr.condition, uses, bound)
        _collect_expression_uses(expr.then_expr, uses, bound)
        _collect_expression_uses(expr.else_expr, uses, bound)
        return
    if isinstance(expr, PerDurationExpression):
        _collect_expression_uses(expr.left, uses, bound)
        return
    if isinstance(expr, Distribution):
        for value in expr.params.values():
            _collect_expression_uses(value, uses, bound)
        return
    if isinstance(expr, BlockExpr):
        _collect_statement_uses(expr.statements, uses, bound)
        return


def _collect_statement_uses(statements: Iterable[Statement], uses: set[str], bound: set[str]) -> None:
    for stmt in statements:
        if isinstance(stmt, VarDecl):
            if stmt.value is not None:
                _collect_expression_uses(stmt.value, uses, bound)
        elif isinstance(stmt, Assignment):
            _collect_expression_uses(stmt.value, uses, bound)
        elif isinstance(stmt, Return) and stmt.value is not None:
            _collect_expression_uses(stmt.value, uses, bound)
        elif isinstance(stmt, IfStmt):
            _collect_expression_uses(stmt.condition, uses, bound)
            _collect_statement_uses(stmt.then_body, uses, bound)
            if stmt.else_body:
                _collect_statement_uses(stmt.else_body, uses, bound)
        elif isinstance(stmt, ForStmt):
            _collect_expression_uses(stmt.start, uses, bound)
            _collect_expression_uses(stmt.end, uses, bound)
            loop_bound = bound | {stmt.var_name}
            _collect_statement_uses(stmt.body, uses, loop_bound)
        else:
            if hasattr(stmt, "value") and isinstance(stmt.value, Expression):
                _collect_expression_uses(stmt.value, uses, bound)


def _collect_model_uses(model: Model) -> set[str]:
    uses: set[str] = set()
    bound: set[str] = set()

    for param in model.params:
        _collect_expression_uses(param.value, uses, bound)
    for var in model.vars:
        if var.value is not None:
            _collect_expression_uses(var.value, uses, bound)
    for func in model.funcs:
        func_bound = bound | {name for name, _ in func.parameters}
        _collect_statement_uses(func.body, uses, func_bound)
    for constraint in model.constraints:
        _collect_expression_uses(constraint.condition, uses, bound)
    for policy in model.policies:
        _collect_expression_uses(policy.trigger.condition, uses, bound)
        _collect_action_uses(policy.action, uses, bound)
    _collect_statement_uses(model.statements, uses, bound)

    return uses


def _collect_action_uses(action, uses: set[str], bound: set[str]) -> None:
    if action is None:
        return
    if getattr(action, "value", None) is not None:
        _collect_expression_uses(action.value, uses, bound)
    if getattr(action, "args", None):
        for value in action.args.values():
            _collect_expression_uses(value, uses, bound)
    if getattr(action, "statements", None):
        for nested in action.statements or []:
            _collect_action_uses(nested, uses, bound)


def _find_declaration_locations(context: LintContext) -> dict[str, tuple[int, int]]:
    locations: dict[str, tuple[int, int]] = {}
    tokens = context.tokens
    for idx, token in enumerate(tokens[:-1]):
        if token.type.name in {"PARAM", "VAR", "FUNC", "CONSTRAINT", "POLICY", "MODEL"}:
            next_token = tokens[idx + 1]
            if next_token.type.name == "IDENTIFIER":
                locations[next_token.value] = (next_token.line, next_token.column)
    return locations


class UnusedParamRule(LintRule):
    def __init__(self) -> None:
        super().__init__("PEL001", "Unused parameter", "warning")

    def run(self, context: LintContext) -> list[LintViolation]:
        if context.model is None:
            return []
        uses = _collect_model_uses(context.model)
        locations = _find_declaration_locations(context)
        violations: list[LintViolation] = []

        for param in context.model.params:
            if param.name.startswith("_"):
                continue
            if param.name not in uses:
                line, column = locations.get(param.name, (1, 1))
                violations.append(
                    LintViolation(
                        code=self.code,
                        message=f"Parameter '{param.name}' is never used",
                        severity=self.default_severity,
                        line=line,
                        column=column,
                        path=str(context.file_path) if context.file_path else None,
                        rule=self.description,
                    )
                )
        return violations


class UnreferencedVarRule(LintRule):
    def __init__(self) -> None:
        super().__init__("PEL002", "Unreferenced variable", "warning")

    def run(self, context: LintContext) -> list[LintViolation]:
        if context.model is None:
            return []
        uses = _collect_model_uses(context.model)
        locations = _find_declaration_locations(context)
        violations: list[LintViolation] = []

        for var in context.model.vars:
            if var.name.startswith("_"):
                continue
            if var.name not in uses:
                line, column = locations.get(var.name, (1, 1))
                violations.append(
                    LintViolation(
                        code=self.code,
                        message=f"Variable '{var.name}' is never referenced",
                        severity=self.default_severity,
                        line=line,
                        column=column,
                        path=str(context.file_path) if context.file_path else None,
                        rule=self.description,
                    )
                )
        return violations


class TypeMismatchRule(LintRule):
    def __init__(self) -> None:
        super().__init__("PEL004", "Type mismatch", "error")

    def run(self, context: LintContext) -> list[LintViolation]:
        if context.model is None:
            return []
        checker = TypeChecker()
        checker.check_model(context.model)
        violations: list[LintViolation] = []
        for error in checker.get_errors():
            line = error.location.line if error.location else 1
            column = error.location.column if error.location else 1
            violations.append(
                LintViolation(
                    code=self.code,
                    message=error.message,
                    severity=self.default_severity,
                    line=line,
                    column=column,
                    path=str(context.file_path) if context.file_path else None,
                    rule=self.description,
                )
            )
        return violations


class CircularDependencyRule(LintRule):
    def __init__(self) -> None:
        super().__init__("PEL005", "Circular dependency", "error")

    def run(self, context: LintContext) -> list[LintViolation]:
        if context.model is None:
            return []
        dependencies: dict[str, set[str]] = {var.name: set() for var in context.model.vars}

        def _target_name(target) -> str | None:
            if isinstance(target, Variable):
                return target.name
            if isinstance(target, Indexing) and isinstance(target.expression, Variable):
                return target.expression.name
            return None

        def _deps_from_expr(expr: Expression) -> set[str]:
            uses: set[str] = set()
            _collect_expression_uses(expr, uses, set())
            return uses

        for stmt in context.model.statements:
            if isinstance(stmt, Assignment):
                name = _target_name(stmt.target)
                if name in dependencies:
                    deps = _deps_from_expr(stmt.value)
                    if isinstance(stmt.target, Indexing) and name in deps:
                        deps.remove(name)
                    dependencies[name].update(deps)
        for var in context.model.vars:
            if var.value is not None:
                dependencies[var.name].update(_deps_from_expr(var.value))

        stack: list[str] = []
        visiting: set[str] = set()
        visited: set[str] = set()
        violations: list[LintViolation] = []

        def _visit(node: str) -> None:
            if node in visited:
                return
            if node in visiting:
                cycle_start = stack.index(node) if node in stack else 0
                cycle_path = stack[cycle_start:] + [node]
                violations.append(
                    LintViolation(
                        code=self.code,
                        message=f"Circular dependency detected: {' -> '.join(cycle_path)}",
                        severity=self.default_severity,
                        line=1,
                        column=1,
                        path=str(context.file_path) if context.file_path else None,
                        rule=self.description,
                    )
                )
                return
            visiting.add(node)
            stack.append(node)
            for dep in dependencies.get(node, set()):
                if dep in dependencies:
                    _visit(dep)
            stack.pop()
            visiting.remove(node)
            visited.add(node)

        for var in dependencies:
            _visit(var)

        return violations


class StyleRule(LintRule):
    def __init__(self) -> None:
        super().__init__("PEL008", "Style violation", "warning")

    def run(self, context: LintContext) -> list[LintViolation]:
        violations: list[LintViolation] = []
        for idx, line in enumerate(context.source_lines, start=1):
            if len(line) > context.config.line_length:
                violations.append(
                    LintViolation(
                        code=self.code,
                        message=f"Line exceeds {context.config.line_length} characters",
                        severity=self.default_severity,
                        line=idx,
                        column=context.config.line_length + 1,
                        path=str(context.file_path) if context.file_path else None,
                        rule=self.description,
                    )
                )
            if line.rstrip() != line:
                violations.append(
                    LintViolation(
                        code=self.code,
                        message="Trailing whitespace",
                        severity=self.default_severity,
                        line=idx,
                        column=len(line),
                        path=str(context.file_path) if context.file_path else None,
                        rule=self.description,
                    )
                )
        return violations


class NamingRule(LintRule):
    def __init__(self) -> None:
        super().__init__("PEL010", "Naming convention", "info")

    def _is_snake(self, name: str) -> bool:
        if not name:
            return False
        if name[0].isdigit():
            return False
        return name == name.lower() and all(ch.isalnum() or ch == "_" for ch in name)

    def run(self, context: LintContext) -> list[LintViolation]:
        if context.model is None:
            return []
        violations: list[LintViolation] = []
        locations = _find_declaration_locations(context)
        model_name = context.model.name
        if model_name and not model_name[0].isupper():
            line, column = locations.get(model_name, (1, 1))
            violations.append(
                LintViolation(
                    code=self.code,
                    message=f"Model '{model_name}' should be PascalCase",
                    severity=self.default_severity,
                    line=line,
                    column=column,
                    path=str(context.file_path) if context.file_path else None,
                    rule=self.description,
                )
            )
        for param in context.model.params:
            if not self._is_snake(param.name):
                line, column = locations.get(param.name, (1, 1))
                violations.append(
                    LintViolation(
                        code=self.code,
                        message=f"Parameter '{param.name}' should be snake_case",
                        severity=self.default_severity,
                        line=line,
                        column=column,
                        path=str(context.file_path) if context.file_path else None,
                        rule=self.description,
                    )
                )
        for var in context.model.vars:
            if not self._is_snake(var.name):
                line, column = locations.get(var.name, (1, 1))
                violations.append(
                    LintViolation(
                        code=self.code,
                        message=f"Variable '{var.name}' should be snake_case",
                        severity=self.default_severity,
                        line=line,
                        column=column,
                        path=str(context.file_path) if context.file_path else None,
                        rule=self.description,
                    )
                )
        return violations


AVAILABLE_RULES: dict[str, LintRule] = {
    "PEL001": UnusedParamRule(),
    "PEL002": UnreferencedVarRule(),
    "PEL004": TypeMismatchRule(),
    "PEL005": CircularDependencyRule(),
    "PEL008": StyleRule(),
    "PEL010": NamingRule(),
}
