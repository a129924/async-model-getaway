# python-pre-commit — Examples

## Scenario 1: New uv project, minimal hooks from scratch

**Starting point**: A freshly initialised uv project, no `.pre-commit-config.yaml` exists.

**Input signals**:
- No `.pre-commit-config.yaml` in the project root.
- `pyproject.toml` contains `ruff>=0.11.0` under `[dependency-groups]`, `[project.dependencies]`, or `[project.optional-dependencies]`.
- Project does not use pyright strict mode.

**How to generate** (using the skill script):
```
# Preview first:
uv run scripts/apply_precommit.py --dry-run

# Write with default ruff version (v0.15.12):
uv run scripts/apply_precommit.py

# Write with a specific ruff version (e.g., an older tag):
uv run scripts/apply_precommit.py --ruff-version v0.11.9
```

**Correct output** — `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.15.12
    hooks:
      - id: ruff
        args: ["--fix"]
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-merge-conflict
      - id: check-added-large-files
        args: ["--maxkb=500"]

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

**Install commands provided to user**:
```
uv run pre-commit install
uv run pre-commit run --all-files
```

**Expected outcome**: `uv run pre-commit run --all-files` exits 0. Ordinary `git commit` runs ruff, ruff-format, and pre-commit-hooks instantly. pytest only runs when explicitly invoked via `uv run pre-commit run --hook-stage manual`.

---

## Scenario 2: Existing `.pre-commit-config.yaml` — merge new hooks without overwriting

**Starting point**: A uv project that already has a hand-authored `.pre-commit-config.yaml`.

**Existing config**:
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.9.0
    hooks:
      - id: ruff
      - id: ruff-format

  - repo: local
    hooks:
      - id: my-custom-check
        name: my-custom-check
        entry: uv run python scripts/check.py
        language: system
        pass_filenames: false
```

**Merge decision**:
- `ruff` and `ruff-format` already present → update `rev` to the matching tag from https://github.com/astral-sh/ruff-pre-commit/releases; do not remove the existing `ruff` entry.
- `my-custom-check` is user-defined → leave untouched.
- Missing canonical hooks → add `pre-commit-hooks` block and `pytest` (manual stage).

**Correct merged output**:
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.11.9   # updated from ruff-pre-commit releases
    hooks:
      - id: ruff
        args: ["--fix"]   # added --fix per canonical spec
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0   # new block added
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-merge-conflict
      - id: check-added-large-files
        args: ["--maxkb=500"]

  - repo: local
    hooks:
      - id: my-custom-check
        name: my-custom-check
        entry: uv run python scripts/check.py
        language: system
        pass_filenames: false

      - id: pytest
        name: pytest
        entry: uv run pytest
        language: system
        types: [python]
        stages: [manual]
        pass_filenames: false
        always_run: true
```

**What must NOT happen**:
- Do not silently discard `my-custom-check` or any other user-configured hook.
- Do not create a completely new file, overwriting the existing one without merging.
- Do not downgrade an existing `rev` that is already newer than the canonical default.

---

## Scenario 3: Project with pyright strict mode — add pyright as manual stage

**Starting point**: A uv project that runs `pyright` in strict mode (e.g., `pyproject.toml` contains `[tool.pyright]` with `typeCheckingMode = "strict"` or the project CI runs pyright).

**Extra hook to include** (appended to the `local` block):
```yaml
      - id: pyright
        name: pyright
        entry: uv run pyright
        language: system
        types: [python]
        stages: [manual]
        pass_filenames: false
```

**When to include pyright**:
- User explicitly asks for pyright integration.
- `pyproject.toml` contains a `[tool.pyright]` section.
- The project README or CI config references pyright strict checks.

**When NOT to include pyright**:
- Project uses mypy exclusively.
- User has not mentioned type checking in the request.

**Run pyright manually**:
```
uv run pre-commit run --hook-stage manual pyright
```

**Why manual stage**: pyright on a large project can take 30–120 seconds. Blocking every commit with that latency creates friction without increasing safety; it belongs in CI or on-demand checks.

---

## Anti-pattern section

### Anti-pattern 1: pytest as a default-stage hook

**Bad config**:
```yaml
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: uv run pytest
        language: system
        types: [python]
        pass_filenames: false
        always_run: true
        # stages not specified — defaults to [commit]
```

**Problem**: Every `git commit` runs the entire test suite. On a project with 500+ tests, this adds 30–120+ seconds to each commit. Contributors stop committing frequently, undermining iterative development and making diffs larger.

**Correct fix**: Add `stages: [manual]` so pytest only runs when explicitly requested:
```yaml
        stages: [manual]
```

---

### Anti-pattern 2: pyright as a default-stage hook

**Bad config**:
```yaml
      - id: pyright
        name: pyright
        entry: uv run pyright
        language: system
        types: [python]
        # stages not specified — runs on every commit
```

**Problem**: Type checking the entire project on every commit is slow. pyright can take 30–120 seconds on a large codebase. Use `stages: [manual]` and run it in CI or on demand.

---

### Anti-pattern 3: Using `python` instead of `uv run` for local hooks

**Bad config**:
```yaml
      - id: pytest
        entry: python -m pytest
        language: python
```

**Problem**: `language: python` creates a separate pre-commit-managed virtualenv that is separate from the uv project environment. This causes the hook to fail if the project's packages are not installed in that separate env. Always use `entry: uv run pytest` with `language: system` so the hook runs inside the uv-managed environment.

---

### Anti-pattern 4: Mismatched ruff rev

**Bad config**:
```yaml
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.0   # pinned to old version while pyproject.toml has ruff>=0.11.0
```

**Problem**: Different ruff versions may produce different lint results. The pre-commit hook may pass while the CI ruff check fails (or vice versa). Always align the `rev` with the matching tag from ruff-pre-commit releases (https://github.com/astral-sh/ruff-pre-commit/releases).
