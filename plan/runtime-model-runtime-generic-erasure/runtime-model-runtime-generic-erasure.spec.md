# runtime-model-runtime-generic-erasure Specification

## Acceptance Criteria

1. `LoadedRuntimeModel` accepts a covariant generic type parameter, and `_provider_runtime()` returns that parameter at the private internal seam.
2. `_LocalLoadedRuntimeModel` and `_create_loaded_runtime_model()` preserve the provider runtime type internally without adding package-root exports.
3. `ModelPool.acquire()`, `LocalModelLoader.load()`, `_load_pickle()`, `_load_torch()`, and `_load_onnx()` are annotated exactly as `LoadedRuntimeModel[object]`.
4. `ModelArtifact` and `LoaderFamily` remain non-generic; provider framework types do not enter public acquisition annotations.
5. Explicit family dispatch, no-I/O, validation, direct await, generic failure propagation, and `CancelledError` propagation remain behaviorally unchanged.

## Behavioral Scenarios

### Scenario 1: private factory retains runtime precision

- **Given**: a provider model with a concrete static type and a valid `LoaderFamily`.
- **When**: `_create_loaded_runtime_model()` receives that provider model.
- **Then**: the returned private-boundary handle is `LoadedRuntimeModel[RuntimeT]`, `_provider_runtime()` returns the same provider object, and `loader_family` remains the supplied family.

### Scenario 2: public local acquisition remains erased

- **Given**: a valid `ModelArtifact` and `ModelPool` with its retained private loader.
- **When**: static analysis examines `ModelPool.acquire()` and the local loader family handlers.
- **Then**: each acquisition annotation is `LoadedRuntimeModel[object]`, regardless of the provider runtime type internally preserved by the factory.

### Scenario 3: existing local boundary behavior remains stable

- **Given**: supported and unsupported artifacts, plus loader failures and cancellation.
- **When**: callers exercise the existing pool and private loader routes.
- **Then**: family selection remains explicit, no artifact I/O occurs, validation failures and loader failures propagate as before, and cancellation is not translated or swallowed.

## Error / Edge Cases

- Abstract `LoadedRuntimeModel` construction remains invalid and existing invalid input exceptions remain unchanged.
- Unsupported loader-family fallback remains closed through `assert_never`; no path- or content-based family inference is introduced.
- No `Any`, file-wide private-use suppression, dynamic module loading, or provider-specific public type is introduced to satisfy static checks.
- Static type validation must include the fixture path positionally and confirm it analyses source, preventing zero-source false green.
- `RuntimeT`, `_LocalLoadedRuntimeModel`, and `_create_loaded_runtime_model` must not become package-root exports.
