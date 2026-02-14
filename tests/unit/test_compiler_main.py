from __future__ import annotations

import json
from pathlib import Path

import pytest

from compiler.compiler import PELCompiler
from compiler.compiler import main as compiler_main


def _write_file(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


@pytest.mark.unit
def test_pel_compiler_compile_defaults_output_path(tmp_path: Path) -> None:
    src = tmp_path / "m.pel"
    _write_file(
        src,
        (
            'model M {\n'
            '  param x: Fraction = 0.1 {\n'
            '    source: "unit",\n'
            '    method: "observed",\n'
            '    confidence: 1\n'
            '  }\n'
            '}\n'
        ),
    )

    compiler = PELCompiler(verbose=False)
    ir = compiler.compile(src)

    out = src.with_suffix(".ir.json")
    assert out.exists()
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["metadata"]["model_hash"] == ir["metadata"]["model_hash"]


@pytest.mark.unit
def test_pel_compiler_compile_verbose_prints_stages(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    src = tmp_path / "m.pel"
    _write_file(
        src,
        (
            'model M {\n'
            '  param x: Fraction = 0.1 {\n'
            '    source: "unit",\n'
            '    method: "observed",\n'
            '    confidence: 1\n'
            '  }\n'
            '}\n'
        ),
    )

    compiler = PELCompiler(verbose=True)
    compiler.compile(src)
    captured = capsys.readouterr()
    assert "[1/5] Lexer" in captured.out
    assert "[5/5] IR generator" in captured.out
    assert "Compiled successfully" in captured.out


@pytest.mark.unit
def test_compiler_main_exits_1_when_file_missing(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr("sys.argv", ["pel", "missing.pel"])
    with pytest.raises(SystemExit) as ex:
        compiler_main()
    assert ex.value.code == 1
    captured = capsys.readouterr()
    assert "File not found" in captured.err


@pytest.mark.unit
def test_compiler_main_exits_1_when_suffix_not_pel(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    src = tmp_path / "m.txt"
    _write_file(src, "hello")

    monkeypatch.setattr("sys.argv", ["pel", str(src)])
    with pytest.raises(SystemExit) as ex:
        compiler_main()
    assert ex.value.code == 1


@pytest.mark.unit
def test_compiler_main_success_writes_output(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    src = tmp_path / "m.pel"
    out = tmp_path / "m.ir.json"
    _write_file(
        src,
        (
            'model M {\n'
            '  param x: Fraction = 0.1 {\n'
            '    source: "unit",\n'
            '    method: "observed",\n'
            '    confidence: 1\n'
            '  }\n'
            '}\n'
        ),
    )

    monkeypatch.setattr("sys.argv", ["pel", str(src), "-o", str(out)])
    with pytest.raises(SystemExit) as ex:
        compiler_main()
    assert ex.value.code == 0
    assert out.exists()


@pytest.mark.unit
def test_compiler_main_exits_1_on_compiler_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    src = tmp_path / "bad.pel"
    _write_file(src, "model M { param x: Fraction = 0.1 }")

    monkeypatch.setattr("sys.argv", ["pel", str(src)])
    with pytest.raises(SystemExit) as ex:
        compiler_main()
    assert ex.value.code == 1


@pytest.mark.unit
def test_compiler_main_exits_2_on_unhandled_exception(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    src = tmp_path / "m.pel"
    _write_file(
        src,
        (
            'model M {\n'
            '  param x: Fraction = 0.1 {\n'
            '    source: "unit",\n'
            '    method: "observed",\n'
            '    confidence: 1\n'
            '  }\n'
            '}\n'
        ),
    )

    def _boom(self, *args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(PELCompiler, "compile", _boom)
    monkeypatch.setattr("sys.argv", ["pel", str(src)])
    with pytest.raises(SystemExit) as ex:
        compiler_main()
    assert ex.value.code == 2


@pytest.mark.unit
def test_compiler_main_verbose_unhandled_exception_prints_traceback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    src = tmp_path / "m.pel"
    _write_file(
        src,
        (
            'model M {\n'
            '  param x: Fraction = 0.1 {\n'
            '    source: "unit",\n'
            '    method: "observed",\n'
            '    confidence: 1\n'
            '  }\n'
            '}\n'
        ),
    )

    def _boom(self, *args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(PELCompiler, "compile", _boom)
    monkeypatch.setattr("sys.argv", ["pel", str(src), "--verbose"])
    with pytest.raises(SystemExit) as ex:
        compiler_main()
    assert ex.value.code == 2
    captured = capsys.readouterr()
    assert "Internal compiler error: boom" in captured.err
    assert "Traceback" in captured.err
