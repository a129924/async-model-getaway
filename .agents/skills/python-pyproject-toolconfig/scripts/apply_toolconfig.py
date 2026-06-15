# /// script
# requires-python = ">=3.11"
# ///
"""Apply tool configuration sections to pyproject.toml.

Detects existing [tool.*] sections via tomllib and appends only missing ones
from the skill's templates directory. Directly modifies pyproject.toml by
default; use --dry-run to preview changes without writing to disk.
"""
import argparse
import re
import tomllib
from pathlib import Path


def _python_version_type(value: str) -> str:
    """Validate --python-version is in X.Y format."""
    if not re.fullmatch(r"^\d+\.\d+$", value):
        raise argparse.ArgumentTypeError(
            f"--python-version must be in X.Y format, e.g. 3.10 or 3.12. Got: {value!r}"
        )
    return value


def _package_name_type(value: str) -> str:
    """Validate --package-name is a valid importable Python module name."""
    if not re.fullmatch(r"^[a-zA-Z_][a-zA-Z0-9_]*$", value):
        raise argparse.ArgumentTypeError(
            f"--package-name must be a valid importable Python module name "
            f"(snake_case, e.g. mylib or ml_utils). Got: {value!r}"
        )
    return value


def _apply_substitutions(content: str, python_version: str, package_name: str) -> str:
    """Replace template placeholders with actual values.

    Order matters: py${PYTHON_VERSION} must be replaced before ${PYTHON_VERSION}
    so ruff's target-version gets the no-dot form (e.g. py310) while pyright's
    pythonVersion retains the dot form (e.g. 3.10).
    """
    python_version_nodot = python_version.replace(".", "")
    content = re.sub(r"py\$\{PYTHON_VERSION\}", f"py{python_version_nodot}", content)
    content = content.replace("${PYTHON_VERSION}", python_version)
    content = content.replace("${PACKAGE_NAME}", package_name)
    return content


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Append missing [tool.*] sections to pyproject.toml"
    )
    parser.add_argument(
        "--python-version",
        required=True,
        type=_python_version_type,
        help="Python version in X.Y format, e.g. 3.10",
    )
    parser.add_argument(
        "--package-name",
        required=True,
        type=_package_name_type,
        help="Importable package name under src/, e.g. mylib",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Preview sections to be appended without modifying pyproject.toml",
    )
    args = parser.parse_args()

    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        raise FileNotFoundError(f"pyproject.toml not found in {Path.cwd()}")

    with pyproject_path.open("rb") as f:
        data = tomllib.load(f)

    existing_tools: set[str] = set(data.get("tool", {}).keys())

    skill_dir = Path(__file__).parent.parent
    templates_dir = skill_dir / "templates"

    sections_to_append: list[str] = []

    for tmpl_name, section_key in [
        ("toolconfig-ruff.toml.tmpl", "ruff"),
        ("toolconfig-pyright.toml.tmpl", "pyright"),
        ("toolconfig-pytest.toml.tmpl", "pytest"),
    ]:
        if section_key in existing_tools:
            print(f"ℹ️  [tool.{section_key}] already exists — skipping")
            continue

        tmpl_path = templates_dir / tmpl_name
        content = _apply_substitutions(
            tmpl_path.read_text(), args.python_version, args.package_name
        )
        sections_to_append.append(content)
        print(f"✅ Will append [tool.{section_key}]")

    if not sections_to_append:
        print("ℹ️  All tool sections already exist — nothing to append")
        return

    if args.dry_run:
        print("\n# --- DRY RUN preview ---")
        for section in sections_to_append:
            print(section)
        print("# --- DRY RUN: pyproject.toml not modified ---")
        return

    with pyproject_path.open("a") as f:
        f.write("\n" + "\n\n".join(sections_to_append) + "\n")

    print(f"\n✅ Appended {len(sections_to_append)} section(s) to {pyproject_path}")


if __name__ == "__main__":
    main()
