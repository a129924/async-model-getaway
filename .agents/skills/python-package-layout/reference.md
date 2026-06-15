# Python package-layout reference

## Default skeleton

```text
repo/
├── pyproject.toml
├── src/
│   └── weather_client/
│       ├── __init__.py
│       ├── api.py
│       ├── cli.py          # only if the package exposes a CLI
│       ├── __main__.py     # only if `python -m weather_client` should work
│       └── data/           # only if runtime package data is shipped
├── tests/
│   └── test_api.py
└── scripts/
    └── smoke.py            # optional repo-local helper, not packaged
```

## Core defaults
- Prefer a `src/` layout for reusable or distributable packages. It reduces false confidence from flat-root execution, where imports and data access may work locally but fail once installed.
- Put importable code under `src/<package_name>/`. The folder name should be the import package name, usually `snake_case`, even if the distribution name in `pyproject.toml` uses hyphens.
- Keep the first draft on a regular package with `__init__.py`. Missing-`__init__.py` namespace-package layouts are an explicit handoff, not the default path here.

## `pyproject.toml` as the package anchor
- Treat `pyproject.toml` as the home for package/distribution metadata and packaging-facing configuration.
- Keep dependencies, optional dependency extras, console entry points, and package-data inclusion rules anchored there.
- This skill prefers one clear package contract in `pyproject.toml` rather than splitting equivalent metadata across legacy files or ad-hoc helper documents.
- The exact backend-specific `tool.*` section still belongs in `pyproject.toml`; keep this skill focused on where package structure and package-facing metadata live, not on choosing the backend.

## Library code versus CLI or scripts
- Reusable behavior belongs in importable package modules under `src/<package_name>/`.
- CLI modules should stay thin: parse arguments, call package code, and return an exit status.
- `__main__.py` is for module execution convenience, not for storing the package's main logic.
- Repo-level `scripts/` files are optional helpers for local operations; they are not a substitute for the packaged library or the official CLI contract.

## Tests relative to packaged code
- Keep tests outside `src/`, usually in `tests/`.
- Tests should import the package by its normal import path, so they exercise the packaged layout rather than sibling-file shortcuts.
- Shared test helpers or fixtures may live under `tests/`; they support the test suite but are not part of the installed package.

## Package data
- Ship runtime data from inside the package tree when the installed package needs it.
- Access packaged data with package-aware resource APIs rather than current-working-directory assumptions.
- Keep test fixtures, sample payloads, and local tooling assets outside the shipped package unless the installed package truly needs them.

## Extras
- Use extras when the package offers optional install-time capabilities such as integrations or heavier feature sets.
- Declare extras in `pyproject.toml`; they belong to the distribution contract, not to an alternate source-tree layout.
- Do not create separate package roots or script-only entrypoints just to model an optional dependency set.

## Split signals
Hand off when the main question becomes:
- public import gateways, `__all__`, or deep-import policy (`python-module-boundaries`)
- `Enum`, dataclass, `ABC`, or `Protocol` choice (`python-model-selection`)
- exception hierarchy or CLI/library error translation (`python-error-handling`)
- repository creation or retrofit execution (`python-project-init-greenfield` or `python-project-retrofit`)
- namespace-package strategy or framework-specific architecture
