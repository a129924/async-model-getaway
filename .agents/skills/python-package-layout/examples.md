# Python package-layout examples

Use these examples after `SKILL.md` narrows the task to conservative package layout for a regular distributable package.

## Library-only package

### Prefer
```text
repo/
├── pyproject.toml
├── src/
│   └── weather_client/
│       ├── __init__.py
│       ├── api.py
│       └── models.py
└── tests/
    ├── test_api.py
    └── test_models.py
```

```toml
[project]
name = "weather-client"

# Configure the chosen build backend here to package from `src/`.
```

- Importable code stays under `src/weather_client/`.
- The distribution name may use hyphens while the import package uses underscores.
- Tests exercise the package through its normal import path.

### Avoid
```text
repo/
├── pyproject.toml
├── weather_client.py
├── models.py
└── test_weather_client.py
```

- Flat-root imports can hide missing packaging configuration.
- Installed-package behavior is harder to verify when code and tests sit at the repo root.

## CLI-enabled package

### Prefer
```text
repo/
├── pyproject.toml
├── src/
│   └── weather_client/
│       ├── __init__.py
│       ├── cli.py
│       ├── service.py
│       └── __main__.py
└── tests/
    └── test_cli.py
```

```toml
[project.scripts]
weather-client = "weather_client.cli:main"
```

```py
# src/weather_client/__main__.py
from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
```

- `cli.py` is a thin launcher that delegates to reusable package code.
- `__main__.py` stays tiny and mirrors the console entry point.
- The package can support both `weather-client` and `python -m weather_client` without duplicating logic.

### Avoid
```text
repo/
├── bin/weather-client
└── src/weather_client/
    ├── __init__.py
    └── service.py
```

```py
# bin/weather-client
from weather_client.service import fetch_weather

records = fetch_weather()
print(records)
```

- The official CLI contract is buried in a repo-local script.
- Reusable behavior and execution flow are mixed together.
- Installed users do not get a clearly declared entry point from package metadata.

## Package data

### Prefer
```text
src/weather_client/
├── __init__.py
├── data/
│   └── report.txt
└── reports.py
```

```py
from importlib.resources import files

TEMPLATE_TEXT = files("weather_client").joinpath("data/report.txt").read_text()
```

- Runtime data ships with the package.
- Access goes through package-aware resource loading instead of relative cwd paths.

### Avoid
```text
repo/
├── assets/report.txt
└── src/weather_client/reports.py
```

```py
from pathlib import Path

TEMPLATE_TEXT = Path("assets/report.txt").read_text()
```

- The code now depends on where the command is run from.
- Repo assets are not automatically part of the installed package contract.

## Optional extras

### Prefer
```toml
[project.optional-dependencies]
cli = ["rich>=13"]
postgres = ["psycopg[binary]>=3.2"]
```

- Extras express optional install surfaces in the package metadata.
- The base package layout stays the same whether an extra is installed or not.

### Avoid
```text
src/
├── weather_client/
└── weather_client_postgres/
```

- Separate package roots are not the default way to model optional dependencies.
- This changes import structure when the real question is just optional installation.

## Tests and local-path accidents

### Prefer
```text
repo/
├── pyproject.toml
├── src/example_pkg/__init__.py
└── tests/test_example_pkg.py
```

```py
from example_pkg import __version__
```

- The test imports the installed package path.
- A `src/` layout helps expose missing packaging config early.

### Avoid
```py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import example_pkg
```

- Path surgery hides package-layout problems.
- The suite is validating the repo checkout, not the distributable package shape.

## Split signals

Hand off when the main question becomes:
- what `src/weather_client/__init__.py` should re-export or hide (`python-module-boundaries`)
- which model type should live in `models.py` (`python-model-selection`)
- how the CLI should translate package exceptions into exit codes (`python-error-handling`)
- how to physically retrofit an existing repository to this layout (`python-project-retrofit`)
- whether a namespace-package layout should replace the regular-package default
