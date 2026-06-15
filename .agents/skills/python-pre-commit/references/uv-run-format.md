# uv run Entry Format

All local hooks in a uv project must use:
```yaml
entry: uv run <command>
language: system
```

## Why `language: system`

pre-commit normally creates an isolated virtualenv for each hook repo. `language: system` prevents pre-commit from creating that separate hook virtualenv. `entry: uv run` is then responsible for running the command inside the project's uv-managed environment. Together, `language: system` stops pre-commit from taking over environment management, and `entry: uv run` ensures the hook sees the correct dependencies.

## Why `uv run` instead of direct binary path

- `uv run <cmd>` activates the uv virtual environment automatically, ensuring the correct Python and all project dependencies are available.
- Direct binary paths (`.venv/bin/pytest`) are fragile and break when the venv is recreated.
- `python -m pytest` without `uv run` does not guarantee the uv venv is active.

## Correct

```yaml
entry: uv run pytest
language: system
```

## Incorrect

```yaml
entry: python -m pytest
language: python         # creates a separate pre-commit venv
```

```yaml
entry: .venv/bin/pytest  # fragile absolute path
language: system
```
