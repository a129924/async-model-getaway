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
- [ ] plan-review
- [ ] tdd-test-authoring
- [ ] implementation
- [ ] implementation-review
- [ ] code-review

## Implementation Steps

- [ ] 1. Tester adds RED coverage in `tests/model_runtime/model_pool/test_model_pool_package_surface.py`, `test_model_pool.py`, and `test_local_model_loader.py`, then records the failing contract in `plan/model-pool-local-loader-minimal-boundary/model-pool-local-loader-minimal-boundary.red-tests.yaml`: construct `LocalModelLoader(_route_mapping=...)` with exactly all `LoaderFamily` keys and unique async sentinel routes; monkeypatch `async_model_gateway.model_runtime.model_pool.pool._create_local_model_loader` with a zero-argument callable returning it before `ModelPool()`; assert only `ModelPool` is package-public, factory-once retention, direct route results, no-I/O defaults, `ValueError` for wrong key sets, `TypeError` for non-`Mapping`/non-callable mapping input, and the locked invalid-input, route-failure, and cancellation surfaces.
- [ ] 2. Implementer adds `src/async_model_gateway/model_runtime/model_pool/_local_model_loader.py` with private `LocalModelLoader(*, _route_mapping=...)`; before any route await, it requires all and only `LoaderFamily` keys (`ValueError` for missing, extra, or non-family keys; `TypeError` for non-`Mapping` input or non-callable values), dispatches explicitly, and supplies no-I/O default routes that raise `NotImplementedError`.
- [ ] 3. Implementer adds `src/async_model_gateway/model_runtime/model_pool/pool.py` and `__init__.py`: define `def _create_local_model_loader() -> LocalModelLoader`; every `ModelPool()` construction calls it exactly once and retains its returned loader; `acquire(...)` validates `ModelArtifact`, directly awaits that loader, and re-exports only `ModelPool` from the topic package root.
- [ ] 4. Implementer runs `uv run pytest tests/model_runtime/model_pool -v`, `uv run ruff check src tests plan/model-pool-local-loader-minimal-boundary`, and `uv run pyright`; after all pass, update only the Implementer-owned progress in `plan/model-pool-local-loader-minimal-boundary/model-pool-local-loader-minimal-boundary.step.md`.
