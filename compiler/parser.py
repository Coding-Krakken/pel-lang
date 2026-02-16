# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""PEL Parser - Complete recursive descent parser for PEL language
Implements full grammar from spec/pel_language_spec.md Section 12
"""

from typing import Any

from compiler.ast_nodes import *
from compiler.errors import SourceLocation, syntax_error, unexpected_token
from compiler.lexer import Token, TokenType


class Parser:
    """Complete recursive descent parser for PEL language."""

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    def current(self) -> Token:
        """Get current token without consuming."""
        return self.tokens[self.pos] if self.pos < len(self.tokens) else self.tokens[-1]

    def peek(self, offset: int = 1) -> Token:
        """Peek ahead at token."""
        pos = self.pos + offset
        return self.tokens[pos] if pos < len(self.tokens) else self.tokens[-1]

    def advance(self) -> Token:
        """Consume and return current token."""
        token = self.current()
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return token

    def expect(self, token_type: TokenType) -> Token:
        """Consume token of expected type or raise error."""
        if self.current().type != token_type:
            raise unexpected_token(
                expected=token_type.name,
                got=self.current().type.name,
                location=SourceLocation("<input>", self.current().line, self.current().column)
            )
        return self.advance()

    def match(self, *token_types: TokenType) -> bool:
        """Check if current token matches any of the given types."""
        return self.current().type in token_types

    def consume_if(self, token_type: TokenType) -> Token | None:
        """Consume token if it matches type, otherwise return None."""
        if self.current().type == token_type:
            return self.advance()
        return None

    # ===== Top-level: Program =====

    def parse(self) -> Model:
        """Parse complete PEL program: imports + model declaration."""
        # TODO: Parse imports (not yet in AST)
        # imports = []
        # while self.match(TokenType.IMPORT):
        #     imports.append(self.parse_import())

        # Parse model declaration
        model = self.parse_model()
        self.expect(TokenType.EOF)
        return model

    def parse_model(self) -> Model:
        """Parse model declaration: model name { ... }"""
        self.expect(TokenType.MODEL)
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.LBRACE)

        model = Model(name=name)

        # Parse model items
        while not self.match(TokenType.RBRACE, TokenType.EOF):
            item = self.parse_model_item()
            if isinstance(item, ParamDecl):
                model.params.append(item)
            elif isinstance(item, VarDecl):
                model.vars.append(item)
            elif isinstance(item, FuncDecl):
                model.funcs.append(item)
            elif isinstance(item, Constraint):
                model.constraints.append(item)
            elif isinstance(item, Policy):
                model.policies.append(item)
            elif isinstance(item, Statement):
                model.statements.append(item)
            # TODO: record_decl, enum_decl, simulate_decl

        self.expect(TokenType.RBRACE)
        return model

    def parse_model_item(self) -> ParamDecl | VarDecl | FuncDecl | Constraint | Policy | Statement:
        """Parse a single model item."""
        if self.match(TokenType.PARAM):
            return self.parse_param()
        elif self.match(TokenType.VAR):
            return self.parse_var()
        elif self.match(TokenType.FUNC):
            return self.parse_func()
        elif self.match(TokenType.CONSTRAINT):
            return self.parse_constraint()
        elif self.match(TokenType.POLICY):
            return self.parse_policy()
        elif self.match(TokenType.IDENTIFIER, TokenType.IF, TokenType.FOR, TokenType.RETURN):
            return self.parse_statement()
        else:
            raise syntax_error(
                f"Expected model item (param, var, func, constraint, policy), got {self.current().type.name}",
                self.current_location()
            )

    # ===== Declarations =====

    def parse_param(self) -> ParamDecl:
        """Parse param declaration with provenance."""
        self.expect(TokenType.PARAM)
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.COLON)
        type_ann = self.parse_type()
        self.expect(TokenType.ASSIGN)
        value = self.parse_expression()
        provenance = self.parse_provenance_block()
        return ParamDecl(name=name, type_annotation=type_ann, value=value, provenance=provenance)

    def parse_var(self) -> VarDecl:
        """Parse var declaration."""
        self.expect(TokenType.VAR)
        is_mutable = self.consume_if(TokenType.MUT) is not None
        name = self.expect(TokenType.IDENTIFIER).value

        # Optional type annotation
        type_ann = None
        if self.consume_if(TokenType.COLON):
            type_ann = self.parse_type()

        value = None
        if self.consume_if(TokenType.ASSIGN):
            value = self.parse_expression()

        return VarDecl(name=name, type_annotation=type_ann, value=value, is_mutable=is_mutable)

    def parse_func(self) -> FuncDecl:
        """Parse function declaration."""
        self.expect(TokenType.FUNC)
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.LPAREN)

        # Parse parameter list
        params = []
        if not self.match(TokenType.RPAREN):
            params = self.parse_param_list()

        self.expect(TokenType.RPAREN)
        self.expect(TokenType.ARROW)
        return_type = self.parse_type()
        body = self.parse_block()

        return FuncDecl(name=name, parameters=params, return_type=return_type, body=body)

    def parse_param_list(self) -> list[tuple]:
        """Parse function parameter list: name: type, ..."""
        params = []
        params.append((self.expect(TokenType.IDENTIFIER).value, self.expect_and_parse_type()))

        while self.consume_if(TokenType.COMMA):
            param_name = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.COLON)
            param_type = self.parse_type()
            params.append((param_name, param_type))

        return params

    def expect_and_parse_type(self) -> TypeAnnotation:
        """Expect colon then parse type."""
        self.expect(TokenType.COLON)
        return self.parse_type()

    def parse_constraint(self) -> Constraint:
        """Parse constraint declaration."""
        self.expect(TokenType.CONSTRAINT)
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.COLON)
        condition = self.parse_expression()
        constraint_meta = self.parse_constraint_block()

        return Constraint(
            name=name,
            condition=condition,
            severity=constraint_meta.get('severity', 'fatal'),
            message=constraint_meta.get('message'),
            scope=constraint_meta.get('scope')
        )

    def parse_policy(self) -> Policy:
        """Parse policy declaration."""
        self.expect(TokenType.POLICY)
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.LBRACE)

        # Parse when clause
        self.expect(TokenType.WHEN)
        self.expect(TokenType.COLON)
        trigger_condition = self.parse_expression()
        self.expect(TokenType.COMMA)

        # Parse then clause
        self.expect(TokenType.THEN)
        self.expect(TokenType.COLON)
        action = self.parse_action()

        self.expect(TokenType.RBRACE)

        trigger = Trigger(trigger_type="condition", condition=trigger_condition)
        return Policy(name=name, trigger=trigger, action=action)

    # ===== Statements and Blocks =====

    def parse_statement(self) -> Statement:
        """Parse a statement (assignment, for/if, return)."""
        if self.match(TokenType.RETURN):
            self.advance()
            value = None
            if not self.match(TokenType.RBRACE, TokenType.SEMICOLON):
                value = self.parse_expression()
            self.consume_if(TokenType.SEMICOLON)
            return Return(value=value)

        if self.match(TokenType.FOR):
            return self.parse_for_stmt()

        if self.match(TokenType.IF):
            # Prefer statement-if when followed by a block, otherwise fall back to if-expression.
            checkpoint = self.pos
            self.advance()
            condition = self.parse_expression()
            if self.match(TokenType.LBRACE):
                then_body = self.parse_statement_block()
                else_body = None
                if self.consume_if(TokenType.ELSE):
                    else_body = self.parse_statement_block()
                return IfStmt(condition=condition, then_body=then_body, else_body=else_body)
            self.pos = checkpoint

        # Assignment or expression statement
        expr = self.parse_expression()
        if self.consume_if(TokenType.ASSIGN):
            value = self.parse_expression()
            self.consume_if(TokenType.SEMICOLON)
            return Assignment(target=expr, value=value)

        self.consume_if(TokenType.SEMICOLON)
        return Assignment(target=Variable(name="_"), value=Literal(value=0.0, literal_type="number"))

    def parse_for_stmt(self) -> ForStmt:
        """Parse for loop statement: for t in start..end { ... }"""
        self.expect(TokenType.FOR)
        var_name = self.expect(TokenType.IDENTIFIER).value

        in_token = self.expect(TokenType.IDENTIFIER)
        if in_token.value != "in":
            raise syntax_error("Expected 'in' in for statement", self.current_location())

        start = self.parse_expression()
        self.expect(TokenType.DOT)
        self.expect(TokenType.DOT)
        end = self.parse_expression()
        body = self.parse_statement_block()
        return ForStmt(var_name=var_name, start=start, end=end, body=body)

    def parse_statement_block(self) -> list[Statement]:
        """Parse a statement block: { stmt* }"""
        self.expect(TokenType.LBRACE)
        statements: list[Statement] = []
        while not self.match(TokenType.RBRACE, TokenType.EOF):
            statements.append(self.parse_statement())
        self.expect(TokenType.RBRACE)
        return statements

    # ===== Types =====

    def parse_type(self) -> TypeAnnotation:
        """Parse type annotation."""
        # Primitive types
        if self.match(TokenType.CURRENCY_TYPE):
            self.advance()
            self.expect(TokenType.LT)
            currency_code = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.GT)
            return TypeAnnotation(type_kind="Currency", params={"currency_code": currency_code})

        elif self.match(TokenType.RATE_TYPE):
            self.advance()
            self.consume_if(TokenType.PER)  # "per" keyword
            time_unit = self.expect(TokenType.IDENTIFIER).value
            return TypeAnnotation(type_kind="Rate", params={"per": time_unit})

        elif self.match(TokenType.DURATION_TYPE):
            self.advance()
            return TypeAnnotation(type_kind="Duration")

        elif self.match(TokenType.CAPACITY_TYPE):
            self.advance()
            self.expect(TokenType.LT)
            entity = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.GT)
            return TypeAnnotation(type_kind="Capacity", params={"entity": entity})

        elif self.match(TokenType.COUNT_TYPE):
            self.advance()
            self.expect(TokenType.LT)
            entity = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.GT)
            return TypeAnnotation(type_kind="Count", params={"entity": entity})

        elif self.match(TokenType.FRACTION_TYPE):
            self.advance()
            return TypeAnnotation(type_kind="Fraction")

        # Composite types
        elif self.match(TokenType.TIMESERIES_TYPE):
            self.advance()
            self.expect(TokenType.LT)
            inner_type = self.parse_type()
            self.expect(TokenType.GT)
            return TypeAnnotation(type_kind="TimeSeries", params={"inner": inner_type})

        elif self.match(TokenType.DISTRIBUTION_TYPE):
            self.advance()
            self.expect(TokenType.LT)
            inner_type = self.parse_type()
            self.expect(TokenType.GT)
            return TypeAnnotation(type_kind="Distribution", params={"inner": inner_type})

        # User-defined types (identifier)
        elif self.match(TokenType.IDENTIFIER):
            type_name = self.advance().value
            return TypeAnnotation(type_kind=type_name)

        else:
            raise syntax_error(f"Expected type, got {self.current().type.name}", self.current_location())

    # ===== Expressions (operator precedence parsing) =====

    def parse_expression(self, min_precedence: int = 0) -> Expression:
        """Parse expression with operator precedence."""
        left = self.parse_primary_expression()

        while True:
            # Check for binary operator
            if self.is_binary_operator():
                precedence = self.get_operator_precedence(self.current().type)
                if precedence < min_precedence:
                    break

                operator = self.parse_binary_operator()
                right = self.parse_expression(precedence + 1)
                left = BinaryOp(operator=operator, left=left, right=right)

            # Check for indexing: expr[...]
            elif self.match(TokenType.LBRACKET):
                self.advance()
                index = self.parse_expression()
                self.expect(TokenType.RBRACKET)
                left = Indexing(expression=left, index=index)

            # Check for member access: expr.member
            elif self.match(TokenType.DOT):
                # Distinguish member access from range syntax (..)
                if self.peek().type != TokenType.IDENTIFIER:
                    break
                self.advance()
                member = self.expect(TokenType.IDENTIFIER).value
                left = MemberAccess(expression=left, member=member)

            else:
                break

        return left

    def parse_primary_expression(self) -> Expression:
        """Parse primary expression (literals, identifiers, function calls, etc.)."""
        # Literals
        if self.match(TokenType.NUMBER):
            value = self.advance().value
            return Literal(value=float(value), literal_type="number")

        elif self.match(TokenType.CURRENCY):
            value = self.advance().value
            return Literal(value=value, literal_type="currency")

        elif self.match(TokenType.STRING):
            value = self.advance().value
            return Literal(value=value, literal_type="string")

        elif self.match(TokenType.PERCENTAGE):
            value = self.advance().value
            # Convert "5%" to 0.05
            numeric_value = float(value.rstrip('%')) / 100.0
            return Literal(value=numeric_value, literal_type="percentage")

        elif self.match(TokenType.DURATION):
            value = self.advance().value
            return Literal(value=value, literal_type="duration")

        # Boolean literals (true/false)
        # TODO: Add TRUE/FALSE token types to lexer

        # Distribution literal: ~ Beta(...)
        elif self.match(TokenType.TILDE):
            return self.parse_distribution()

        # Array literal: [1, 2, 3]
        elif self.match(TokenType.LBRACKET):
            return self.parse_array_literal()

        # Block expression: { ... }
        elif self.match(TokenType.LBRACE):
            return self.parse_block_expression()

        # Parenthesized expression or lambda
        elif self.match(TokenType.LPAREN):
            return self.parse_paren_or_lambda()

        # Conditional: if ... then ... else ...
        elif self.match(TokenType.IF):
            return self.parse_if_expression()

        # Unary operators: -, !
        elif self.match(TokenType.MINUS, TokenType.NOT):
            operator = self.advance().value
            operand = self.parse_primary_expression()
            return UnaryOp(operator=operator, operand=operand)

        # Identifier or function call
        elif self.match(TokenType.IDENTIFIER):
            name = self.advance().value

            # Function call: name(...)
            if self.match(TokenType.LPAREN):
                return self.parse_function_call(name)

            # Variable reference
            return Variable(name=name)

        else:
            raise syntax_error(f"Expected expression, got {self.current().type.name}", self.current_location())

    def parse_block_expression(self) -> BlockExpr:
        """Parse a block expression: { statements }"""
        statements = self.parse_statement_block()
        return BlockExpr(statements=statements)

    def parse_distribution(self) -> Distribution:
        """Parse distribution literal: ~ Beta(α=2, β=8)"""
        self.expect(TokenType.TILDE)
        dist_name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.LPAREN)

        # Parse named arguments
        params = {}
        if not self.match(TokenType.RPAREN):
            params = self.parse_named_arguments()

        self.expect(TokenType.RPAREN)
        return Distribution(dist_type=dist_name, params=params)

    def parse_named_arguments(self) -> dict[str, Expression]:
        """Parse named arguments: α=2, β=8"""
        args = {}

        param_name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.ASSIGN)
        param_value = self.parse_expression()
        args[param_name] = param_value

        while self.consume_if(TokenType.COMMA):
            if self.match(TokenType.RPAREN):  # Trailing comma
                break
            param_name = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.ASSIGN)
            param_value = self.parse_expression()
            args[param_name] = param_value

        return args

    def parse_array_literal(self) -> ArrayLiteral:
        """Parse array literal: [1, 2, 3]"""
        self.expect(TokenType.LBRACKET)
        elements = []

        if not self.match(TokenType.RBRACKET):
            elements.append(self.parse_expression())

            while self.consume_if(TokenType.COMMA):
                if self.match(TokenType.RBRACKET):  # Trailing comma
                    break
                elements.append(self.parse_expression())

        self.expect(TokenType.RBRACKET)
        return ArrayLiteral(elements=elements)

    def parse_paren_or_lambda(self) -> Expression:
        """Parse parenthesized expression or lambda: (...) or (x: T) -> expr"""
        self.expect(TokenType.LPAREN)

        # Empty parens: ()
        if self.match(TokenType.RPAREN):
            self.advance()
            self.expect(TokenType.ARROW)
            # Lambda with no params: () -> expr
            body = self.parse_expression()
            return Lambda(params=[], body=body)

        # Could be (expr) or (param: Type) -> expr
        # Look ahead to distinguish
        checkpoint = self.pos

        # Try parsing as parameter list
        try:
            if self.match(TokenType.IDENTIFIER) and self.peek().type == TokenType.COLON:
                # Lambda: (x: T, ...) -> expr
                params = self.parse_param_list()
                self.expect(TokenType.RPAREN)
                self.expect(TokenType.ARROW)
                body = self.parse_expression()
                return Lambda(params=params, body=body)
        except Exception:
            self.pos = checkpoint

        # Otherwise, parenthesized expression
        expr = self.parse_expression()
        self.expect(TokenType.RPAREN)
        return expr

    def parse_if_expression(self) -> IfThenElse:
        """Parse if-then-else expression."""
        self.expect(TokenType.IF)
        condition = self.parse_expression()
        self.expect(TokenType.THEN)
        then_expr = self.parse_expression()
        self.expect(TokenType.ELSE)
        else_expr = self.parse_expression()
        return IfThenElse(condition=condition, then_expr=then_expr, else_expr=else_expr)

    def parse_function_call(self, name: str) -> FunctionCall:
        """Parse function call: name(arg1, arg2, ...)"""
        self.expect(TokenType.LPAREN)
        args = []

        if not self.match(TokenType.RPAREN):
            args.append(self.parse_expression())

            while self.consume_if(TokenType.COMMA):
                if self.match(TokenType.RPAREN):  # Trailing comma
                    break
                args.append(self.parse_expression())

        self.expect(TokenType.RPAREN)
        return FunctionCall(function_name=name, arguments=args)

    # ===== Binary Operators =====

    def is_binary_operator(self) -> bool:
        """Check if current token is a binary operator."""
        return self.match(
            TokenType.PLUS, TokenType.MINUS, TokenType.STAR, TokenType.SLASH,
            TokenType.PERCENT, TokenType.CARET,
            TokenType.EQ, TokenType.NE, TokenType.LT, TokenType.LE, TokenType.GT, TokenType.GE,
            TokenType.AND, TokenType.OR
        )

    def parse_binary_operator(self) -> str:
        """Parse and return binary operator symbol."""
        token = self.advance()
        operator_map = {
            TokenType.PLUS: "+",
            TokenType.MINUS: "-",
            TokenType.STAR: "*",
            TokenType.SLASH: "/",
            TokenType.PERCENT: "%",
            TokenType.CARET: "^",
            TokenType.EQ: "==",
            TokenType.NE: "!=",
            TokenType.LT: "<",
            TokenType.LE: "<=",
            TokenType.GT: ">",
            TokenType.GE: ">=",
            TokenType.AND: "&&",
            TokenType.OR: "||",
        }
        return operator_map.get(token.type, token.value)

    def get_operator_precedence(self, token_type: TokenType) -> int:
        """Return operator precedence (higher = tighter binding)."""
        precedence_table = {
            TokenType.OR: 1,
            TokenType.AND: 2,
            TokenType.EQ: 3,
            TokenType.NE: 3,
            TokenType.LT: 4,
            TokenType.LE: 4,
            TokenType.GT: 4,
            TokenType.GE: 4,
            TokenType.PLUS: 5,
            TokenType.MINUS: 5,
            TokenType.STAR: 6,
            TokenType.SLASH: 6,
            TokenType.PERCENT: 6,
            TokenType.CARET: 7,  # Right-associative (handled separately)
        }
        return precedence_table.get(token_type, 0)

    # ===== Blocks and Statements =====

    def parse_block(self) -> list[Expression]:
        """Parse block: { stmt1 stmt2 ... }"""
        self.expect(TokenType.LBRACE)
        statements = []

        while not self.match(TokenType.RBRACE, TokenType.EOF):
            statements.append(self.parse_expression())
            # Optional semicolon
            self.consume_if(TokenType.SEMICOLON)

        self.expect(TokenType.RBRACE)
        return statements

    def parse_action(self) -> Action:
        """Parse policy action."""
        if self.match(TokenType.LBRACE):
            self.advance()
            actions: list[Action] = []
            while not self.match(TokenType.RBRACE, TokenType.EOF):
                actions.append(self.parse_action())
                self.consume_if(TokenType.SEMICOLON)
            self.expect(TokenType.RBRACE)
            return Action(action_type="block", statements=actions)

        if self.match(TokenType.EMIT):
            return self.parse_emit_action()

        # Simple actions: var = expr, var *= expr, emit event(...)
        if self.match(TokenType.IDENTIFIER):
            target = self.advance().value

            if self.consume_if(TokenType.ASSIGN):
                value = self.parse_expression()
                return Action(action_type="assign", target=target, value=value)

            # TODO: Handle +=, *=, etc.

        # Fallback: parse as expression (block)
        return Action(action_type="block", value=self.parse_expression())

    def parse_emit_action(self) -> Action:
        """Parse emit event(...)."""
        self.expect(TokenType.EMIT)
        self.expect(TokenType.EVENT)
        self.expect(TokenType.LPAREN)

        event_name = self.expect(TokenType.STRING).value
        args: dict[str, Expression] = {}

        while self.consume_if(TokenType.COMMA):
            if self.match(TokenType.RPAREN):
                break
            arg_name = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.COLON)
            args[arg_name] = self.parse_expression()

        self.expect(TokenType.RPAREN)
        return Action(action_type="emit_event", event_name=event_name, args=args)

    # ===== Provenance and Metadata =====

    def parse_provenance_block(self) -> dict[str, Any]:
        """Parse provenance block: { source: ..., method: ..., ... }"""
        self.expect(TokenType.LBRACE)
        provenance: dict[str, Any] = {}

        # Required: source, method, confidence
        provenance['source'] = self.parse_metadata_field('source')
        self.expect(TokenType.COMMA)
        provenance['method'] = self.parse_metadata_field('method')
        self.expect(TokenType.COMMA)
        provenance['confidence'] = self.parse_metadata_number_field('confidence')

        # Optional fields
        while self.consume_if(TokenType.COMMA):
            if self.match(TokenType.RBRACE):
                break

            field_name = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.COLON)

            if field_name == 'correlated_with':
                provenance[field_name] = self.parse_correlation_list()
            elif self.match(TokenType.NUMBER):
                provenance[field_name] = float(self.advance().value)
            elif self.match(TokenType.STRING):
                provenance[field_name] = self.advance().value
            else:
                # Default: parse as expression
                provenance[field_name] = self.parse_expression()

        self.expect(TokenType.RBRACE)
        return provenance

    def parse_metadata_field(self, field_name: str) -> str:
        """Parse a string metadata field."""
        self.expect(TokenType.IDENTIFIER)  # field name
        self.expect(TokenType.COLON)
        return self.expect(TokenType.STRING).value

    def parse_metadata_number_field(self, field_name: str) -> float:
        """Parse a numeric metadata field."""
        self.expect(TokenType.IDENTIFIER)  # field name
        self.expect(TokenType.COLON)
        return float(self.expect(TokenType.NUMBER).value)

    def parse_correlation_list(self) -> list[tuple]:
        """Parse correlation list: [(var1, coef1), (var2, coef2), ...]"""
        self.expect(TokenType.LBRACKET)
        correlations = []

        if not self.match(TokenType.RBRACKET):
            correlations.append(self.parse_correlation_pair())

            while self.consume_if(TokenType.COMMA):
                if self.match(TokenType.RBRACKET):
                    break
                correlations.append(self.parse_correlation_pair())

        self.expect(TokenType.RBRACKET)
        return correlations

    def parse_correlation_pair(self) -> tuple:
        """Parse correlation pair: (var_name, coefficient)"""
        self.expect(TokenType.LPAREN)
        varname = self.expect(TokenType.IDENTIFIER).value if self.match(TokenType.IDENTIFIER) else self.expect(TokenType.STRING).value
        self.expect(TokenType.COMMA)
        sign = -1.0 if self.consume_if(TokenType.MINUS) else 1.0
        coefficient = sign * float(self.expect(TokenType.NUMBER).value)
        self.expect(TokenType.RPAREN)
        return (varname, coefficient)

    def parse_constraint_block(self) -> dict[str, Any]:
        """Parse constraint metadata block."""
        self.expect(TokenType.LBRACE)
        metadata: dict[str, Any] = {}

        # Parse severity (required)
        self.expect(TokenType.IDENTIFIER)  # "severity"
        self.expect(TokenType.COLON)
        severity_token = self.expect(TokenType.IDENTIFIER)
        metadata['severity'] = severity_token.value  # "fatal" or "warning"

        # Optional fields
        while self.consume_if(TokenType.COMMA):
            if self.match(TokenType.RBRACE):
                break

            if self.match(TokenType.IDENTIFIER, TokenType.FOR):
                field_name = self.advance().value
            else:
                field_name = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.COLON)

            if field_name == 'message':
                metadata['message'] = self.expect(TokenType.STRING).value
            elif field_name == 'for':
                metadata['scope'] = self.parse_scope_spec()
            else:
                # Generic field
                metadata[field_name] = self.parse_expression()

        self.expect(TokenType.RBRACE)
        return metadata

    def parse_scope_spec(self) -> str | Expression:
        """Parse scope specification: 'all timesteps', etc."""
        # Common case: `all timesteps`
        if self.match(TokenType.IDENTIFIER) and self.current().value == "all":
            scope_parts = []
            while not self.match(TokenType.COMMA, TokenType.RBRACE):
                if self.match(TokenType.IDENTIFIER):
                    scope_parts.append(self.advance().value)
                else:
                    break
            return " ".join(scope_parts)

        # Otherwise treat scope as an expression like `t >= 6` or `t == 0`.
        # Note: this is not yet mapped into the structured `Scope` AST.
        return self.parse_expression()

    # ===== Utilities =====

    def current_location(self) -> SourceLocation:
        """Get current source location for errors."""
        token = self.current()
        return SourceLocation("<input>", token.line, token.column)
