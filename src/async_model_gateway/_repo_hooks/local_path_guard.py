"""Prevent committing machine-local paths into the repository."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
import re
import sys


@dataclass(frozen=True)
class PathRule:
    """A single local-path detection rule."""

    name: str
    pattern: re.Pattern[str]


@dataclass(frozen=True)
class Finding:
    """A detected local-path violation."""

    path: Path
    line_number: int
    rule: str
    match: str

    def format(self) -> str:
        """Render the finding in a pre-commit-friendly format."""
        return f"{self.path}:{self.line_number}: {self.rule}: {self.match}"


def _join(*parts: str) -> str:
    """Assemble pattern fragments without embedding full sample paths in source."""
    return "".join(parts)


POSIX_MATCH_BODY = r"[^\s'\"<>()\[\]{}]+"
URI_MATCH_BODY = r"[^\s'\"<>()\[\]{}]+"
WINDOWS_MATCH_BODY = r"[^\r\n\"'<>]+"

RULES: tuple[PathRule, ...] = (
    PathRule(
        "posix-users-path",
        re.compile(_join(re.escape("/"), re.escape("Users/"), POSIX_MATCH_BODY)),
    ),
    PathRule(
        "posix-private-path",
        re.compile(_join(re.escape("/"), re.escape("private/"), POSIX_MATCH_BODY)),
    ),
    PathRule(
        "file-uri",
        re.compile(_join(re.escape("file"), re.escape("://"), URI_MATCH_BODY)),
    ),
    PathRule(
        "vscode-uri",
        re.compile(_join(re.escape("vscode"), re.escape("://"), URI_MATCH_BODY)),
    ),
    PathRule(
        "posix-home-path",
        re.compile(_join(re.escape("/"), re.escape("home/"), POSIX_MATCH_BODY)),
    ),
    PathRule(
        "windows-users-path",
        re.compile(
            _join(
                r"[A-Za-z]:",
                r"[\\/]+",
                re.escape("Users"),
                r"[\\/]+",
                WINDOWS_MATCH_BODY,
            )
        ),
    ),
)


def _decode_text(raw_bytes: bytes) -> str | None:
    """Decode staged text content or return None when it should be skipped."""
    if b"\x00" in raw_bytes:
        return None

    for encoding in ("utf-8-sig", "utf-8"):
        try:
            return raw_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue

    return None


def _scan_file(path: Path) -> list[Finding]:
    """Scan a single file for local path violations."""
    content = _decode_text(path.read_bytes())
    if content is None:
        return []

    findings: list[Finding] = []
    for line_number, line in enumerate(content.splitlines(), start=1):
        for rule in RULES:
            for match in rule.pattern.finditer(line):
                findings.append(
                    Finding(
                        path=path,
                        line_number=line_number,
                        rule=rule.name,
                        match=match.group(0),
                    )
                )

    return findings


def scan_paths(paths: Iterable[str]) -> list[Finding]:
    """Scan every provided path and collect local path findings."""
    findings: list[Finding] = []
    for raw_path in paths:
        findings.extend(_scan_file(Path(raw_path)))
    return findings


def build_failure_message(findings: Sequence[Finding]) -> str:
    """Build a readable aggregated failure message for pre-commit output."""
    return "\n".join(finding.format() for finding in findings)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the local-path guard as a CLI entrypoint."""
    args = list(sys.argv[1:] if argv is None else argv)
    findings = scan_paths(args)
    if not findings:
        return 0

    print(build_failure_message(findings), file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
