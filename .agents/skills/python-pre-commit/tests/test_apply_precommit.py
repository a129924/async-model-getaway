"""Tests for apply_precommit.py script."""
import subprocess
from pathlib import Path

SCRIPT_PATH = (
    Path(__file__).parent.parent / "scripts" / "apply_precommit.py"
)
TEMPLATE_PATH = (
    Path(__file__).parent.parent / "templates" / "pre-commit-config.yaml"
)


def _run(tmp_path: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["uv", "run", str(SCRIPT_PATH), *extra_args],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )


def test_version_substitution(tmp_path: Path) -> None:
    result = _run(tmp_path)
    assert result.returncode == 0
    config = (tmp_path / ".pre-commit-config.yaml").read_text()
    assert "rev: v0.15.12" in config
    assert "RUFF_VERSION" not in config


def test_custom_ruff_version(tmp_path: Path) -> None:
    result = _run(tmp_path, "--ruff-version", "v0.12.0")
    assert result.returncode == 0
    config = (tmp_path / ".pre-commit-config.yaml").read_text()
    assert "rev: v0.12.0" in config


def test_dry_run_no_write(tmp_path: Path) -> None:
    result = _run(tmp_path, "--dry-run")
    assert result.returncode == 0
    assert not (tmp_path / ".pre-commit-config.yaml").exists()
    assert "rev: v0.15.12" in result.stdout


def test_force_overwrites(tmp_path: Path) -> None:
    (tmp_path / ".pre-commit-config.yaml").write_text("old content")
    result = _run(tmp_path, "--force")
    assert result.returncode == 0
    config = (tmp_path / ".pre-commit-config.yaml").read_text()
    assert "rev: v0.15.12" in config
    assert "old content" not in config


def test_no_force_fails_if_exists(tmp_path: Path) -> None:
    (tmp_path / ".pre-commit-config.yaml").write_text("existing content")
    result = _run(tmp_path)
    assert result.returncode != 0
    assert "already exists" in result.stderr or "already exists" in result.stdout


def test_template_has_ruff_placeholder() -> None:
    assert TEMPLATE_PATH.exists()
    assert "RUFF_VERSION" in TEMPLATE_PATH.read_text()
