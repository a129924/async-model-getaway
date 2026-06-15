---
name: python-pre-commit
description: Configures pre-commit hooks for uv-based Python projects by producing a valid `.pre-commit-config.yaml` with the canonical hook set. Use this when a uv Python project needs pre-commit setup or an existing config needs hooks merged in.
complexity: medium
risk_profile:
  - code_modification
  - external_tooling
inputs:
  - Target project directory path.
  - Whether `.pre-commit-config.yaml` already exists in the project root.
  - Whether pyright strict mode is used in the project (determines optional pyright hook inclusion).
  - Target ruff rev tag from ruff-pre-commit releases (independent of the uv-installed ruff version).
outputs:
  - "`.pre-commit-config.yaml` written to the project root."
  - "Install instructions reported to the user: `uv run pre-commit install` and `uv run pre-commit run --all-files`."
use_when:
  - A uv-based Python project has no `.pre-commit-config.yaml` and needs one created from scratch.
  - An existing `.pre-commit-config.yaml` in a uv project is missing canonical hooks and needs them merged in.
  - The user asks to "set up pre-commit", "add pre-commit hooks", or "configure commit hooks" for a uv Python project.
do_not_use_when:
  - The project does not use uv (pip, poetry, conda, or bare virtualenv).
  - The request is about CI/CD pipeline configuration (GitHub Actions, pre-commit.ci cloud service).
  - The request is about secrets scanning hooks (detect-secrets, gitleaks, etc.).
  - The request asks for `.git/hooks/` file creation rather than `.pre-commit-config.yaml`.
---

# Purpose
Produce a valid `.pre-commit-config.yaml` for a uv-based Python project with the canonical hook set (ruff, ruff-format, pre-commit-hooks). Keep slow hooks (pytest, pyright) on `manual` stage so they never block ordinary commits.

# Trigger / When to use
Use this skill when:
- A uv-based Python project has no `.pre-commit-config.yaml` and needs one created from scratch.
- An existing `.pre-commit-config.yaml` in a uv project is missing canonical hooks and needs them merged in.
- The user asks to "set up pre-commit", "add pre-commit hooks", or "configure commit hooks" for a uv Python project.

Do not use this skill when:
- The project does not use uv (pip, poetry, conda, or bare virtualenv).
- The request is about CI/CD pipeline configuration (GitHub Actions, pre-commit.ci cloud service).
- The request is about secrets scanning hooks (detect-secrets, gitleaks, etc.).
- The request asks for `.git/hooks/` file creation rather than `.pre-commit-config.yaml`.

# Inputs
- The target project directory path.
- Whether a `.pre-commit-config.yaml` already exists.
- Whether pyright strict mode is used in the project (determines whether to include the optional pyright hook).
- The target ruff rev tag from https://github.com/astral-sh/ruff-pre-commit/releases (independent of the uv-installed ruff version).

# Process
1. **Check for existing config** — look for `.pre-commit-config.yaml` in the project root.
   - **New config (file does not exist)**: create a fresh file with the full canonical hook set from `references/hooks-catalog.md`.
   - **Update existing config (file exists)**: read the current file, identify which canonical hooks are missing, and merge them in without overwriting hooks the user has already configured.

2. **Determine ruff rev** — Use the `--ruff-version` default (`v0.15.12`) from `scripts/apply_precommit.py`, or specify a custom tag. The rev comes from [ruff-pre-commit releases](https://github.com/astral-sh/ruff-pre-commit/releases) and is independent of the uv-installed ruff version. Update manually when upgrading.

3. **Decide on optional hooks**:
   - Include the `pytest` hook using `stages: [manual]`. It must never be on the default stage.
   - Include the `pyright` hook with `stages: [manual]` only if the project uses pyright strict mode.

4. **Write the config** — use `scripts/apply_precommit.py` to generate `.pre-commit-config.yaml` from the canonical template:
   ```
   # New config (preview first):
   uv run scripts/apply_precommit.py --dry-run

   # Write (default ruff version v0.15.12):
   uv run scripts/apply_precommit.py

   # Write with a specific older ruff version:
   uv run scripts/apply_precommit.py --ruff-version v0.11.9

   # Overwrite existing config:
   uv run scripts/apply_precommit.py --force
   ```
   If the script is not available, fall back to manually producing `.pre-commit-config.yaml` following the hook structure in `references/hooks-catalog.md`.

   After writing the config, apply the pyright decision from Step 3:
   - **Project uses pyright strict mode**: append the pyright hook block from `references/hooks-catalog.md` to `.pre-commit-config.yaml`.
   - **Project does not use pyright**: no further action needed; the template already omits the pyright hook.

5. **Provide install command** — after writing the file, output the commands the user must run manually:
   ```
   uv run pre-commit install
   uv run pre-commit run --all-files
   ```
   Do not run these commands automatically; report them for the user to execute.

# Examples
- **Positive**: A new uv project has no `.pre-commit-config.yaml`. The skill creates one with ruff, ruff-format, and pre-commit-hooks at default stage, and a pytest hook at `manual` stage. Running `uv run pre-commit run --all-files` exits 0.
- **Negative**: Adding pytest as a default-stage hook so every `git commit` runs the full test suite. This blocks ordinary commits and defeats the purpose of fast pre-commit checks. pytest must always use `stages: [manual]`.

# Outputs
- `.pre-commit-config.yaml` in the project root.
- Install instructions for the user:
  ```
  uv run pre-commit install
  uv run pre-commit run --all-files
  ```

# Boundaries
- Does not cover CI/CD pipeline configuration (GitHub Actions, pre-commit.ci).
- Does not support non-uv toolchains (pip, poetry, conda).
- Does not manage secrets scanning hooks (detect-secrets, gitleaks, etc.).
- Does not write `.git/hooks/` files directly; only produces `.pre-commit-config.yaml`.
- Does not run `uv run pre-commit install` or `uv run pre-commit run --all-files` autonomously; those commands are the user's responsibility.

# Validation

## Required Checks
- Confirm the target project directory is known and reachable before writing any file.
- Confirm the project uses uv (e.g., `pyproject.toml` present, `uv.lock` or `[tool.uv]` section); halt if not.
- Check whether `.pre-commit-config.yaml` already exists to choose create vs. merge path.
- Verify the ruff rev tag format is a valid semver tag (e.g., `v0.15.12`) before embedding it in the config.

## Quality Checks
- After writing `.pre-commit-config.yaml`, confirm it is valid YAML (no syntax errors).
- Confirm all canonical hooks from `references/hooks-catalog.md` are present in the output file.
- Confirm `pytest` hook (if included) uses `stages: [manual]` — never `stages: [commit]`.
- Confirm `pyright` hook (if included) uses `stages: [manual]`.

## On Soft Fail
- Return with a clear explanation of what could not be completed; do not silently produce a partial config.
- If ruff rev cannot be determined, report the issue and fall back to the default rev (`v0.15.12`) only if the user explicitly accepts the default.

# Failure Handling

## Missing Context
- BLOCKED — if the target project directory cannot be determined, stop and ask before proceeding.

## Ambiguous Requirement
- If the existing `.pre-commit-config.yaml` has conflicting hook entries (e.g., duplicate `repo:` blocks for ruff), report the conflict to the user, show both versions, and ask which to keep before merging.
- Do not silently overwrite or discard existing hooks; use `--force` only when the user explicitly requests it.

## Execution Limitation
- If `scripts/apply_precommit.py` is not available, fall back to manually producing `.pre-commit-config.yaml` following `references/hooks-catalog.md`; note the fallback in the output.
- If the ruff rev cannot be fetched from ruff-pre-commit releases (network unavailable), use the default rev (`v0.15.12`) and explicitly note that the user should verify currency before committing.
- If `pre-commit` is not installed in the project environment, output the install instructions and note that `uv run pre-commit install` will fail until the dependency is added.

# Local references
- `reference.md`: index overview pointing to split topic files in `references/`.
- `references/hooks-catalog.md`: canonical YAML blocks for ruff, pre-commit-hooks, pytest, and pyright hooks.
- `references/stage-matrix.md`: stage decision table (`commit` / `manual` / `push`) and manual-run commands.
- `references/uv-run-format.md`: `uv run` + `language: system` entry rationale with correct and incorrect patterns.
- `references/version-pinning.md`: ruff rev alignment strategy, upgrade steps, and pre-commit-hooks rev guidance.
- `examples.md`: detailed scenarios for new setup, config merging, pyright strict projects, and anti-patterns.
- `templates/pre-commit-config.yaml`: canonical pre-commit config template with RUFF_VERSION placeholder; used as the base for new config creation in Process Step 4.
- `scripts/apply_precommit.py`: CLI script that reads `templates/pre-commit-config.yaml`, substitutes `RUFF_VERSION`, and writes `.pre-commit-config.yaml` to the current directory. Supports `--ruff-version`, `--dry-run`, and `--force`.
- `tests/`: Unit tests for `scripts/apply_precommit.py`; verifies version substitution, dry-run (no disk write), force-overwrite, and guard-on-existing-file behaviors.
