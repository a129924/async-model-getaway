# pr-18-remove-dynamic-onnx-import-test Specification

## Acceptance Criteria

1. The only production/test implementation paths are
   `src/async_model_gateway/model_runtime/model_pool/_onnx_runtime_loader.py` and
   `tests/model_runtime/model_pool/test_onnx_local_runtime_acquisition.py`.
2. Production ONNX acquisition still lazily imports the real
   `onnxruntime.InferenceSession` when no private test override is supplied, then
   constructs it with the existing path and `CPUExecutionProvider` through the existing
   `asyncio.to_thread(...)` call.
3. A private, fully typed, zero-argument lazy-importer callable seam permits focused
   tests to supply a constructor or raise an import error. It is not public, exported,
   accepted by `ModelPool`/`LocalModelLoader`, or typed with `Any`.
4. An injected `ModuleNotFoundError(name="onnxruntime")` becomes the existing chained
   `RuntimeError("ONNX runtime support requires installing async-model-gateway[onnx]")`.
   An injected `ModuleNotFoundError(name="onnxruntime.capi")` is unchanged by identity.
5. The test file has no `ModuleType`, `sys.modules`, `importlib`, module-table mutation,
   or dynamic module loading. Its normal `onnx` and `onnxruntime` imports remain static.
6. Existing empty-options, provider failure, invalid path/model, explicit-family,
   opaque-handle, ModelExecution handoff, thread-offload, and cancellation checks remain
   semantically intact.
7. `ModelPool.acquire(...) -> LoadedRuntimeModel[object]`, `LoadedRuntimeModel`,
   `ModelExecution`, dependency metadata, CI, docs, and all package exports remain
   unchanged.

## Behavioral Scenarios

### Scenario 1: default production acquisition remains real and lazy

- **Given**: a valid temporary ONNX artifact and no private importer override.
- **When**: a caller awaits `ModelPool().acquire(artifact)`.
- **Then**: the loader reaches the real private lazy import, creates a CPU-only
  `InferenceSession` in the existing worker-thread boundary, and returns the existing
  opaque loaded handle.

### Scenario 2: injected top-level missing dependency retains exact guidance

- **Given**: a focused helper invocation with a typed importer callable that raises
  `ModuleNotFoundError(name="onnxruntime")`.
- **When**: acquisition starts after empty-options validation.
- **Then**: it raises the exact existing install-guidance `RuntimeError` with that error
  as its cause.
- **And**: no test changes Python's module table.

### Scenario 3: injected nested import failure remains provider-owned

- **Given**: a typed importer callable that raises one
  `ModuleNotFoundError(name="onnxruntime.capi")` instance.
- **When**: the helper begins acquisition.
- **Then**: the same exception instance propagates without install guidance or wrapping.

### Scenario 4: constructor and existing async behavior remain intact

- **Given**: injected constructor callables for provider failure, deliberate blocking,
  and cancellation coverage.
- **When**: existing focused acquisition tests run.
- **Then**: constructor/provider errors propagate unchanged, the event loop advances
  while construction runs in its worker thread, and caller cancellation is re-raised
  unchanged.

## Error / Edge Cases

- Non-empty options fail before any importer or constructor callable runs.
- A nested import error must not be identified by message text or broadly translated;
  only its exact top-level `name` qualifies for installation guidance.
- The seam must not become a `LocalModelLoader`/`ModelPool` injection point, alter CPU
  providers, cache sessions, run inference, or add timeout/retry/lifecycle behavior.
- Dynamic module fabrication or `sys.modules` mutation is a governance failure even if
  functional tests pass.
