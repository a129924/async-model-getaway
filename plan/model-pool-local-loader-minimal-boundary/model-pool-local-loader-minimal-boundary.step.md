---
topic: model-pool-local-loader-minimal-boundary
phase: plan-authoring
created: 2026-07-13
---

# model-pool-local-loader-minimal-boundary — Step Tracking

> **Executor**: Mark each step `[X]` when complete.
> All Implementation Steps must be `[X]` before submitting for `python-implementation-review`.
> Update this file at: `plan/model-pool-local-loader-minimal-boundary/model-pool-local-loader-minimal-boundary.step.md`

## Workflow Stages

- [X] plan-authoring
- [X] plan-review
- [X] tdd-test-authoring
- [X] implementation
- [X] implementation-review
- [X] code-review

> `assert_never(...)` revises the implementation contract. Fresh plan-review and
> human-check evidence approve and clear this revision for the mandatory RED-test
> subphase. All prior `ValueError`-fallback RED-test, implementation-review, and
> code-review evidence remains stale and cannot satisfy this revision's later gates.

## Review Evidence Gate

- `plan/model-pool-local-loader-minimal-boundary/model-pool-local-loader-minimal-boundary.code-review.yaml`
  is the sole Reviewer-owned `python-code-review` evidence path. It may be written
  only after this revision's implementation-review artifact is `approved`; its fresh
  `verdict: approved` is required before `pr-comment` routing.
- Any reviewed source/test change, or plan/spec/RED/step change that alters the
  implementation contract, after that verdict makes the code-review evidence stale.
  Leave this stage unchecked and route to a new independent code review at the same
  path after the applicable rework and fresh implementation review.

## Implementation Steps

- [X] 1. Tester replaced `_route_mapping`-based tests and wrote fresh RED evidence: the suite asserts the exact two-line TODO, monkeypatches each private `_load_pickle`, `_load_torch`, and `_load_onnx` handler with distinct async results, and proves every `LoaderFamily` follows only its matching explicit branch. It retains package surface, pool-factory retention, applicable TypeError/ValueError validation, default NotImplementedError, route-failure, cancellation, and path-appearance coverage. The fabricated unforeseen-family `ValueError` expectation is removed; a source regression instead requires the `typing_extensions.assert_never` import and `case _` call. No test references `_route_mapping` or uses dynamic module loading. RED evidence: `uv run pytest --no-cov tests/model_runtime/model_pool -v` → `1 failed, 16 passed`; the failure confirms that the current `ValueError` fallback has not yet imported or called `assert_never`.
- [X] 2. Implementer revises `_local_model_loader.py`: remove mapping types, construction parameter, helper validation, stored mapping, and lookup dispatch; add the exact TODO; implement the three explicit `match/case` branches with `await`ed matching private handlers; retain no-I/O handler `NotImplementedError`; import `assert_never` from `typing_extensions` and make `case _` call `assert_never(artifact.loader_family)`.
- [X] 3. Implementer updates `pool.py` and `__init__.py` only as needed to conform to the removed private constructor seam, preserving ModelPool's locked public contract, factory-once retention, TypeError validation, direct await, and package-root export.
- [X] 4. Implementer runs `uv run pytest --no-cov tests/model_runtime/model_pool -v`, `uv run pytest -v`, `uv run ruff check src tests plan/model-pool-local-loader-minimal-boundary`, and `uv run pyright`, then marks only completed implementation steps.
