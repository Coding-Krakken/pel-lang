from __future__ import annotations

import json
from pathlib import Path

import pytest

from runtime.runtime import main as runtime_main


def _write_json(path: Path, obj: object) -> None:
    path.write_text(json.dumps(obj), encoding="utf-8")


@pytest.mark.unit
def test_runtime_main_writes_output_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    ir = {"model": {"name": "m", "time_horizon": 1, "time_unit": "Month", "nodes": []}}
    ir_path = tmp_path / "m.ir.json"
    out_path = tmp_path / "out.json"
    _write_json(ir_path, ir)

    monkeypatch.setattr(
        "sys.argv",
        [
            "pel-runtime",
            "run",
            str(ir_path),
            "--mode",
            "deterministic",
            "--seed",
            "1",
            "--time-horizon",
            "1",
            "-o",
            str(out_path),
        ],
    )

    runtime_main()

    assert out_path.exists()
    captured = capsys.readouterr()
    assert "Results written" in captured.out


@pytest.mark.unit
def test_runtime_main_prints_to_stdout_when_no_output(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    ir = {"model": {"name": "m", "time_horizon": 1, "time_unit": "Month", "nodes": []}}
    ir_path = tmp_path / "m.ir.json"
    _write_json(ir_path, ir)

    monkeypatch.setattr("sys.argv", ["pel-runtime", "run", str(ir_path), "--time-horizon", "1"])

    runtime_main()

    captured = capsys.readouterr()
    # Should be JSON printed to stdout.
    assert "\"status\"" in captured.out
