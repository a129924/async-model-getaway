"""Tests for --python-version and --package-name input validation."""
import subprocess
from pathlib import Path

SCRIPT_PATH = (
    Path(__file__).parent.parent / "scripts" / "apply_toolconfig.py"
)


def _run(tmp_path: Path, python_version: str, package_name: str) -> subprocess.CompletedProcess:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nname = "test"\n')
    return subprocess.run(
        ["uv", "run", str(SCRIPT_PATH), "--python-version", python_version, "--package-name", package_name],
        capture_output=True,
        text=True,
        cwd=tmp_path,
    )


def test_invalid_python_version_py311(tmp_path: Path) -> None:
    result = _run(tmp_path, "py311", "mylib")
    assert result.returncode != 0
    assert "X.Y" in result.stderr or "X.Y" in result.stdout


def test_invalid_python_version_nodot(tmp_path: Path) -> None:
    result = _run(tmp_path, "311", "mylib")
    assert result.returncode != 0


def test_invalid_package_name_kebab(tmp_path: Path) -> None:
    result = _run(tmp_path, "3.10", "my-lib")
    assert result.returncode != 0
    assert "snake_case" in result.stderr or "snake_case" in result.stdout


def test_valid_inputs_pass(tmp_path: Path) -> None:
    result = _run(tmp_path, "3.10", "mylib")
    assert result.returncode == 0


def test_dry_run_does_not_modify_file(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    original = '[project]\nname = "test"\n'
    pyproject.write_text(original)
    result = subprocess.run(
        [
            "uv", "run", str(SCRIPT_PATH),
            "--python-version", "3.10",
            "--package-name", "mylib",
            "--dry-run",
        ],
        capture_output=True,
        text=True,
        cwd=tmp_path,
    )
    assert result.returncode == 0
    assert "DRY RUN" in result.stdout
    assert pyproject.read_text() == original
