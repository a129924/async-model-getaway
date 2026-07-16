---
topic: runtime-model-runtime-generic-erasure
phase: plan-authoring
created: 2026-07-16
---

# runtime-model-runtime-generic-erasure — Step Tracking

> **Executor**: Mark each step `[X]` when complete.
> All Implementation Steps must be `[X]` before submitting for `python-implementation-review`.
> Update this file at: `plan/runtime-model-runtime-generic-erasure/runtime-model-runtime-generic-erasure.step.md`

## Workflow Stages

- [X] plan-authoring
- [X] plan-review
- [X] tdd-test-authoring
- [X] implementation
- [X] implementation-review
- [X] code-review

## Implementation Steps

- [X] 1. Tester updates the five declared runtime-model/model-pool test files, adds `tests/typecheck/runtime_model_generic_erasure.py` and the topic-local `pyrightconfig.json`, then records fresh focused pytest and dedicated Pyright RED evidence in `runtime-model-runtime-generic-erasure.red-tests.yaml` before production source changes.
- [X] 2. Implementer changes `src/async_model_gateway/model_runtime/runtime_model/loaded_runtime_model.py` to define covariant `RuntimeT`, genericise the ABC and private local implementation, and make the private factory preserve `RuntimeT` without exporting private symbols.
- [X] 3. Implementer changes `src/async_model_gateway/model_runtime/model_pool/pool.py` only to make `ModelPool.acquire()` return `LoadedRuntimeModel[object]`, retaining its validation, retained loader, and direct-await behavior.
- [X] 4. Implementer changes `src/async_model_gateway/model_runtime/model_pool/_local_model_loader.py` only to make `load()` and `_load_pickle()`, `_load_torch()`, and `_load_onnx()` return `LoadedRuntimeModel[object]`, retaining explicit dispatch, `assert_never`, no-I/O, and propagation behavior.
- [X] 5. Implementer runs the declared validation commands, confirms focused RED is GREEN, confirms ReadOnly and historical paths have no diff, and marks only actually completed entries in `runtime-model-runtime-generic-erasure.step.md`.
