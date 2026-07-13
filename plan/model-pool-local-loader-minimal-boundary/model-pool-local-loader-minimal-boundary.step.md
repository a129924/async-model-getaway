---
topic: model-pool-local-loader-minimal-boundary
phase: plan-authoring
created: 2026-07-13
---

# model-pool-local-loader-minimal-boundary — Step Tracking

> **Executor**: Mark each step `[X]` when complete.
> Historical implementation rows remain `[X]`; release progression uses the fresh
> release gates and Implementer release steps below.
> Update this file at: `plan/model-pool-local-loader-minimal-boundary/model-pool-local-loader-minimal-boundary.step.md`

## Workflow Stages

- [X] plan-authoring
- [X] plan-review
- [X] tdd-test-authoring
- [X] implementation
- [X] implementation-review
- [X] code-review
- [ ] release

> The six checked stages and their implementation plan-review/human-check, RED-test,
> implementation-review, and code-review evidence are historical truth for the merged
> `assert-never-explicit-dispatch` implementation. The pending release stage is a
> separately gated post-merge metadata/docs/tag/evidence action; it does not reopen or
> rewrite that evidence.

> **Current release status**: `merged`. It may advance to `released` only after fresh
> release gates 5–6 and Implementer release steps 7–9 complete in order.

## Historical Review Evidence

- `plan/model-pool-local-loader-minimal-boundary/model-pool-local-loader-minimal-boundary.code-review.yaml`
  records the completed implementation code review. Along with the implementation
  plan-review, human-check, RED-test, and implementation-review artifacts, it is
  historical evidence only and is not a release gate. Fresh release gating is limited
  to steps 5–6 below.

## Historical Implementation Record

- [X] 1. Tester replaced `_route_mapping`-based tests and wrote fresh RED evidence: the suite asserts the exact two-line TODO, monkeypatches each private `_load_pickle`, `_load_torch`, and `_load_onnx` handler with distinct async results, and proves every `LoaderFamily` follows only its matching explicit branch. It retains package surface, pool-factory retention, applicable TypeError/ValueError validation, default NotImplementedError, route-failure, cancellation, and path-appearance coverage. The fabricated unforeseen-family `ValueError` expectation is removed; a source regression instead requires the `typing_extensions.assert_never` import and `case _` call. No test references `_route_mapping` or uses dynamic module loading. RED evidence: `uv run pytest --no-cov tests/model_runtime/model_pool -v` → `1 failed, 16 passed`; the failure confirms that the current `ValueError` fallback has not yet imported or called `assert_never`.
- [X] 2. Implementer revises `_local_model_loader.py`: remove mapping types, construction parameter, helper validation, stored mapping, and lookup dispatch; add the exact TODO; implement the three explicit `match/case` branches with `await`ed matching private handlers; retain no-I/O handler `NotImplementedError`; import `assert_never` from `typing_extensions` and make `case _` call `assert_never(artifact.loader_family)`.
- [X] 3. Implementer updates `pool.py` and `__init__.py` only as needed to conform to the removed private constructor seam, preserving ModelPool's locked public contract, factory-once retention, TypeError validation, direct await, and package-root export.
- [X] 4. Implementer runs `uv run pytest --no-cov tests/model_runtime/model_pool -v`, `uv run pytest -v`, `uv run ruff check src tests plan/model-pool-local-loader-minimal-boundary`, and `uv run pyright`, then marks only completed implementation steps.

## Post-merge / release gates

- [ ] 5. Plan-Reviewer records `verdict: approved` in
  `model-pool-local-loader-minimal-boundary.release-plan-review.json` for revision
  `v0.4.7-release-contract-sequenced`; only then may the Human create the release
  clearance.
- [ ] 6. Human creates
  `model-pool-local-loader-minimal-boundary.release-human-check.json` before any
  release work. It identifies this topic and revision, records the approved
  release-plan-review path and verdict, and states `decision: approved`,
  `status: cleared`, `cleared_for: release`, and `cleared: true`. Implementer must not
  author this artifact.

## Release Implementation Steps

- [ ] 7. After steps 5 and 6 are complete, Implementer updates only `README.md`,
  `docs/architecture.md`,
  `docs/specs/model-side-boundary.md`, `docs/specs/core-abstractions-boundary.md`, and
  `docs/specs/canonical-input-boundary.md` to state the minimal implemented
  ModelPool/private-loader boundary and retain all deferred wider-runtime work;
  synchronizes `src/async_model_gateway/__version__.py`, `pyproject.toml`, and
  `uv.lock` to `0.4.7`; runs release validation; and commits and pushes exactly those
  eight bounded docs/version changes on `dev` as the release commit.
- [ ] 8. Implementer creates lightweight `v0.4.7` from the exact release commit in
  step 7 and pushes the tag; local and remote tag verification must resolve to that
  release commit.
- [ ] 9. Implementer writes
  `model-pool-local-loader-minimal-boundary.release.yaml` with the release-commit SHA,
  tag resolution, remote-tag verification, and no-GitHub-Release/no-publish outcome;
  then commits and pushes the evidence separately on `dev` without moving, replacing,
  deleting, or retargeting `v0.4.7`.
