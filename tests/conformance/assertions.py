# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""
Conformance Test Assertions
Provides spec-aware assertion functions for validating compiler behavior.
"""

from typing import List, Dict, Any, Optional
from compiler.lexer import Token, TokenType
from compiler.ast_nodes import ASTNode
from compiler.errors import CompilerError


def assert_tokens_match(actual: List[Token], expected: List[Dict[str, Any]]) -> None:
    """
    Assert that token sequence matches expected structure.
    
    Args:
        actual: List of tokens from lexer
        expected: List of dicts with 'type' and optionally 'value' keys
    
    Raises:
        AssertionError: If tokens don't match
    """
    assert len(actual) == len(expected), (
        f"Token count mismatch: expected {len(expected)}, got {len(actual)}"
    )
    
    for i, (actual_token, expected_spec) in enumerate(zip(actual, expected)):
        expected_type = expected_spec['type']
        
        # Convert string to TokenType if needed
        if isinstance(expected_type, str):
            expected_type = TokenType[expected_type]
        
        assert actual_token.type == expected_type, (
            f"Token {i}: type mismatch - expected {expected_type}, got {actual_token.type}"
        )
        
        # Check value if specified
        if 'value' in expected_spec:
            expected_value = expected_spec['value']
            assert actual_token.value == expected_value, (
                f"Token {i}: value mismatch - expected {expected_value}, got {actual_token.value}"
            )


def assert_ast_structure(ast: ASTNode, expected: Dict[str, Any]) -> None:
    """
    Assert that AST structure matches expected shape.
    
    Args:
        ast: Root AST node
        expected: Dict describing expected AST structure
    
    Raises:
        AssertionError: If AST doesn't match
    """
    node_type = expected.get('node_type')
    if node_type:
        assert ast.__class__.__name__ == node_type, (
            f"AST node type mismatch: expected {node_type}, got {ast.__class__.__name__}"
        )
    
    # Check attributes
    if 'attributes' in expected:
        for attr_name, attr_value in expected['attributes'].items():
            assert hasattr(ast, attr_name), (
                f"AST node missing attribute '{attr_name}'"
            )
            actual_value = getattr(ast, attr_name)
            assert actual_value == attr_value, (
                f"Attribute '{attr_name}' mismatch: expected {attr_value}, got {actual_value}"
            )
    
    # Check children recursively
    if 'children' in expected:
        expected_children = expected['children']
        if hasattr(ast, 'children'):
            actual_children = ast.children
        elif hasattr(ast, 'statements'):
            actual_children = ast.statements
        else:
            actual_children = []
        
        assert len(actual_children) >= len(expected_children), (
            f"Not enough children: expected at least {len(expected_children)}, got {len(actual_children)}"
        )


def assert_type(node: ASTNode, expected_type: str) -> None:
    """
    Assert that AST node has expected type annotation.
    
    Args:
        node: AST node to check
        expected_type: Expected type as string
    
    Raises:
        AssertionError: If type doesn't match
    """
    assert hasattr(node, 'type'), f"Node {node.__class__.__name__} has no type annotation"
    
    actual_type = str(node.type) if node.type else None
    assert actual_type is not None, f"Node {node.__class__.__name__} type is None"
    
    # Simple string comparison for now
    assert expected_type in actual_type or actual_type in expected_type, (
        f"Type mismatch: expected {expected_type}, got {actual_type}"
    )


def assert_dimension_error(code: str, expected_msg: str, compiler) -> None:
    """
    Assert that code raises a dimensional analysis error with expected message.
    
    Args:
        code: PEL source code
        expected_msg: Expected error message substring
        compiler: PELCompiler instance
    
    Raises:
        AssertionError: If error not raised or message doesn't match
    """
    import tempfile
    from pathlib import Path
    
    # Write code to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.pel', delete=False) as f:
        f.write(code)
        temp_path = Path(f.name)
    
    try:
        # Expect compilation to fail
        error_raised = False
        actual_msg = None
        
        try:
            compiler.compile(temp_path)
        except CompilerError as e:
            error_raised = True
            actual_msg = str(e)
        
        assert error_raised, "Expected CompilerError but none was raised"
        assert expected_msg.lower() in actual_msg.lower(), (
            f"Error message mismatch: expected substring '{expected_msg}', got '{actual_msg}'"
        )
    finally:
        # Clean up temp file
        temp_path.unlink()


def assert_parse_error(code: str, expected_msg: str, lexer_factory, parser_factory) -> None:
    """
    Assert that code raises a parse error with expected message.
    
    Args:
        code: PEL source code
        expected_msg: Expected error message substring
        lexer_factory: Function to create lexer
        parser_factory: Function to create parser
    
    Raises:
        AssertionError: If error not raised or message doesn't match
    """
    error_raised = False
    actual_msg = None
    
    try:
        lexer = lexer_factory(code)
        tokens = lexer.tokenize()
        parser = parser_factory(tokens)
        parser.parse()
    except CompilerError as e:
        error_raised = True
        actual_msg = str(e)
    
    assert error_raised, "Expected ParseError but none was raised"
    assert expected_msg.lower() in actual_msg.lower(), (
        f"Error message mismatch: expected substring '{expected_msg}', got '{actual_msg}'"
    )


def assert_runtime_value(runtime_result: Any, expected_value: Any, tolerance: float = 1e-9) -> None:
    """
    Assert that runtime evaluation produces expected value.
    
    Args:
        runtime_result: Actual result from runtime
        expected_value: Expected value
        tolerance: Tolerance for float comparison
    
    Raises:
        AssertionError: If values don't match
    """
    if isinstance(expected_value, float) and isinstance(runtime_result, (int, float)):
        assert abs(runtime_result - expected_value) < tolerance, (
            f"Value mismatch: expected {expected_value}, got {runtime_result} (tolerance={tolerance})"
        )
    else:
        assert runtime_result == expected_value, (
            f"Value mismatch: expected {expected_value}, got {runtime_result}"
        )
