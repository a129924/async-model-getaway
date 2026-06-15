---
name: python-package-layout
description: Design or review conservative Python package layouts with `src/`, `pyproject.toml`, clear library-vs-CLI placement, and tests that exercise packaged code rather than local-path accidents.
complexity: medium
risk_profile: [ambiguity_sensitive]
inputs:
  - whether the package is library-only, CLI-enabled, or both
  - the import package name and any differing distribution name
  - whether the package ships data files or optional dependency extras
  - where tests should live relative to the packaged code
  - whether the repository currently relies on flat-root execution or ad-hoc scripts
outputs:
  - a review-ready package-layout rule set or design recommendation
  - default placement rules for source packages, tests, CLI entrypoints, package data, and extras
  - local reference and branching examples for normal cases and handoff cases
use_when:
  - designing or reviewing the directory layout of a reusable Python package
  - deciding whether code belongs under src/<package_name>/, tests/, a CLI module, or a non-package script
  - deciding how pyproject.toml should anchor package metadata, entry points, package data, and extras
  - repairing a package layout that works only because local execution happens from the repo root
do_not_use_when:
  - the main question is package public exports, __all__, or deep-import policy; use python-module-boundaries
  - the main question is Enum / dataclass / ABC / Protocol choice; use python-model-selection
  - the main question is custom error hierarchy or exception translation; use python-error-handling
  - the task is to scaffold or retrofit an actual repository end-to-end; use python-project-init-greenfield or python-project-retrofit
  - the preferred path is a namespace-package or no-__init__.py design
---

# Purpose
Choose a clear, distributable layout for an ordinary Python package without drifting into architecture policy or project-bootstrap workflow.

# Trigger / When to use
Use this skill when:
- designing or reviewing the directory layout of a reusable Python package
- deciding whether code belongs under `src/<package_name>/`, `tests/`, a CLI module, or a non-package script
- deciding how `pyproject.toml` should anchor package metadata, entry points, package data, and extras
- repairing a package layout that works only because local execution happens from the repo root

Do not use this skill when:
- the main question is package public exports, `__all__`, or deep-import policy; use `python-module-boundaries`
- the main question is `Enum` / `dataclass` / `ABC` / `Protocol` choice; use `python-model-selection`
- the main question is custom error hierarchy or exception translation; use `python-error-handling`
- the task is to scaffold or retrofit an actual repository end-to-end; use `python-project-init-greenfield` or `python-project-retrofit`
- the preferred path is a namespace-package or no-`__init__.py` design

# Inputs
- whether the package is library-only, CLI-enabled, or both
- the import package name and any differing distribution name
- whether the package ships data files or optional dependency extras
- where tests should live relative to the packaged code
- whether the repository currently relies on flat-root execution or ad-hoc scripts

# Process
1. Confirm the task is about package/distribution structure for a regular package, not about architecture, modeling, or project bootstrap.
2. Default to a `src/` layout for reusable or distributable packages, and put importable code under `src/<package_name>/` with `__init__.py`.
3. Use `pyproject.toml` as the packaging anchor for project metadata, dependencies, extras, entry points, and package-data settings; do not spread the package contract across ad-hoc files unless a tool-specific workflow already owns that choice.
4. Keep reusable library logic inside the package. Keep CLI launchers and ad-hoc scripts thin consumers; if the package exposes a CLI, route it through a console script and/or `__main__.py` that delegates to package code.
5. Put tests outside `src/`, usually under `tests/`, and make them import the packaged code through normal package paths instead of relying on the repo root being on `sys.path`.
6. Treat package data and extras as packaging decisions. Keep shipped data near the package and declare it from `pyproject.toml`; keep extras for optional install-time capabilities rather than as a substitute for package structure.
7. If the question shifts to public import gateways, API composition, error contracts, or repository transformation workflow, hand off to the adjacent skill instead of expanding this one.

# Examples
- Positive: Put reusable code in `src/weather_client/`, keep `pyproject.toml` as the metadata and entry-point anchor, expose `weather-client` through a thin CLI module, and keep tests in `tests/` importing `weather_client`.
- Negative: Leave importable modules at the repo root, mix reusable logic into `scripts/run.py`, let tests pass only because the current working directory is importable, or treat a namespace-package layout as the default first draft.

# Outputs
- a review-ready package-layout rule set or design recommendation
- default placement rules for source packages, tests, CLI entrypoints, package data, and extras
- local reference and branching examples for normal cases and handoff cases

# Validation
Before proceeding, confirm:
- confirm importable code lives under `src/<package_name>/` and the package is regular, with `__init__.py`
- confirm `pyproject.toml` is the single package/distribution anchor for metadata, entry points, extras, and package-data declarations
- confirm reusable logic is not trapped in scripts or `__main__.py`, and tests do not depend on repo-root import accidents

**SOFT FAIL** — ask and wait before continuing:
- Whether the package is library-only, CLI-enabled, or both is unstated → ask before applying default layout rules
- Whether the repository currently uses flat-root execution or ad-hoc scripts is unclear → ask before recommending `src/` migration steps

**BLOCKED** — stop and redirect:
- The main question is package public exports, `__all__`, or deep-import policy → redirect to `python-module-boundaries`
- The task is to scaffold or retrofit an actual repository end-to-end → redirect to `python-project-init-greenfield` or `python-project-retrofit`

# Boundaries
- Do not define package public export policy, `__all__`, or deep-import rules.
- Do not define architecture slicing, bounded contexts, or facade/client composition.
- Do not choose `Enum`, `dataclass`, `ABC`, or `Protocol`.
- Do not define exception hierarchy, translation, or propagation rules.
- Do not turn this into a greenfield scaffold or retrofit execution workflow.
- Do not treat namespace packages as the first-draft default path.

# Failure Handling
- **Missing Context**: if package type (library-only vs CLI-enabled), distribution name, or test placement are unknown, ask once clearly before applying default layout rules.
- **Ambiguous Requirement**: if the stated goal conflicts with package-layout scope (e.g., the task is really about public export policy or end-to-end scaffolding), name the conflict and redirect to the appropriate skill.
- **Execution Limitation**: if the layout involves namespace packages or no-`__init__.py` designs, stop and note the out-of-scope condition.

# Local references
- `reference.md`: default layout skeleton, `pyproject.toml` anchor rules, and split signals
- `examples.md`: branching layout scenarios for library-only, CLI-enabled, package-data, and extras cases
