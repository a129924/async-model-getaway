# Version Pinning Strategy

## ruff-pre-commit rev

**Goal**: keep the pre-commit hook version aligned with the intended ruff version to avoid split-brain lint results between the hook and CI.

| Approach | When to use | Trade-off |
|----------|------------|-----------|
| Check ruff-pre-commit releases | Always | Authoritative source; requires a manual lookup step |
| Pin to current latest stable | Greenfield project | Easy to set up; update when upgrading ruff |

**Source of truth**: https://github.com/astral-sh/ruff-pre-commit/releases  
The `rev` for `ruff-pre-commit` is independent of the ruff version resolved by `uv`. Always derive the rev tag from the ruff-pre-commit releases page, not from `pyproject.toml` or the locally-installed ruff version.

**Updating** (when upgrading ruff):
1. Update the ruff version constraint in `pyproject.toml`.
2. Run `uv sync` to resolve the new version.
3. Check https://github.com/astral-sh/ruff-pre-commit/releases to find the matching rev tag.
4. Update `rev` in `.pre-commit-config.yaml` to the new tag (e.g., `v0.12.0`).
5. Run `uv run pre-commit run --all-files` to validate.

## pre-commit-hooks rev

`pre-commit-hooks` is stable and infrequently breaking. Pin to `v4.6.0` unless a specific newer hook is needed. Update lazily when the project upgrades its Python or pre-commit version.
