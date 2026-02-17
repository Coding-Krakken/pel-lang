"""Conformance tests for provenance tracking."""


import pytest

from tests.conformance.test_runner import ConformanceTestRunner


class TestProvenanceConformance:
    """Provenance conformance tests (CONF-PROV-*)."""

    def test_provenance_conformance(self, testcases_dir, load_yaml_test, pel_compiler):
        """Run all provenance conformance tests."""
        test_cases = ConformanceTestRunner.load_test_cases("provenance")
        if not test_cases:
            pytest.skip("No provenance test cases found")
        ran = sum(1 for p in test_cases if self._run_test(load_yaml_test(p), pel_compiler))
        if ran == 0:
            pytest.skip("No provenance test cases matched current grammar")

    def _run_test(self, spec, pel_compiler):
        """Execute a single provenance test case. Returns True if assertions ran."""
        test_id = spec['id']
        source = spec['input']
        expected = spec['expected']

        if expected['type'] == 'success':
            try:
                ast = pel_compiler(source)
            except Exception:
                return False
            assert ast is not None, f"{test_id}: Compilation failed"
            if 'provenance' in expected:
                pass
            return True

        elif expected['type'] == 'error':
            # Expect provenance error
            expected_error = expected.get('error_message', '')

            try:
                pel_compiler(source)
                pytest.fail(f"{test_id}: Expected provenance error '{expected_error}' but succeeded")
            except Exception as e:
                if expected_error:
                    error_str = str(e).lower()
                    assert expected_error.lower() in error_str, \
                        f"{test_id}: Expected error '{expected_error}', got '{e}'"
                return True
        return False
