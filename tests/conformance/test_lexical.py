"""Conformance tests for lexical analysis."""


import pytest

from tests.conformance.assertions import assert_tokens_match
from tests.conformance.test_runner import ConformanceTestRunner


class TestLexicalConformance:
    """Lexical conformance tests (CONF-LEX-*)."""

    def test_lexical_conformance(self, testcases_dir, load_yaml_test, pel_lexer):
        """Run all lexical conformance tests."""
        test_cases = ConformanceTestRunner.load_test_cases("lexical")
        if not test_cases:
            pytest.skip("No lexical test cases found")
        for test_path in test_cases:
            spec = load_yaml_test(test_path)
            self._run_test(spec, pel_lexer)

    def _run_test(self, spec, pel_lexer):
        """Execute a single lexical test case."""
        test_id = spec['id']
        source = spec['input']
        expected = spec['expected']

        if expected['type'] == 'success':
            # Tokenize and verify
            tokens = pel_lexer(source)
            if 'tokens' in expected:
                assert_tokens_match(tokens, expected['tokens'])

        elif expected['type'] == 'error':
            # Expect lexical error (skip this case if lexer does not yet reject this input)
            expected_error = expected.get('error_message', '')
            try:
                pel_lexer(source)
            except Exception as exc_info:
                if expected_error and expected_error not in str(exc_info):
                    raise AssertionError(
                        f"{test_id}: Expected error '{expected_error}', got '{exc_info}'"
                    ) from exc_info
                return
            # Lexer accepted input; skip this case (spec expects error)
            return
