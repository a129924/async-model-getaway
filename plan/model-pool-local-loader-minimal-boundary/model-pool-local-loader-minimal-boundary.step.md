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

- [X] 1. Tester replaces `_route_mapping`-based tests in the three declared test files and writes fresh RED evidence: assert the exact two-line TODO, monkeypatch each private `_load_pickle`, `_load_torch`, and `_load_onnx` handler with distinct async results, and prove each `LoaderFamily` follows only its matching explicit branch. Retain package surface, pool-factory retention, TypeError, ValueError, default NotImplementedError, route-failure, cancellation, and path-appearance coverage. Tests must not reference `_route_mapping` or use dynamic module loading.
- [X] 2. Implementer revises `_local_model_loader.py`: remove mapping types, construction parameter, helper validation, stored mapping, and lookup dispatch; add the exact TODO; implement the three explicit `match/case` branches with `await`ed matching private handlers; retain no-I/O handler `NotImplementedError`; raise `ValueError` for an unforeseen family instead of allowing `KeyError`.
- [X] 3. Implementer updates `pool.py` and `__init__.py` only as needed to conform to the removed private constructor seam, preserving ModelPool's locked public contract, factory-once retention, TypeError validation, direct await, and package-root export.
- [X] 4. Implementer runs `uv run pytest --no-cov tests/model_runtime/model_pool -v`, `uv run pytest -v`, `uv run ruff check src tests plan/model-pool-local-loader-minimal-boundary`, and `uv run pyright`, then marks only completed implementation steps.
