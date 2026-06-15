# Python error-handling examples

Use these examples after `SKILL.md` narrows the task to general Python exception design.

## Root error and topic-level bases

### Define one root error first
```py
class BaseAppError(Exception):
    """Root error for this package."""

class InvalidConfigError(BaseAppError):
    pass

class StartupError(BaseAppError):
    pass

class UserNotFoundError(BaseAppError):
    pass

class UserAlreadyExistsError(BaseAppError):
    pass

class ProjectLoadError(BaseAppError):
    pass

class InvalidUserInputError(BaseAppError):
    pass
```

- A package should have one stable custom root error.
- Later snippets reuse these leaf errors as members of the same custom error family.
- Leaf errors should carry the main business or package meaning.

### Add topic-level bases only when they earn their keep
```py
class BaseAppError(Exception):
    pass

class ConfigError(BaseAppError):
    pass

class InvalidConfigError(ConfigError):
    pass

class MissingConfigError(ConfigError):
    pass
```

- Add a topic-level base only when you need stable grouping or a real catch boundary.
- Do not build deep hierarchies just to look formal.

## Translate once and preserve the cause

### Translate at the first meaningful boundary
```py
def load_settings(text: str) -> Settings:
    try:
        raw = parse_settings(text)
    except ValueError as exc:
        raise InvalidConfigError("settings text is invalid") from exc
    return build_settings(raw)
```

- Catch known low-level failures only when the current layer can add real meaning.
- Use `raise ... from exc` by default.
- Do not re-wrap the same failure again in every caller above this point.

### Avoid repeated wrapping
```py
def start_app(text: str) -> Settings:
    try:
        return load_settings(text)
    except InvalidConfigError as exc:
        raise StartupError("app startup failed") from exc
```

- If `load_settings()` already translated the error into the right semantic type, another wrapper is often noise.
- Re-wrap only when the outer boundary truly adds a new, useful meaning.

## Built-ins vs custom errors

### Keep programmer errors as built-ins
```py
def chunk_size(value: int) -> int:
    if value <= 0:
        raise ValueError("value must be positive")
    return value
```

- Built-ins such as `TypeError` or `ValueError` are appropriate for tiny helpers, misuse, or obvious code bugs.
- These are signals to fix code, not members of the normal business error flow.

### Use custom errors for known business or package failures
```py
def register_user(email: str) -> None:
    if email_already_exists(email):
        raise UserAlreadyExistsError(f"{email} is already registered")
```

- Known business or package failures should default to semantic custom errors under `BaseAppError`.

## Public API boundary

### Prefer exposing one custom error family
```py
def load_project(path: str) -> Project:
    try:
        return _load_project_impl(path)
    except OSError as exc:
        raise ProjectLoadError(f"cannot load project at {path}") from exc
```

- A public package boundary should prefer exposing the package's custom error family for known failures.
- Do not leak arbitrary lower-level built-ins when the package already knows the semantic failure.

## Sentinel returns and benign suppression

### Allow sentinel returns only for explicit optional contracts
```py
def find_user(user_id: str) -> User | None:
    return _users_by_id.get(user_id)
```

- Returning `None` is fine when the API contract is truly "not found" or "optional absence".

### Raise instead of silent fallback for real failures
```py
def parse_port(text: str) -> int:
    try:
        return int(text)
    except ValueError as exc:
        raise InvalidConfigError("port must be an integer") from exc
```

- Do not quietly return `None`, `False`, or an empty value for a known failure.

### Suppress only benign expected exceptions
```py
from contextlib import suppress
from pathlib import Path

def clear_cache_file(path: Path) -> None:
    with suppress(FileNotFoundError):
        path.unlink()
```

- Only ignore exceptions when they are benign, expected, and genuinely safe to ignore.
- Prefer `contextlib.suppress(...)` over `try/except ...: pass` when the intent is deliberate.

### Avoid untyped suppression
```py
def clear_cache_file(path: Path) -> None:
    try:
        path.unlink()
    except:
        pass
```

- Never use untyped `except: pass`.

## Boundary-only broad catch

### Only use `except Exception` at a real process boundary
```py
def main() -> int:
    try:
        run_cli()
    except BaseAppError:
        return 2
    except Exception:
        return 1
    return 0
```

- In ordinary program logic, `except Exception` is a smell.
- Reserve it for clear top-level entrypoints or process boundaries.

## `from None` is rare

```py
def load_user_input(text: str) -> UserId:
    try:
        return parse_user_id(text)
    except ValueError:
        raise InvalidUserInputError("user id is invalid") from None
```

- Do not do this by default.
- Only suppress original context at a clear boundary when hiding low-level detail is intentional and still responsible for debugging.

## Python version scope

- First draft assumes ordinary synchronous single-exception flows.
- Treat `ExceptionGroup`, `except*`, and other Python 3.11+ multi-error features as out of scope.
- Treat `asyncio.CancelledError` and async-specific cancellation behavior as out of scope.
- Mention Python-version limits explicitly so Python 3.10 baselines do not accidentally inherit newer rules.

## Split signals

Stop and hand off to another skill when the main question becomes:

- logging or duplicate-log policy
- retry and recovery strategy
- HTTP, framework, or transport-layer exception mapping
- DDD layer-specific translation rules
- async cancellation or multi-error aggregation
