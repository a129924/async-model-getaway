---
topic: runtime-model-minimal-consumption-contract
phase: plan-review
created: 2026-07-15
---

# runtime-model-minimal-consumption-contract — Step Tracking

> **Current state**: `reviewer-in-progress`. plan-authoring is complete; active plan-review is not complete.

## Workflow Stages

- [X] plan-authoring
- [ ] plan-review (active)
- [ ] human-check
- [ ] tdd-test-authoring
- [ ] implementation
- [ ] implementation-review
- [ ] code-review
- [ ] pr-comment
- [ ] human-merge
- [ ] release

## Implementation Steps

- [ ] 1. Tester writes fresh RED tests in `tests/model_runtime/runtime_model/test_loaded_runtime_model.py`, `tests/model_runtime/runtime_model/test_runtime_model_package_surface.py`, `tests/model_runtime/model_pool/test_model_pool.py`, `tests/model_runtime/model_pool/test_local_model_loader.py`, and `tests/model_runtime/model_pool/test_model_pool_package_surface.py`; statically imports the private helper and records `runtime-model-minimal-consumption-contract.red-tests.yaml` without dynamic loading.
- [ ] 2. Implementer adds `src/async_model_gateway/model_runtime/runtime_model/loaded_runtime_model.py` and `src/async_model_gateway/model_runtime/runtime_model/__init__.py` with the locked immutable opaque handle and helper.
- [ ] 3. Implementer updates `src/async_model_gateway/model_runtime/model_pool/pool.py` so `ModelPool.acquire` returns `LoadedRuntimeModel`, retaining validation, retained loader, direct await.
- [ ] 4. Implementer updates `src/async_model_gateway/model_runtime/model_pool/_local_model_loader.py` so `load` and all handlers return `LoadedRuntimeModel`, retaining dispatch, `assert_never`, no-I/O stubs.
- [ ] 5. Implementer runs `uv run pytest --no-cov tests/model_runtime/runtime_model tests/model_runtime/model_pool -v`, `uv run pytest -v`, `uv run ruff check src tests plan/runtime-model-minimal-consumption-contract`, `uv run pyright`, and `uv lock --check`; records truthful progress.
- [ ] 6. After Human merge/release-human-check, Implementer updates only `README.md`, `docs/architecture.md`, `docs/specs/model-side-boundary.md`, `docs/specs/core-abstractions-boundary.md`, `src/async_model_gateway/__version__.py`, `pyproject.toml`, `uv.lock` to v0.5.0 and validates.
- [ ] 7. Implementer creates/pushes lightweight `v0.5.0` from the step-6 release commit and writes `plan/runtime-model-minimal-consumption-contract/runtime-model-minimal-consumption-contract.release.yaml`; no GitHub Release/package publish.
