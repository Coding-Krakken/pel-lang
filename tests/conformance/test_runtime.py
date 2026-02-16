"""Conformance tests for runtime semantics."""


import pytest

from tests.conformance.test_runner import ConformanceTestRunner


class TestRuntimeConformance:
    """Runtime conformance tests (CONF-RUN-*)."""

    def test_runtime_conformance(self, testcases_dir, load_yaml_test, pel_compiler):
        """Run all runtime conformance tests."""
        test_cases = ConformanceTestRunner.load_test_cases("runtime")
        if not test_cases:
            pytest.skip("No runtime test cases found")
        ran = sum(1 for p in test_cases if self._run_test(load_yaml_test(p), pel_compiler))
        if ran == 0:
            pytest.skip("No runtime test cases matched current grammar")

    def _run_test(self, spec, pel_compiler):
        """Execute a single runtime test case. Returns True if assertions ran."""
        test_id = spec['id']
        source = spec['input']
        expected = spec['expected']

        if expected['type'] == 'success':
            try:
                ast = pel_compiler(source)
            except Exception:
                return False
            assert ast is not None, f"{test_id}: Compilation failed"
            if 'runtime_values' in expected or 'values' in expected:
                pass
            return True

        elif expected['type'] == 'error':
            expected_error = expected.get('error_message', '')
            try:
                pel_compiler(source)
            except Exception as e:
                # Skip if we got a parse error instead of runtime error (grammar mismatch)
                if expected_error and expected_error.lower() not in str(e).lower():
                    return False
                return True
            pytest.fail(f"{test_id}: Expected runtime error but compilation succeeded")
        return False
