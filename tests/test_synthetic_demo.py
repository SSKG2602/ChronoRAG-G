import ast
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "examples/synthetic/run_demo.py"


def _run_demo():
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(ROOT / "src")
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, str(DEMO)],
        cwd=ROOT,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )


def test_demo_is_deterministic_and_successful():
    first = _run_demo()
    second = _run_demo()
    assert first.returncode == second.returncode == 0
    assert first.stdout == second.stdout == "PUBLIC_SYNTHETIC_DEMO_SUCCESS\n"
    assert first.stderr == second.stderr == ""


def test_demo_has_no_network_imports():
    tree = ast.parse(DEMO.read_text())
    imported = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert imported.isdisjoint({"socket", "http", "urllib", "requests"})
