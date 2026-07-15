# runtime-model-minimal-consumption-contract Specification

## Acceptance Criteria

1. `async_model_gateway.model_runtime.runtime_model` exports exactly concrete nominal
   `LoadedRuntimeModel`; root package and `model_runtime` umbrella root do not re-export it.
2. `loaded_runtime_model.py` defines but does not export
   `_create_loaded_runtime_model(*, loader_family: LoaderFamily, provider_model: object)
   -> LoadedRuntimeModel`. Tests may statically import this helper; dynamic loading is
   prohibited.
3. `LoadedRuntimeModel` uses private `__loader_family` and `__provider_model` slots,
   rejects direct construction and mutation, and exposes only readonly `loader_family`.
   It has no public payload, unwrap, invocation, close, unload, timeout, cache, reuse,
   identity, or serialization API.
4. `ModelPool.acquire`, `LocalModelLoader.load`, `_load_pickle`, `_load_torch`, and
   `_load_onnx` annotate `LoadedRuntimeModel` as their return type.
5. ModelPool-only export, private loader, retained loader, input validation, explicit
   family match/case, `assert_never`, direct await, and no-I/O `NotImplementedError`
   behavior remain unchanged.
6. Existing `TypeError`, `ValueError`, generic handler failure, and
   `asyncio.CancelledError` behavior propagates unchanged; no domain exception, I/O,
   timeout/retry/fallback, task, or lifecycle policy is added.
7. Tester authors fresh RED tests/evidence first through static private-helper import;
   the six Implementer steps then execute. Independent implementation/code review
   approval precedes PR routing; fresh Human release check precedes post-merge v0.5.0
   work, with no GitHub Release or package publish.

## Behavioral Scenarios

### Scenario 1: typed opaque local acquisition

- **Given**: a static-imported private helper creates a handle returned by a private
  family handler
- **When**: `ModelPool.acquire(artifact)` is awaited
- **Then**: it returns that typed handle with matching `loader_family`, without public
  provider-payload access

### Scenario 2: family is the only route input

- **Given**: a PICKLE artifact whose path looks like ONNX and typed monkeypatched handlers
- **When**: `LocalModelLoader.load(artifact)` is awaited
- **Then**: only `_load_pickle` is awaited

### Scenario 3: narrow package surfaces

- **Given**: ordinary imports of root, umbrella, `runtime_model`, and `model_pool`
- **When**: exports are inspected
- **Then**: `runtime_model` contains only `LoadedRuntimeModel`, `model_pool` only
  `ModelPool`, and root/umbrella gain no export

## Error / Edge Cases

- Invalid acquisition input and artifact construction retain `TypeError` and `ValueError`.
- Direct handle construction/mutation is rejected; provider payload is inaccessible.
- Default family handlers remain no-I/O `NotImplementedError` stubs.
- Generic handler exceptions and `asyncio.CancelledError` are neither caught nor translated.
- Fresh RED evidence precedes implementation; independent implementation/code review
  approval precedes PR routing; fresh Human release check precedes post-merge v0.5.0 work.
