---
name: python-error-handling
description: Design or review general Python exception handling. Use this when choosing custom errors, translation boundaries, chaining, and when failures should propagate.
complexity: medium
risk_profile: [ambiguity_sensitive]
inputs:
  - whether the failure is business/package meaning or programmer misuse
  - whether the boundary is internal or public
  - whether the API contract is optional or error-signaling
  - whether the failure is known and controllable
  - the supported Python version baseline
outputs:
  - a review-ready general Python error-handling rule set or skill draft
  - defaults for error hierarchy, translation, propagation, and benign suppression
  - local examples for common cases, anti-patterns, and scope boundaries
use_when:
  - designing a project or package error hierarchy
  - deciding when to raise a custom error, keep a built-in, or let a failure propagate
  - reviewing broad catches, silent fallbacks, exception translation, or benign suppression
do_not_use_when:
  - the task is mainly about logging, observability, retry policy, or HTTP/framework exception mapping
  - the task is mainly about DDD layer-specific error translation
  - the task is mainly about ExceptionGroup, asyncio.CancelledError, or multi-error aggregation
---

# Purpose
Choose clear, semantic Python error-handling rules without mixing in framework or architecture-specific mapping.

# Trigger / When to use
Use this skill when:
- designing a project or package error hierarchy
- deciding when to raise a custom error, keep a built-in, or let a failure propagate
- reviewing broad catches, silent fallbacks, exception translation, or benign suppression

Do not use this skill when:
- the task is mainly about logging, observability, retry policy, or HTTP/framework exception mapping
- the task is mainly about DDD layer-specific error translation
- the task is mainly about `ExceptionGroup`, `asyncio.CancelledError`, or multi-error aggregation

# Inputs
- whether the failure is business/package meaning or programmer misuse
- whether the boundary is internal or public
- whether the API contract is optional or error-signaling
- whether the failure is known and controllable
- the supported Python version baseline

# Process
1. Define one custom root error that inherits from `Exception`; add topic-level base errors only when grouping or a stable catch boundary justifies them.
2. Use semantic custom errors for known business or package failures; leave programmer misuse and obvious bugs as built-ins such as `TypeError` or `ValueError`.
3. Catch only known, controllable failures and translate them once at the first boundary that can add real meaning.
4. Preserve the cause with `raise CustomError(...) from exc`; avoid `from None` except for narrow boundary cases that intentionally hide low-level detail.
5. Reject broad catches, silent `None` / `False` fallback, and untyped `except: pass`; allow only narrow benign suppression with explicit intent.
6. Keep the first draft on synchronous single-exception flows, and mention Python-version limits when newer exception features are out of scope.

# Examples
- Positive: Catch a low-level `ValueError` once at a package boundary and raise `InvalidConfigError` from it; return `None` only for an explicit lookup-miss API.
- Negative: Re-wrap the same failure at every layer, leak random built-ins from a public API for known business failures, or hide errors behind `except Exception` and empty fallback values.

# Outputs
- a review-ready general Python error-handling rule set or skill draft
- defaults for error hierarchy, translation, propagation, and benign suppression
- local examples for common cases, anti-patterns, and scope boundaries

# Boundaries
- Do not use Python's built-in `BaseException` as the application or package root error.
- Do not define logging timing, retry policy, or framework-specific exception mapping.
- Do not cover `ExceptionGroup`, `asyncio.CancelledError`, or multi-error aggregation in the first draft.

# Validation
Before proceeding, confirm:
- The failure domain is clear enough to distinguish business/package errors from programmer misuse
- The boundary type (internal vs public) is known or can be inferred

**SOFT FAIL** — ask and wait before continuing:
- Whether the failure is a business/package error or programmer misuse is unclear → ask before recommending a custom error vs built-in
- Whether the boundary is internal or public is unstated → ask before applying translation rules

**BLOCKED** — stop and redirect:
- The task is mainly about logging, observability, retry policy, or HTTP/framework exception mapping → redirect to the appropriate skill
- The task involves `ExceptionGroup`, `asyncio.CancelledError`, or multi-error aggregation → out of scope for this skill

# Failure Handling
- **Missing Context**: if the failure domain, boundary type, or Python version baseline are unknown, ask once clearly before applying defaults.
- **Ambiguous Requirement**: if the stated goal conflicts with error-handling scope (e.g., the task is really about retry policy or DDD translation), name the conflict and redirect.
- **Execution Limitation**: if the task involves framework-specific exception mapping, `ExceptionGroup`, or multi-error aggregation, stop and note the out-of-scope condition.

# Local references
- `examples.md`: hierarchy examples, translation rules, anti-patterns, and Python-version scope notes
