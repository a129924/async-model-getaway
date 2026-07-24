# loaded-runtime-binding-refactor Specification

## Acceptance Criteria

1. `_LocalRuntimeComposition.execute()` is the sole production path calling `_RuntimeBindingResolver.resolve()`.
2. One execute call resolves once, passes same binding loader/concurrency to pool, then invokes same binding executor.
3. Private `_OnnxRuntime` Protocol requires only `get_providers() -> list[str]` and keeps production ONNX loader/executor/binding precisely paired. The loader applies the sole `cast(_OnnxRuntime, ...)` to `asyncio.to_thread(InferenceSession, ...)` result at optional third-party-stub boundary; only `_RuntimeBindingResolver` applies the erasure cast to its locked `RuntimeBinding[object, object, object]` return.
4. Internal pool accepts generic injection, loads raw runtime, creates wrapper, and has no resolver/executor/cache/retained-loader state.
5. Loaded model is concrete/generic with visible runtime, semaphore and aware-UTC timestamps, but no family/binding/loader/executor/lifecycle API.
6. Executor serializes with gate, timestamps after acquisition, and preserves result/error/cancellation identity.
7. Executor AST imports no resolver/composition, pool or artifact module and performs no late type/family/runtime dispatch.
8. Package exports are absent; old loader/helper/test and three live legacy fixtures are deleted; four historical configs remain unchanged and unexecuted.
9. Human-check and human-merge JSON shapes gate implementation/merge in required order.

## Behavioral Scenarios

### Scenario 1: Binding continuity

- **Given**: recording resolver, pool, loader and executor doubles.
- **When**: internal composition executes artifact and invocation.
- **Then**: events are `resolve`, acquire with resolver’s loader/concurrency, then execute with resolver’s executor; result identity is preserved.

### Scenario 2: Internal pool remains uncached

- **Given**: two equivalent injected ONNX acquisitions.
- **When**: both complete.
- **Then**: loader runs twice, wrappers differ, and each owns `Semaphore(1)`.

### Scenario 3: Precise ONNX pairing erases only at routing boundary

- **Given**: private `_OnnxRuntime` Protocol with `get_providers() -> list[str]` and concrete ONNX loader/executor.
- **When**: resolver creates ONNX binding.
- **Then**: loader, executor and binding share `_OnnxRuntime` internally; loader cast occurs only after session-constructor `asyncio.to_thread(...)`; only resolver return is erased to `object`.

### Scenario 4: Gate lifecycle precedes unsupported ONNX invocation

- **Given**: ONNX binding and loaded model.
- **When**: binding executor executes.
- **Then**: it obtains gate and marks model used before raising `NotImplementedError`.

## Error / Edge Cases

- Non-artifact input preserves `TypeError`.
- PICKLE/TORCH resolver paths raise `NotImplementedError` before loading.
- Existing ONNX options/missing-dependency/provider errors remain unchanged.
- Queued execution does not update timestamp; failed/cancelled invocation releases gate and propagates identical exception.
- New strict fixture rejects mismatched loader/executor/runtime pairing, missing or incompatible `get_providers() -> list[str]`, and any cast placement outside the two locked boundaries.
- Deleted paths include `_local_model_loader.py`, `_onnx_runtime_loader.py`, and `test_local_model_loader.py`; replacement loader package and protocol are required.
- Human check is exactly `{"status":"cleared_for_implementation"}` before implementation.
- Human merge is exactly `{"status":"cleared_for_merge","pr":"<actual PR identifier>"}` before merge; merge SHA comes only from repository/PR merge evidence.
