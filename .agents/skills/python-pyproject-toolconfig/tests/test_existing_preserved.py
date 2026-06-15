"""Tests that existing tool sections are not overwritten."""
import subprocess
import tomllib
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).parent.parent / "scripts" / "apply_toolconfig.py"
)


def test_existing_ruff_preserved(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nname = "mylib"\n\n[tool.ruff]\nline-length = 80\n')

    result = subprocess.run(
        ["uv", "run", str(SCRIPT_PATH), "--python-version", "3.10", "--package-name", "mylib"],
        capture_output=True,
        text=True,
        cwd=tmp_path,
    )
    assert result.returncode == 0

    with pyproject.open("rb") as f:
        data = tomllib.load(f)

    assert data["tool"]["ruff"]["line-length"] == 80


def test_partial_existing_appends_missing(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nname = "mylib"\n\n[tool.ruff]\nline-length = 80\n')

    result = subprocess.run(
        ["uv", "run", str(SCRIPT_PATH), "--python-version", "3.10", "--package-name", "mylib"],
        capture_output=True,
        text=True,
        cwd=tmp_path,
    )
    assert result.returncode == 0

    with pyproject.open("rb") as f:
        data = tomllib.load(f)

    assert "pyright" in data["tool"]
    assert "pytest" in data["tool"]
    assert data["tool"]["ruff"]["line-length"] == 80
