"""Tests for idempotent append behavior."""
import tomllib
import subprocess
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).parent.parent / "scripts" / "apply_toolconfig.py"
)


def _run_script(tmp_path: Path, extra_args: list[str] | None = None) -> subprocess.CompletedProcess:
    args = [
        "uv", "run", str(SCRIPT_PATH),
        "--python-version", "3.10",
        "--package-name", "mylib",
    ]
    if extra_args:
        args.extend(extra_args)
    return subprocess.run(
        args,
        capture_output=True,
        text=True,
        cwd=tmp_path,
    )


def test_idempotent_double_run(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[project]\nname = 'mylib'\n")

    result1 = _run_script(tmp_path)
    assert result1.returncode == 0

    result2 = _run_script(tmp_path)
    assert result2.returncode == 0
    assert "already exists" in result2.stdout

    with pyproject.open("rb") as f:
        data = tomllib.load(f)

    tools = data.get("tool", {})
    assert list(tools.keys()).count("ruff") == 1
    assert list(tools.keys()).count("pyright") == 1
    assert list(tools.keys()).count("pytest") == 1
