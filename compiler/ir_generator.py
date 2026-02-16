# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""PEL IR Generator - Generate PEL-IR JSON from typed AST
"""

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from compiler.ast_nodes import *


class IRGenerator:
    """Generate PEL-IR from typed AST."""

    def __init__(self, source_path: str, compiler_version: str = "0.1.0"):
        self.source_path = source_path
        self.compiler_version = compiler_version
        self.node_counter = 0

    def generate(self, model: Model) -> dict[str, Any]:
        """Generate complete IR document."""
        ir_model = {
            "name": model.name,
            "time_horizon": model.time_horizon,
            "time_unit": model.time_unit,
            "nodes": [],
            "constraints": [],
            "policies": []
        }

        # Convert params to nodes
        for param in model.params:
            ir_model["nodes"].append(self.generate_param_node(param))

        # Convert vars to nodes
        for var in model.vars:
            ir_model["nodes"].append(self.generate_var_node(var))

        # Convert constraints
        for const in model.constraints:
            ir_model["constraints"].append(self.generate_constraint(const))

        # Convert policies
        for policy in model.policies:
            ir_model["policies"].append(self.generate_policy(policy))

        # Generate metadata
        metadata = self.generate_metadata(ir_model)

        return {
            "version": "0.1.0",
            "model": ir_model,
            "metadata": metadata
        }

    def generate_param_node(self, param: ParamDecl) -> dict[str, Any]:
        """Generate IR node for parameter."""
        node_id = f"param_{self.node_counter}"
        self.node_counter += 1

        return {
            "node_id": node_id,
            "node_type": "param",
            "name": param.name,
            "type_annotation": self.generate_type(param.type_annotation),
            "value": self.generate_expression(param.value),
            "provenance": self.generate_provenance(param.provenance) if param.provenance else None,
            "dependencies": []
        }

    def generate_var_node(self, var: VarDecl) -> dict[str, Any]:
        """Generate IR node for variable."""
        node_id = f"var_{self.node_counter}"
        self.node_counter += 1

        node = {
            "node_id": node_id,
            "node_type": "var",
            "name": var.name,
            "type_annotation": self.generate_type(var.type_annotation) if var.type_annotation else None,
            "is_mutable": getattr(var, 'is_mutable', False),
            "dependencies": []
        }

        # Add value if present
        if var.value:
            node["value"] = self.generate_expression(var.value)
            # Extract dependencies from expression
            node["dependencies"] = self.extract_dependencies(var.value)

        return node

    def extract_dependencies(self, expr: Expression) -> list:
        """Extract variable dependencies from an expression."""
        deps = set()

        if isinstance(expr, Variable):
            deps.add(expr.name)
        elif isinstance(expr, BinaryOp):
            deps.update(self.extract_dependencies(expr.left))
            deps.update(self.extract_dependencies(expr.right))
        elif isinstance(expr, UnaryOp):
            deps.update(self.extract_dependencies(expr.operand))
        elif isinstance(expr, FunctionCall):
            for arg in expr.arguments:
                deps.update(self.extract_dependencies(arg))
        elif isinstance(expr, IfThenElse):
            deps.update(self.extract_dependencies(expr.condition))
            deps.update(self.extract_dependencies(expr.then_expr))
            deps.update(self.extract_dependencies(expr.else_expr))
        elif isinstance(expr, Distribution):
            for param_expr in expr.params.values():
                deps.update(self.extract_dependencies(param_expr))
        elif isinstance(expr, ArrayLiteral):
            for elem in expr.elements:
                deps.update(self.extract_dependencies(elem))
        elif isinstance(expr, Indexing):
            deps.update(self.extract_dependencies(expr.expression))
            deps.update(self.extract_dependencies(expr.index))
        elif isinstance(expr, Lambda):
            deps.update(self.extract_dependencies(expr.body))
        elif isinstance(expr, MemberAccess):
            deps.update(self.extract_dependencies(expr.expression))

        return list(deps)

    def generate_type(self, typ: TypeAnnotation) -> dict[str, Any]:
        """Generate IR type annotation."""
        result: dict[str, Any] = {"type_kind": typ.type_kind}
        for key, value in typ.params.items():
            if isinstance(value, TypeAnnotation):
                result[key] = self.generate_type(value)
            else:
                result[key] = value
        return result

    def generate_expression(self, expr: Expression) -> dict[str, Any]:
        """Generate IR expression - complete implementation."""
        if isinstance(expr, Literal):
            return {
                "expr_type": "Literal",
                "literal_type": getattr(expr, 'literal_type', 'number'),
                "literal_value": expr.value
            }

        elif isinstance(expr, Variable):
            return {
                "expr_type": "Variable",
                "variable_name": expr.name
            }

        elif isinstance(expr, BinaryOp):
            return {
                "expr_type": "BinaryOp",
                "operator": expr.operator,
                "left": self.generate_expression(expr.left),
                "right": self.generate_expression(expr.right)
            }

        elif isinstance(expr, UnaryOp):
            return {
                "expr_type": "UnaryOp",
                "operator": expr.operator,
                "operand": self.generate_expression(expr.operand)
            }

        elif isinstance(expr, FunctionCall):
            return {
                "expr_type": "FunctionCall",
                "function_name": expr.function_name,
                "arguments": [self.generate_expression(arg) for arg in expr.arguments]
            }

        elif isinstance(expr, IfThenElse):
            return {
                "expr_type": "IfThenElse",
                "condition": self.generate_expression(expr.condition),
                "then_expr": self.generate_expression(expr.then_expr),
                "else_expr": self.generate_expression(expr.else_expr)
            }

        elif isinstance(expr, Distribution):
            return {
                "expr_type": "Distribution",
                "dist_type": expr.dist_type,
                "params": {k: self.generate_expression(v) for k, v in expr.params.items()}
            }

        elif isinstance(expr, ArrayLiteral):
            return {
                "expr_type": "ArrayLiteral",
                "elements": [self.generate_expression(elem) for elem in expr.elements]
            }

        elif isinstance(expr, Indexing):
            return {
                "expr_type": "Indexing",
                "expression": self.generate_expression(expr.expression),
                "index": self.generate_expression(expr.index)
            }

        elif isinstance(expr, Lambda):
            return {
                "expr_type": "Lambda",
                "params": [(name, self.generate_type(typ)) for name, typ in expr.params],
                "body": self.generate_expression(expr.body)
            }

        elif isinstance(expr, MemberAccess):
            return {
                "expr_type": "MemberAccess",
                "expression": self.generate_expression(expr.expression),
                "member": expr.member
            }

        else:
            # Fallback for unknown expression types
            return {"expr_type": "Unknown"}

    def generate_provenance(self, prov: Provenance) -> dict[str, Any]:
        """Generate IR provenance block."""
        # Parser currently produces provenance as a plain dict.
        if isinstance(prov, dict):
            return dict(prov)

        result = {
            "source": prov.source,
            "method": prov.method,
            "confidence": prov.confidence,
        }
        if prov.freshness:
            result["freshness"] = prov.freshness
        if prov.owner:
            result["owner"] = prov.owner
        if prov.notes:
            result["notes"] = prov.notes
        return result

    def generate_constraint(self, const: Constraint) -> dict[str, Any]:
        """Generate IR constraint (stub)."""
        return {
            "constraint_id": f"const_{const.name}",
            "name": const.name,
            "condition": self.generate_expression(const.condition),
            "severity": const.severity
        }

    def generate_policy(self, policy: Policy) -> dict[str, Any]:
        """Generate IR policy (stub)."""
        return {
            "policy_id": f"policy_{policy.name}",
            "name": policy.name,
            "trigger": {"trigger_type": policy.trigger.trigger_type, "condition": {}},
            "action": {"action_type": policy.action.action_type}
        }

    def generate_metadata(self, ir_model: dict[str, Any]) -> dict[str, Any]:
        """Generate metadata with model hash."""
        # Normalize and hash
        model_json = json.dumps(ir_model, sort_keys=True)
        model_hash = hashlib.sha256(model_json.encode()).hexdigest()

        return {
            "model_hash": f"sha256:{model_hash}",
            "compiled_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "compiler_version": f"pel-{self.compiler_version}",
            "source_file": self.source_path
        }
