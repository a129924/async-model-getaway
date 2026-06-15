"""Tests for placeholder substitution logic."""
import re


def _apply_substitutions(content: str, python_version: str, package_name: str) -> str:
    """Replicate the substitution logic from apply_toolconfig.py."""
    python_version_nodot = python_version.replace(".", "")
    content = re.sub(r'py\$\{PYTHON_VERSION\}', f"py{python_version_nodot}", content)
    content = content.replace("${PYTHON_VERSION}", python_version)
    content = content.replace("${PACKAGE_NAME}", package_name)
    return content


def test_ruff_target_version_substitution() -> None:
    content = 'target-version = "py${PYTHON_VERSION}"'
    result = _apply_substitutions(content, "3.10", "mylib")
    assert 'target-version = "py310"' in result


def test_pyright_python_version_substitution() -> None:
    content = 'pythonVersion = "${PYTHON_VERSION}"'
    result = _apply_substitutions(content, "3.10", "mylib")
    assert 'pythonVersion = "3.10"' in result


def test_package_name_substitution() -> None:
    content = 'include = ["src/${PACKAGE_NAME}"]'
    result = _apply_substitutions(content, "3.10", "mylib")
    assert 'include = ["src/mylib"]' in result


def test_no_placeholders_remaining(tmp_path) -> None:
    content = 'target-version = "py${PYTHON_VERSION}"\npythonVersion = "${PYTHON_VERSION}"\ninclude = ["src/${PACKAGE_NAME}"]'
    result = _apply_substitutions(content, "3.12", "my_package")
    assert "${" not in result
