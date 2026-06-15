# /// script
# requires-python = ">=3.11"
# ///
"""Apply pre-commit configuration from skill template.

Reads the canonical template from templates/pre-commit-config.yaml,
substitutes RUFF_VERSION with the specified version string, and writes
the result to .pre-commit-config.yaml in the current working directory.
"""
import argparse
import sys
from pathlib import Path

DEFAULT_RUFF_VERSION = "v0.15.12"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Apply pre-commit config from skill template"
    )
    parser.add_argument(
        "--ruff-version",
        default=DEFAULT_RUFF_VERSION,
        help=f"ruff-pre-commit rev tag (default: {DEFAULT_RUFF_VERSION}). "
             "Update manually from https://github.com/astral-sh/ruff-pre-commit/releases",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Print the resulting config to stdout without writing to disk",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        default=False,
        help="Overwrite .pre-commit-config.yaml if it already exists",
    )
    args = parser.parse_args()

    skill_dir = Path(__file__).parent.parent
    template_path = skill_dir / "templates" / "pre-commit-config.yaml"

    if not template_path.exists():
        print(f"❌ Template not found: {template_path}", file=sys.stderr)
        sys.exit(1)

    content = template_path.read_text()
    content = content.replace("RUFF_VERSION", args.ruff_version)

    target = Path.cwd() / ".pre-commit-config.yaml"

    if args.dry_run:
        print(content)
        return

    if target.exists() and not args.force:
        print(
            f"❌ {target} already exists. Use --force to overwrite.",
            file=sys.stderr,
        )
        sys.exit(1)

    target.write_text(content)
    print(f"✅ Written: {target}")


if __name__ == "__main__":
    main()
