# local-runtime-handle-ownership-clarification Specification

## Acceptance Criteria

1. `LoadedRuntimeModel[RuntimeT]` remains an abstract, covariant opaque handle with
   readonly `loader_family` and private `_provider_runtime() -> RuntimeT`; its module
   no longer defines `_LocalLoadedRuntimeModel` or `_create_loaded_runtime_model()`.
2. `_local_model_loader.py` defines the only production concrete local handle as
   `LoadedRuntimeModel[object]`; it stores explicit `LoaderFamily` provenance and the
   provider object, and `_load_onnx(...)` directly returns that handle after unchanged
   ONNX session acquisition.
3. `LocalModelLoader` does not import the runtime-model private module/factory and has
   no `reportPrivateUsage` suppression. `ModelPool.acquire(...)` stays
   `LoadedRuntimeModel[object]` without a source change.
4. `ModelExecution.execute(...)` retains its existing public generic signature,
   injected async invoker, direct-await behavior, provider identity handoff, exception
   propagation, and cancellation propagation. It is the only production call site of
   `_provider_runtime()`.
5. Runtime-model/model-pool tests and strict fixtures construct test-local concrete
   handles where needed; they do not import, call, or simulate the removed factory, and
   they do not use dynamic module loading.
6. `docs/specs/model-side-boundary.md` states that a loaded local model is an opaque
   acquisition handle whose construction belongs to `LocalModelLoader`, and that
   `ModelExecution` owns invocation semantics. It does not claim `execute(...)`, an
   ONNX invoker, or provider adapters now exist.
7. ONNX CPU acquisition, explicit family routing, PICKLE/TORCH fail-closed behavior,
   dependencies, exports, README, version, release intent, and all public contracts
   outside this ownership clarification remain unchanged.

## Behavioral Scenarios

### Scenario 1: loader-local construction preserves opaque acquisition

- **Given**: an ONNX artifact whose existing private helper returns a provider session.
- **When**: `LocalModelLoader._load_onnx(...)` completes its existing await.
- **Then**: it directly creates a private local `LoadedRuntimeModel[object]` with
  `LoaderFamily.ONNX`, and callers observe the same erased public result/provenance as
  before.
- **And**: `LocalModelLoader` contains no import or call of a runtime-model factory.

### Scenario 2: execution remains the only production provider consumer

- **Given**: a loaded model and a typed injected invoker.
- **When**: `ModelExecution.execute(...)` is awaited.
- **Then**: the same provider object is handed to that invoker exactly once and the
  awaited result/exception/cancellation is propagated unchanged.
- **And**: a production-tree AST/source assertion identifies no other
  `_provider_runtime()` call expression.

### Scenario 3: private construction is reproducible in tests without a production factory

- **Given**: runtime-model, model-pool, or static-typing tests needing a provider handle.
- **When**: they exercise abstract typing or delegation behavior.
- **Then**: they use a test-local concrete `LoadedRuntimeModel` subclass with the
  needed concrete runtime type.
- **And**: the public runtime-model package exports only `LoadedRuntimeModel`.

### Scenario 4: ONNX acquisition and provenance do not gain execution semantics

- **Given**: the existing valid ONNX acquisition fixture.
- **When**: it is acquired and handed to existing `ModelExecution`.
- **Then**: ONNX family and provider identity remain available only through the internal
  handoff to the injected invoker; the loader does not invoke inference or dispatch on
  provider family.

## Error / Edge Cases

- `LoadedRuntimeModel()` remains uninstantiable because its two contract members remain
  abstract.
- No production consumer may call `_provider_runtime()` outside `ModelExecution`, even
  if it needs provider-specific behavior; that request belongs to a future execution
  topic.
- The governance test must inspect call expressions, not mere method definitions, so
  abstract/test-local method declarations do not create false failures.
- No changed test may use dynamic imports to access private modules. Private production
  construction factory use must be removed rather than bypassed with type-check ignores.
- Any need to expose a provider runtime, introduce `execute(...)`, alter generic typing,
  or add a dependency is scope drift and returns to planning.
