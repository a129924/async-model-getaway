# Stage Decision Matrix

## Stage reference table

| Stage | When it runs | Use for |
|-------|-------------|---------|
| `commit` (default) | On every `git commit` | Fast checks: linting, formatting, file hygiene (ruff, ruff-format, pre-commit-hooks) |
| `manual` | Only when explicitly called via `uv run pre-commit run --hook-stage manual [hook-id]` | Slow checks: test suites (pytest), full type checking (pyright) |
| `push` | On `git push` | Medium-speed checks you want before pushing but not on every local commit |

## Decision rule

- If a hook takes more than ~3 seconds on average, put it on `manual` or `push`.
- If a hook modifies files (autofix), keep it at `commit` stage so fixes are ready to stage.
- Default (unspecified) `stages` resolves to `[commit]` in pre-commit ≥ 3.x. Always be explicit for hooks that should not run on commit.

## Running manual-stage hooks

```bash
# Run all manual-stage hooks
uv run pre-commit run --hook-stage manual

# Run a specific manual-stage hook
uv run pre-commit run --hook-stage manual pytest
uv run pre-commit run --hook-stage manual pyright
```
