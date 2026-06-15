"""Tests for section existence detection logic."""
import tomllib
from pathlib import Path


def _write_pyproject(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "pyproject.toml"
    p.write_text(content)
    return p


def test_existing_ruff_section_detected(tmp_path: Path) -> None:
    pyproject = _write_pyproject(tmp_path, "[tool.ruff]\nline-length = 80\n")
    with pyproject.open("rb") as f:
        data = tomllib.load(f)
    existing = set(data.get("tool", {}).keys())
    assert "ruff" in existing


def test_missing_ruff_section_detected(tmp_path: Path) -> None:
    pyproject = _write_pyproject(tmp_path, "[project]\nname = 'mylib'\n")
    with pyproject.open("rb") as f:
        data = tomllib.load(f)
    existing = set(data.get("tool", {}).keys())
    assert "ruff" not in existing


def test_all_sections_present(tmp_path: Path) -> None:
    content = "[tool.ruff]\n[tool.pyright]\n[tool.pytest.ini_options]\n"
    pyproject = _write_pyproject(tmp_path, content)
    with pyproject.open("rb") as f:
        data = tomllib.load(f)
    existing = set(data.get("tool", {}).keys())
    assert existing >= {"ruff", "pyright", "pytest"}


def test_empty_pyproject_no_tools(tmp_path: Path) -> None:
    pyproject = _write_pyproject(tmp_path, "[project]\nname = 'mylib'\n")
    with pyproject.open("rb") as f:
        data = tomllib.load(f)
    existing = set(data.get("tool", {}).keys())
    assert len(existing) == 0
