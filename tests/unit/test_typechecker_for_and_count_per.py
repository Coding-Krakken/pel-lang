"""Regression tests for function for-loop scope and Count-per-time semantics."""
import tempfile
from pathlib import Path

import pytest

from compiler.compiler import PELCompiler
from compiler.errors import TypeError as CompilerTypeError


def _compile_model(model_src: str) -> dict:
    fd, tmp = tempfile.mkstemp(suffix=".pel")
    Path(tmp).write_text(model_src + "\n", encoding="utf-8")
    return PELCompiler(verbose=False).compile(Path(tmp))


@pytest.mark.unit
def test_for_loop_variable_scoped_in_function_typecheck() -> None:
    model_src = """
model LoopScope {
  func sum_to_n(n: Count) -> Count {
    var s: Count = 0
    for i in 0..n {
      s = s + i
    }
    return s
  }

  var out: Count = sum_to_n(3)
}
"""

    result = _compile_model(model_src)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_count_per_time_rejects_plain_int() -> None:
    model_src = """
model CountPerReject {
  var throughput: Count<User> per Day = 10
}
"""

    with pytest.raises(CompilerTypeError):
        _compile_model(model_src)


@pytest.mark.unit
def test_count_per_time_accepts_count_div_duration() -> None:
    model_src = """
model CountPerAccept {
  var users: Count<User> = 300
  var window: Duration<Day> = 30d
  var throughput: Count<User> per Day = users / window
}
"""

    result = _compile_model(model_src)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_count_per_time_rejects_mismatched_time_unit() -> None:
    model_src = """
model CountPerMismatch {
  var users: Count<User> = 300
  var window: Duration<Day> = 30d
  var throughput: Count<User> per Month = users / window
}
"""

    with pytest.raises(CompilerTypeError):
        _compile_model(model_src)
