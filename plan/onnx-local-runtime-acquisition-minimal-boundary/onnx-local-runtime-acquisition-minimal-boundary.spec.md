# onnx-local-runtime-acquisition-minimal-boundary Specification

## Acceptance Criteria

1. A valid `ModelArtifact` with `LoaderFamily.ONNX`, an empty `loader_options`, and a
   valid local model path can be acquired through `ModelPool.acquire()` as
   `LoadedRuntimeModel[object]` containing a real CPU-only `onnxruntime.InferenceSession`.
2. The ONNX session is built in `asyncio.to_thread(...)` with only
   `artifact.artifact_path` and `providers=["CPUExecutionProvider"]`; construction must
   not block the event-loop thread.
3. The ONNX provider object is wrapped through existing
   `_create_loaded_runtime_model(loader_family=LoaderFamily.ONNX, provider_model=session)`;
   `ModelExecution` can receive the same identity through its existing private handoff,
   while the loader does not invoke the session.
4. A non-empty `loader_options` raises exact
   `ValueError("ONNX loader_options are not supported")` before provider construction.
5. Only a missing top-level `onnxruntime` dependency is translated to chained
   `RuntimeError("ONNX runtime support requires installing async-model-gateway[onnx]")`.
   Provider failure, invalid model/path, nested import failure, and cancellation retain
   their original exception behavior.
6. `onnxruntime>=1.22.0,<1.22.1` is a published `onnx` optional extra;
   `onnx>=1.16.2,<1.17` is a dev fixture-only dependency. No public API/export, version,
   README, documentation, or release change is introduced.
7. PICKLE/TORCH remain fail closed; explicit `LoaderFamily` remains authoritative even
   when an artifact path suggests a different suffix.
8. Strict static analysis continues to see
   `ModelPool.acquire(...) -> LoadedRuntimeModel[object]`, and tests use static imports
   rather than dynamic module loading.

## Behavioral Scenarios

### Scenario 1: CPU-only ONNX acquisition returns an opaque loaded model

- **Given**: a temporary, valid ONNX model generated with the dev `onnx` package and a
  `ModelArtifact` whose explicit family is ONNX and whose options are empty.
- **When**: a caller awaits `ModelPool().acquire(artifact)`.
- **Then**: the loader uses the ONNX helper, constructs a real `InferenceSession` with
  `CPUExecutionProvider`, and returns `LoadedRuntimeModel[object]` whose family is ONNX.
- **And**: passing that handle to existing `ModelExecution` exposes the same session
  object only to the injected invoker; no inference occurs during loading.

### Scenario 2: explicit family wins over path appearance

- **Given**: a valid ONNX model stored at a path without an `.onnx` suffix.
- **When**: its artifact explicitly selects `LoaderFamily.ONNX`.
- **Then**: the loader acquires it successfully without suffix/path inference.
- **And**: a PICKLE artifact whose path looks like `.onnx` still reaches only the
  PICKLE handler and remains fail closed.

### Scenario 3: session creation yields control to the event loop

- **Given**: the private session factory is deliberately blocked after worker start and
  another coroutine is ready to run.
- **When**: ONNX acquisition awaits the thread-offloaded factory.
- **Then**: the other coroutine advances before the factory is released.
- **And**: cancellation of the awaiting caller is raised unchanged; the test releases
  the worker fixture without claiming the cancellation stopped native construction.

### Scenario 4: optional dependency and options failures are bounded

- **Given**: an ONNX artifact with non-empty options, or a private import seam that
  reports `ModuleNotFoundError(name="onnxruntime")`.
- **When**: the helper begins acquisition.
- **Then**: non-empty options fail before import/construction with the exact
  `ValueError`; missing runtime fails with the exact chained install-guidance
  `RuntimeError`.
- **And**: no other exception family is translated.

## Error / Edge Cases

- Invalid/missing model paths, invalid ONNX graph contents, execution-provider failures,
  and nested import failures propagate their original provider exception; they are not
  changed into install guidance.
- Cancellation propagates as `asyncio.CancelledError`; no timeout/retry/cancellation
  enforcement is added for a native session construction already running in a thread.
- No `.onnx` suffix is required for an explicit ONNX artifact, and no suffix may route a
  different family into ONNX.
- Empty options are the only supported first-version configuration. No partial options
  parsing or silently ignored options is permitted.
- The loader does not create an invoker, call inference, cache sessions, close sessions,
  or modify public package exports.
