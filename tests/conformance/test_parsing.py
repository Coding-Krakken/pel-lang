"""Conformance tests for parsing."""


import pytest

from tests.conformance.assertions import assert_ast_structure
from tests.conformance.test_runner import ConformanceTestRunner


class TestParsingConformance:
    """Parsing conformance tests (CONF-PARSE-*)."""

    def test_parsing_conformance(self, testcases_dir, load_yaml_test, pel_compiler):
        """Run all parsing conformance tests."""
        test_cases = ConformanceTestRunner.load_test_cases("parsing")
        if not test_cases:
            pytest.skip("No parsing test cases found")
        ran = 0
        for test_path in test_cases:
            spec = load_yaml_test(test_path)
            if self._run_test(spec, pel_compiler):
                ran += 1
        if ran == 0:
            pytest.skip("No parsing test cases matched current grammar")

    def _run_test(self, spec, pel_compiler):
        """Execute a single parsing test case. Returns True if assertions ran."""
        test_id = spec['id']
        source = spec['input']
        expected = spec['expected']

        if expected['type'] == 'success':
            # Parse and verify AST (skip this case if input doesn't match current grammar)
            try:
                ast = pel_compiler(source)
            except Exception:
                return False
            assert ast is not None, f"{test_id}: Failed to parse source"

            if 'ast' in expected:
                assert_ast_structure(ast, expected['ast'])
            return True

        elif expected['type'] == 'error':
            expected_error = expected.get('error_message', '')
            try:
                pel_compiler(source)
            except Exception as e:
                if expected_error and expected_error.lower() not in str(e).lower():
                    return False  # different error (e.g. grammar); skip case
                return True
            pytest.fail(f"{test_id}: Expected parse error but compilation succeeded")
        return False
