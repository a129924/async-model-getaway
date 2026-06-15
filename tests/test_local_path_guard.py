"""Tests for the local path guard hook."""

from __future__ import annotations

from pathlib import Path

from async_model_gateway._repo_hooks.local_path_guard import (
    build_failure_message,
    main,
    scan_paths,
)


def _join(*parts: str) -> str:
    """Build sample content without storing forbidden literals in test source."""
    return "".join(parts)


def test_scan_paths_reports_all_required_rule_types(tmp_path: Path) -> None:
    """Every required local-path pattern should be detected."""
    sample = tmp_path / "sample.txt"
    users_path = _join("/", "Users/", "alice", "/project/config.toml")
    private_path = _join("/", "private/", "tmp/cache.db")
    file_uri = _join("file", "://", "repo/secrets.txt")
    vscode_uri = _join("vscode", "://", "file/workspace/settings.json")
    home_path = _join("/", "home/", "alice/.config/tool")
    windows_path = _join("C:", "\\", "Users", "\\", "Alice", "\\Desktop\\notes.txt")
    sample.write_text(
        "\n".join(
            [
                f"macOS user path: {users_path}",
                f"private temp path: {private_path}",
                f"file uri: {file_uri}",
                f"editor uri: {vscode_uri}",
                f"linux home path: {home_path}",
                f"windows path: {windows_path}",
            ]
        ),
        encoding="utf-8",
    )

    findings = scan_paths([str(sample)])

    assert [(item.line_number, item.rule, item.match) for item in findings] == [
        (1, "posix-users-path", users_path),
        (2, "posix-private-path", private_path),
        (3, "file-uri", file_uri),
        (4, "vscode-uri", vscode_uri),
        (5, "posix-home-path", home_path),
        (6, "windows-users-path", windows_path),
    ]


def test_scan_paths_ignores_clean_relative_content(tmp_path: Path) -> None:
    """Relative paths and ordinary text should not be flagged."""
    sample = tmp_path / "clean.md"
    sample.write_text(
        "Use docs/architecture.md and src/async_model_gateway/__init__.py.\n",
        encoding="utf-8",
    )

    assert scan_paths([str(sample)]) == []


def test_main_prints_filename_line_rule_and_match_for_violations(
    tmp_path: Path, capsys
) -> None:
    """CLI output should include the required violation details."""
    sample = tmp_path / "violations.md"
    users_path = _join("/", "Users/", "bob", "/project/file.txt")
    file_uri = _join("file", "://", "tmp/value")
    sample.write_text(
        "first line\n"
        f"contains {users_path} and {file_uri}\n",
        encoding="utf-8",
    )

    exit_code = main([str(sample)])
    captured = capsys.readouterr()

    assert exit_code == 1
    output_lines = captured.err.strip().splitlines()
    assert output_lines == [
        f"{sample}:2: posix-users-path: {users_path}",
        f"{sample}:2: file-uri: {file_uri}",
    ]
    assert captured.out == ""


def test_build_failure_message_aggregates_each_finding(tmp_path: Path) -> None:
    """The aggregated failure message should preserve per-finding formatting."""
    sample = tmp_path / "violations.txt"
    sample.write_text(_join("vscode", "://", "workspace/item"), encoding="utf-8")

    findings = scan_paths([str(sample)])

    assert build_failure_message(findings) == (
        f"{sample}:1: vscode-uri: {_join('vscode', '://', 'workspace/item')}"
    )


def test_main_skips_binary_and_undecodable_files(tmp_path: Path, capsys) -> None:
    """Binary and non-UTF-8 files should be ignored."""
    binary_file = tmp_path / "image.bin"
    binary_file.write_bytes(b"\x89PNG\x00\x01")
    invalid_text = tmp_path / "broken.txt"
    invalid_text.write_bytes(b"\xff\xfe\xfd")

    exit_code = main([str(binary_file), str(invalid_text)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.out == ""
    assert captured.err == ""


def test_main_accepts_utf8_sig_and_empty_argument_list(tmp_path: Path) -> None:
    """UTF-8-SIG files and empty runs should both succeed cleanly."""
    sample = tmp_path / "clean.txt"
    sample.write_bytes("plain content\n".encode("utf-8-sig"))

    assert main([str(sample)]) == 0
    assert main([]) == 0
