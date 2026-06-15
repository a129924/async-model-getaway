# Python module-boundaries examples

Use these examples after `SKILL.md` narrows the task to regular Python package and module boundaries.

## Package gateway and explicit re-exports

### Keep the public surface in `__init__.py`
```py
# package/__init__.py
from .service import UserService
from .types import User

__all__ = ["User", "UserService"]
```

```py
# package/service.py
from .types import User

__all__ = ["UserService"]


class UserService:
    ...
```

- The package exposes one clear import surface.
- External callers can use `from package import UserService`.
- The public module and the package gateway both declare exports explicitly.

### Avoid forcing deep imports as the normal public path
```py
from package.internal.models.user import User
```

- This leaks implementation structure into the caller contract.
- If `User` is public, re-export it through the package gateway instead.

## Internal modules and boundary leaks

### Underscore modules are internal to outside callers
```py
# package/_adapter.py
__all__ = ["build_adapter"]


def build_adapter() -> object:
    ...
```

```py
# package/service.py
from ._adapter import build_adapter

__all__ = ["UserService"]


class UserService:
    ...
```

- Same-package code may import underscore modules directly.
- The underscore path still signals "not public" to outside packages.

### Do not cross into another subpackage's internal module
```py
from app.db._internal import connection_state
```

- Crossing a clearer subpackage boundary into an underscore module is a contract leak.
- Go through that subpackage's public API instead.

## Relative vs absolute imports

### Relative import for close internal collaboration
```py
from ._internal import build_parser
from .types import ParsedConfig
```

- Relative imports make local implementation coupling obvious.
- This is the preferred shape inside one close module group.

### Absolute import across clearer subpackage boundaries
```py
from app.auth.service import AuthService
```

- Absolute imports make cross-boundary dependencies easier to trace.
- Prefer this to deep multi-level relative imports such as `from ...auth.service import AuthService`.

## `__all__` even for small public modules

### A tiny public module should still declare exports
```py
__all__ = ["slugify"]


def slugify(value: str) -> str:
    return value.lower().replace(" ", "-")
```

- Public contract size does not change the need for explicit exports.
- Even a one-symbol public module should make intent visible.

### Do not export underscore names
```py
__all__ = ["_normalize_user", "create_user"]
```

- Underscore names should stay out of the public surface.
- Keep internal helpers internal.

## Ban wildcard imports

### Use explicit or namespace imports
```py
from package import UserService
import package.service as service_module
```

- Every imported name stays traceable.
- This complements the explicit export contract.

### Avoid `from x import *`
```py
from package import *
```

- This hides name origins and weakens reviewability.
- The ban applies in production code, scripts, and tests.

## Import-time side effects

### Keep imports declarative
```py
__all__ = ["bootstrap"]


def bootstrap() -> None:
    load_settings()
    open_connection_pool()
```

- Importing the module is harmless.
- Expensive or stateful work happens only when explicitly called.

### Avoid runtime work on import
```py
load_settings()
open_connection_pool()
start_background_worker()
```

- This makes module import non-idempotent and risky.
- Tests and tooling should be able to import the module safely.

## Circular imports

### Break the cycle by extracting shared contracts
```py
# package/types.py
__all__ = ["UserId"]

UserId = str
```

```py
# package/auth.py
from .types import UserId

__all__ = ["authenticate"]
```

```py
# package/profiles.py
from .types import UserId

__all__ = ["load_profile"]
```

- Shared low-level contracts moved into a neutral module.
- The dependency graph becomes directional again.

### Type-only cycles may use `TYPE_CHECKING`
```py
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .service import UserService
```

- Use this only when the cycle exists for annotations, not runtime behavior.

### Function-local import is the last resort
```py
def render_report() -> str:
    # Last resort until boundary refactor removes the cycle.
    from .formatting import render_text

    return render_text("report")
```

- This should not become the normal fix.
- Keep a comment that explains why refactoring was deferred.

## Plugin and registry patterns

### Prefer explicit setup or lazy discovery
```py
class PluginRegistry:
    def load_plugins(self) -> None:
        ...


def bootstrap_plugins(registry: PluginRegistry) -> None:
    registry.load_plugins()
```

- Plugin loading stays explicit and controlled.
- Importing the module does not silently mutate global state.

### Avoid import-to-register by default
```py
from .plugins.user_plugin import register_plugin

register_plugin()
```

- Hidden import-time registration makes bootstrap order harder to reason about.
- Use this only when a framework truly requires it and the module documents that constraint.

## Script and CLI entrypoints

### Keep CLI modules thin and safe to import
```py
from app.cli.runner import run_cli


def main() -> int:
    return run_cli()


if __name__ == "__main__":
    raise SystemExit(main())
```

- The file acts as an entrypoint, not a reusable public API module.
- Importing it does not immediately run the program.

### Avoid embedding reusable business logic in the entrypoint
```py
def main() -> int:
    records = query_database()
    normalized = normalize_records(records)
    write_report(normalized)
    return 0


main()
```

- The entrypoint now mixes orchestration with reusable logic and import-time execution.
- Move reusable work into package modules and keep the entrypoint thin.

## Test support modules

### Reusable test helpers should still have boundaries
```py
# tests/helpers/__init__.py
from .factories import make_user

__all__ = ["make_user"]
```

```py
# tests/helpers/factories.py
__all__ = ["make_user"]


def make_user() -> object:
    ...
```

- Shared test support code should stay organized like other reusable modules.
- Deep imports between tests become unnecessary.

### Individual test files do not need `__all__`
```py
def test_login_success() -> None:
    ...
```

- A `test_*.py` file is an execution-oriented consumer, not a public API provider.

## Namespace packages are out of scope

### Flag missing `__init__.py` as a first-draft handoff
```text
pkg/
├── auth/
│   └── service.py
└── users/
    └── service.py
```

- Without `__init__.py`, the first-draft gateway rules do not apply cleanly.
- Suggest converting to a regular package if explicit re-exports and gateway control are desired.

## Deprecated re-exports

### Allow only explicit temporary bridges
```py
from warnings import warn

# package/__init__.py
from .service import UserService


# Deprecated bridge: remove in v2.0; use package.UserService instead.
def LegacyUserService(*args: object, **kwargs: object) -> UserService:
    warn(
        "package.LegacyUserService is deprecated and will be removed in v2.0; use package.UserService",
        DeprecationWarning,
        stacklevel=2,
    )
    return UserService(*args, **kwargs)

__all__ = ["UserService"]
```

- The new public path already exists.
- The deprecated bridge is clearly marked, warns, and includes a removal plan.
- It is intentionally excluded from `__all__` so new callers do not treat it as part of the fresh intended surface.

### Avoid silent permanent baggage
```py
# package/__init__.py
from .service import UserService as LegacyUserService
from .service import UserService

__all__ = ["LegacyUserService", "UserService"]
```

- This invites new callers onto the deprecated path.
- Keep migration bridges explicit, temporary, and easy to remove.

## Split signals

Stop and hand off to another skill when the main question becomes:

- DDD layering or architecture-specific package boundaries
- packaging/distribution layout, namespace-package strategy, or release structure
- strict typing syntax for imports and exported types
- API-signature details inside a function or method rather than module/package surface
