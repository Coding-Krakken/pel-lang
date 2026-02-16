"""Assertion helpers for conformance tests."""

from typing import List, Dict, Any, Optional
from compiler.lexer import Token, TokenType
from compiler.ast_nodes import ASTNode


def assert_tokens_match(actual_tokens: List[Token], expected_tokens: List[Dict[str, Any]]):
    """Assert token stream matches expected sequence.
    
    Args:
        actual_tokens: List of tokens from lexer
        expected_tokens: List of expected token specs with 'type' and optional 'value'
    """
    assert len(actual_tokens) == len(expected_tokens), \
        f"Token count mismatch: expected {len(expected_tokens)}, got {len(actual_tokens)}"
    
    for i, (actual, expected) in enumerate(zip(actual_tokens, expected_tokens)):
        expected_type = expected['type']
        
        # Handle string type names or TokenType enums
        if isinstance(expected_type, str):
            assert actual.type.name == expected_type, \
                f"Token {i}: expected type {expected_type}, got {actual.type.name}"
        else:
            assert actual.type == expected_type, \
                f"Token {i}: expected type {expected_type}, got {actual.type}"
        
        # Check value if specified
        if 'value' in expected:
            assert actual.value == expected['value'], \
                f"Token {i}: expected value {expected['value']}, got {actual.value}"


def assert_ast_structure(ast: ASTNode, expected: Dict[str, Any]):
    """Assert AST structure matches expected shape.
    
    Args:
        ast: Root AST node
        expected: Expected structure with 'node_type' and optional 'attributes'
    """
    assert type(ast).__name__ == expected['node_type'], \
        f"Expected AST node type {expected['node_type']}, got {type(ast).__name__}"
    
    # Check attributes if specified
    if 'attributes' in expected:
        for attr_name, expected_value in expected['attributes'].items():
            actual_value = getattr(ast, attr_name, None)
            assert actual_value == expected_value, \
                f"AST attribute '{attr_name}': expected {expected_value}, got {actual_value}"


def assert_type_annotation(node: ASTNode, expected_type: str):
    """Assert type annotation matches expected type.
    
    Args:
        node: AST node with type annotation
        expected_type: Expected type as string
    """
    assert hasattr(node, 'type'), f"Node {type(node).__name__} has no type annotation"
    
    actual_type = str(node.type) if node.type else None
    assert actual_type == expected_type, \
        f"Type mismatch: expected {expected_type}, got {actual_type}"


def assert_dimension_error(source: str, expected_error: str, pel_compiler):
    """Assert dimensional analysis produces expected error.
    
    Args:
        source: PEL source code
        expected_error: Expected error message substring
        pel_compiler: Compiler fixture
    """
    try:
        ast = pel_compiler(source)
        # If we get here, no error was raised
        pytest.fail(f"Expected dimensional error containing '{expected_error}', but compilation succeeded")
    except Exception as e:
        error_msg = str(e)
        assert expected_error in error_msg, \
            f"Expected error containing '{expected_error}', got: {error_msg}"


def assert_parse_error(source: str, expected_error: str, pel_compiler):
    """Assert parsing produces expected error.
    
    Args:
        source: PEL source code
        expected_error: Expected error message substring
        pel_compiler: Compiler fixture
    """
    import pytest
    
    with pytest.raises(Exception) as exc_info:
        pel_compiler(source)
    
    error_msg = str(exc_info.value)
    assert expected_error in error_msg or expected_error in type(exc_info.value).__name__, \
        f"Expected error containing '{expected_error}', got: {error_msg}"


def assert_provenance_chain(ast: ASTNode, expected_provenance: Dict[str, List[str]]):
    """Assert provenance tracking matches expected dependencies.
    
    Args:
        ast: AST with provenance information
        expected_provenance: Map of variable names to their dependencies
    """
    if not hasattr(ast, 'provenance_map'):
        pytest.fail("AST has no provenance_map attribute")
    
    for var_name, expected_deps in expected_provenance.items():
        assert var_name in ast.provenance_map, \
            f"Variable '{var_name}' not found in provenance map"
        
        actual_deps = ast.provenance_map[var_name]
        assert set(actual_deps) == set(expected_deps), \
            f"Provenance for '{var_name}': expected {expected_deps}, got {actual_deps}"


def assert_runtime_value(result: Any, expected_value: Any, tolerance: float = 1e-9):
    """Assert runtime evaluation matches expected value.
    
    Args:
        result: Actual runtime result
        expected_value: Expected value
        tolerance: Tolerance for float comparisons
    """
    if isinstance(expected_value, float):
        assert abs(result - expected_value) < tolerance, \
            f"Runtime value mismatch: expected {expected_value}, got {result}"
    else:
        assert result == expected_value, \
            f"Runtime value mismatch: expected {expected_value}, got {result}"
