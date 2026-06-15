---
name: python-module-boundaries
description: Design or review regular Python package and module boundaries with explicit public surfaces, disciplined re-exports, safe imports, and clear internal-module contracts.
complexity: medium
risk_profile: [ambiguity_sensitive]
inputs:
  - whether the package is a regular package with `__init__.py`
  - the intended public import paths
  - which modules are implementation detail only
  - whether imports stay within one local scope or cross a clearer subpackage boundary
  - whether the package has import-time setup, compatibility re-exports, or circular dependencies
outputs:
  - a review-ready Python module-boundary rule set or review guide
  - defaults for package gateways, module exports, import style, and import-time safety
  - local examples for public-surface patterns, anti-patterns, edge cases, and split signals
use_when:
  - designing or reviewing a Python package's public import surface
  - deciding what should be re-exported through `__init__.py`
  - deciding whether a module is public, internal, too broad, or too side-effectful at import time
  - reviewing deep imports, wildcard imports, circular imports, or boundary leaks across subpackages
do_not_use_when:
  - the main task is DDD layering, repository architecture, or framework-specific project structure
  - the main task is strict type-hint syntax, API-signature design, or ordinary class internals
  - the package is a namespace-package or no-`__init__.py` layout and the task is mainly about that structure
---

# Purpose
Choose clear, reviewable Python package and module boundaries without drifting into DDD, framework architecture, or packaging policy.

# Trigger / When to use
Use this skill when:
- designing or reviewing a Python package's public import surface
- deciding what should be re-exported through `__init__.py`
- deciding whether a module is public, internal, too broad, or too side-effectful at import time
- reviewing deep imports, wildcard imports, circular imports, or boundary leaks across subpackages

Do not use this skill when:
- the main task is DDD layering, repository architecture, or framework-specific project structure
- the main task is strict type-hint syntax, API-signature design, or ordinary class internals
- the package is a namespace-package or no-`__init__.py` layout and the task is mainly about that structure

# Inputs
- whether the package is a regular package with `__init__.py`
- the intended public import paths
- which modules are implementation detail only
- whether imports stay within one local scope or cross a clearer subpackage boundary
- whether the package has import-time setup, compatibility re-exports, or circular dependencies

# Process
1. Keep the first draft on regular packages with `__init__.py`; treat namespace-package or no-`__init__.py` layouts as out of scope and suggest a regular package when an explicit gateway is needed.
2. Define the package's public API through `__init__.py` with explicit re-exports and `__all__`; do not make external callers depend on deep imports into nested internal paths.
3. Treat underscore-prefixed modules and subpackages as non-public contracts to external packages; if outside callers need a stable entrypoint, re-export it through the package gateway instead.
4. Require every public module, even a single-file module, to declare `__all__`; do not expose underscore-prefixed private names through that export surface.
5. Within one local scope, prefer relative imports for internal collaboration; across clearer subpackage boundaries, prefer absolute imports and do not reach into another subpackage's underscore modules.
6. Keep imports declarative and safe: no wildcard imports, no import-time I/O, connections, environment-driven runtime validation, background tasks, or hidden registration side effects.
7. Treat circular imports as a boundary smell; first extract shared lower-level contracts, then inspect premature `__init__.py` coupling, then use `if TYPE_CHECKING:` for type-only cycles, and only use a function-local import as a documented last resort.
8. Keep executable script and CLI modules thin consumers rather than public API providers; reusable logic belongs in regular package modules, and execution should stay behind `main()` and/or `if __name__ == "__main__":`.
9. Treat test support code as boundary-managed code too: reusable test helper packages should expose a clean gateway, while individual `test_*.py` files remain execution-oriented consumers.
10. When a module becomes too broad, mixes unrelated responsibilities, or blends public and internal sections, recommend splitting it; keep deprecated re-exports only as explicit temporary bridges with a removal plan, replacement path, and deprecation signal.

# Examples
- Positive: Re-export `User` from `package/__init__.py`, declare `__all__` in both the gateway and the public module, keep `_adapter.py` internal, and move import-time setup into an explicit bootstrap function.
- Negative: Make callers import `package.internal.models.user.User`, rely on `from package.x import *`, register plugins just by importing a module, or leave a deprecated re-export in place with no warning or removal note.

# Outputs
- a review-ready Python module-boundary rule set or review guide
- defaults for package gateways, module exports, import style, and import-time safety
- local examples for public-surface patterns, anti-patterns, edge cases, and split signals

# Boundaries
- Do not define DDD layering, framework module layout, or packaging/distribution policy.
- Do not define strict typing syntax, API-signature rules, or class-internal design rules.
- Do not treat namespace packages as first-draft in-scope; only flag them and hand off.
- Do not claim `approved` or `stable`.

# Validation
Before proceeding, confirm:
- The package uses a regular layout with `__init__.py` (namespace packages are out of scope)
- The intended public import surface and which modules are internal are known or can be inferred

**SOFT FAIL** — ask and wait before continuing:
- Whether the package is a regular package or a namespace/no-`__init__.py` layout is unclear → ask before applying gateway rules
- Whether a circular import is type-only vs a runtime cycle is unclear → ask before recommending a specific fix path

**BLOCKED** — stop and redirect:
- The package is explicitly a namespace package or no-`__init__.py` layout and the task is mainly about that structure → note the limitation and redirect
- The main task is DDD layering, service architecture, or framework-specific project structure → redirect to the appropriate architectural skill

# Failure Handling
- **Missing Context**: if the public surface, internal module boundaries, or import patterns are unknown, ask once clearly before applying defaults.
- **Ambiguous Requirement**: if the stated goal conflicts with module-boundary scope (e.g., the question is really about DDD layering), name the conflict and redirect.
- **Execution Limitation**: if the task involves namespace packages or framework-specific layouts, stop and note the out-of-scope condition.

# Local references
- `examples.md`: gateway patterns, internal-module rules, import-side-effect anti-patterns, circular-import fixes, script/test edge cases, and deprecated re-export examples
