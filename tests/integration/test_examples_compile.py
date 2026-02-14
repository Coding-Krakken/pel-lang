from pathlib import Path

import pytest

from compiler.compiler import PELCompiler


@pytest.mark.integration
def test_saas_subscription_example_compiles(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    source = repo_root / "examples" / "saas_subscription.pel"
    output = tmp_path / "saas_subscription.ir.json"

    compiler = PELCompiler(verbose=False)
    ir = compiler.compile(source, output)

    assert output.exists()
    assert ir["model"]["name"] == "saas_subscription"
