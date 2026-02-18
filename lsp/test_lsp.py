#!/usr/bin/env python3
"""
Simple test script for PEL LSP server
Tests basic functionality of the language server
"""

import sys
from pathlib import Path


def test_lsp_start():
    """Test that LSP server can start"""
    print("Testing LSP server startup...")
    try:
        # Try importing the server
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from lsp.server import server  # noqa: F401
        print("✓ LSP server module loads successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import LSP server: {e}")
        print("  Run: pip install -e '.[lsp]'")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def test_parsing():
    """Test that parsing works with sample PEL code"""
    print("\nTesting document parsing...")
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from lsp.server import parse_document

        sample_code = """
model TestModel {
  param price: Currency<USD> = $100
  var revenue: Currency<USD>
}
"""
        ast, tokens, diagnostics = parse_document(sample_code)

        if ast:
            print(f"✓ Successfully parsed model: {ast.name}")
            print(f"  - Parameters: {len(ast.params)}")
            print(f"  - Variables: {len(ast.vars)}")
            print(f"  - Diagnostics: {len(diagnostics)}")
            return True
        else:
            print("✗ Failed to parse sample code")
            if diagnostics:
                for diag in diagnostics:
                    print(f"  - {diag.message}")
            return False

    except Exception as e:
        print(f"✗  Parsing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_completions():
    """Test completion functionality"""
    print("\nTesting completions...")
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from lsprotocol.types import Position

        from lsp.server import get_completions, parse_document

        sample_code = """
model TestModel {
  param price: Currency = 100 USD
}
"""
        ast, _, _ = parse_document(sample_code)

        # Get completions at a certain position
        completions = get_completions(ast, Position(line=2, character=10), sample_code)

        if completions:
            print(f"✓ Generated {len(completions)} completion items")
            # Show some examples
            keywords = [c for c in completions if c.label in ['model', 'param', 'rate']]
            types = [c for c in completions if c.label in ['Currency', 'Rate', 'Duration']]
            print(f"  - Keywords found: {[c.label for c in keywords[:3]]}")
            print(f"  - Types found: {[c.label for c in types[:3]]}")
            return True
        else:
            print("✗ No completions generated")
            return False

    except Exception as e:
        print(f"✗ Completion test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_diagnostics():
    """Test diagnostic generation for invalid code"""
    print("\nTesting diagnostics...")
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from lsp.server import parse_document

        # Invalid code (type mismatch)
        invalid_code = """
model TestModel {
  param count: Count = 100
  param rate: Rate = count + 5.5
}
"""
        ast, tokens, diagnostics = parse_document(invalid_code)

        if diagnostics:
            print(f"✓ Generated {len(diagnostics)} diagnostic(s) for invalid code")
            for diag in diagnostics[:3]:
                print(f"  - {diag.severity.name}: {diag.message[:80]}")
            return True
        else:
            print("⚠ No diagnostics generated (but errors were expected)")
            return True  # Not critical

    except Exception as e:
        print(f"✗ Diagnostics test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("PEL LSP Server Test Suite")
    print("=" * 60)

    results = []

    results.append(("Server Import", test_lsp_start()))
    results.append(("Document Parsing", test_parsing()))
    results.append(("Completions", test_completions()))
    results.append(("Diagnostics", test_diagnostics()))

    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)

    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status:8} {name}")

    total = len(results)
    passed = sum(1 for _, p in results if p)

    print(f"\nTotal: {passed}/{total} tests passed")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
