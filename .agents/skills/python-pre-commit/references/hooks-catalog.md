# Hooks Catalog

Canonical YAML blocks for all four supported hook types. Copy these blocks into `.pre-commit-config.yaml`.

## ruff-pre-commit

| Property | Value |
|----------|-------|
| Repo URL | `https://github.com/astral-sh/ruff-pre-commit` |
| Hooks | `ruff` (lint + autofix), `ruff-format` (formatter) |
| Canonical rev | Use the tag from https://github.com/astral-sh/ruff-pre-commit/releases — independent of the uv-installed ruff version. |
| Example rev | `v0.15.12` (update to current stable at config creation time) |
| Version source | Manual update from https://github.com/astral-sh/ruff-pre-commit/releases — version is independent of `uv run ruff --version` |

**Canonical block**:
```yaml
- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: v0.15.12
  hooks:
    - id: ruff
      args: ["--fix"]
    - id: ruff-format
```

> **Version note**: The `rev` for `ruff-pre-commit` is independent of the ruff version installed by uv. Always check [ruff-pre-commit releases](https://github.com/astral-sh/ruff-pre-commit/releases) and update manually when upgrading. The default used by `scripts/apply_precommit.py` is `v0.15.12`.

- Always add `args: ["--fix"]` to `ruff` so autofix runs on staged files before the commit is blocked.
- Run `ruff-format` after `ruff` (pre-commit runs hooks in declaration order).

## pre-commit-hooks

| Property | Value |
|----------|-------|
| Repo URL | `https://github.com/pre-commit/pre-commit-hooks` |
| Canonical rev | `v4.6.0` (stable; update when project needs a newer feature) |

**Canonical block**:
```yaml
- repo: https://github.com/pre-commit/pre-commit-hooks
  rev: v4.6.0
  hooks:
    - id: trailing-whitespace
    - id: end-of-file-fixer
    - id: check-yaml
    - id: check-merge-conflict
    - id: check-added-large-files
      args: ["--maxkb=500"]
```

- `trailing-whitespace` and `end-of-file-fixer` keep files clean with zero config.
- `check-yaml` catches syntax errors in YAML files before commit.
- `check-merge-conflict` prevents accidental commits with unresolved conflict markers.
- `check-added-large-files` with `--maxkb=500` blocks binary blobs and generated files from entering the repo.

## pytest (local, manual stage)

```yaml
- repo: local
  hooks:
    - id: pytest
      name: pytest
      entry: uv run pytest
      language: system
      types: [python]
      stages: [manual]
      pass_filenames: false
      always_run: true
```

- **Always** `stages: [manual]`. Never omit this field or set it to `[commit]`.
- `language: system` uses the uv-managed environment rather than a separate pre-commit venv.
- `pass_filenames: false` + `always_run: true` ensures the full suite runs when manually triggered.

## pyright (local, manual stage — optional)

```yaml
- repo: local
  hooks:
    - id: pyright
      name: pyright
      entry: uv run pyright
      language: system
      types: [python]
      stages: [manual]
      pass_filenames: false
```

- Include only when the project uses pyright (indicated by `[tool.pyright]` in `pyproject.toml` or explicit user request).
- **Always** `stages: [manual]`.
