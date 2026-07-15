# runtime-model-minimal-consumption-contract Specification

## Acceptance Criteria

1. `async_model_gateway.model_runtime.runtime_model` exports exactly abstract nominal
   `LoadedRuntimeModel` based on `ABC`; it is not a dataclass, value object, type alias,
   Protocol, or Generic. Root package and `model_runtime` umbrella root do not re-export it.
2. `loaded_runtime_model.py` defines but does not export
   `_create_loaded_runtime_model(*, loader_family: LoaderFamily, provider_model: object)
   -> LoadedRuntimeModel`. Tests may statically import this helper; dynamic loading is
   prohibited.
3. `LoadedRuntimeModel` has abstract readonly `loader_family: LoaderFamily` as its only
   public semantic and `_provider_runtime(self) -> object` as a non-public model-side
   internal handoff. It has no public payload, unwrap, invocation, close, unload, timeout,
   cache, reuse, identity, or serialization API.
4. `loaded_runtime_model.py` keeps `_LocalLoadedRuntimeModel` private. It uses ordinary
   `__init__` to retain loader family/provider runtime, implements the abstract contract,
   makes no immutability claim, and uses none of `__new__`, custom `__setattr__`, frozen
   dataclass, or constructor-token enforcement.
5. `ModelPool.acquire`, `LocalModelLoader.load`, `_load_pickle`, `_load_torch`, and
   `_load_onnx` annotate `LoadedRuntimeModel` as their return type.
6. ModelPool-only export, private loader, retained loader, input validation, explicit
   family match/case, `assert_never`, direct await, and no-I/O `NotImplementedError`
   behavior remain unchanged.
7. Existing `TypeError`, `ValueError`, generic handler failure, and
   `asyncio.CancelledError` behavior propagates unchanged; no domain exception, I/O,
   timeout/retry/fallback, task, or lifecycle policy is added.
8. No `TypeVar`, `Generic`, `ModelArtifact[ProviderRuntimeT]`, or
   `LoadedRuntimeModel[object]` is introduced. Tester authors fresh replacement RED
   tests/evidence first through static private-factory import; historical immutable
   revision evidence does not approve this correction.
   the four pre-merge Implementer steps then execute. Independent implementation/code
   review approval precedes PR routing. Fresh Human release check gates separate
   post-merge v0.5.0 work and is not an implementation-review prerequisite; no GitHub
   Release or package publish occurs.

## Behavioral Scenarios

### Scenario 1: typed opaque local acquisition

- **Given**: a static-imported private helper creates a handle returned by a private
  family handler
- **When**: `ModelPool.acquire(artifact)` is awaited
- **Then**: it returns that typed abstract-boundary handle with matching
  `loader_family`, without public provider-payload access; the internal test seam may
  verify `_provider_runtime()` preserves the supplied provider runtime

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
- Direct `LoadedRuntimeModel` instantiation fails because it is abstract; provider payload
  is inaccessible from the public package surface. Mutation behavior is intentionally not
  a contract.
- Default family handlers remain no-I/O `NotImplementedError` stubs.
- Generic handler exceptions and `asyncio.CancelledError` are neither caught nor translated.
- Fresh RED evidence precedes implementation; independent implementation/code review
  approval precedes PR routing; fresh Human release check precedes post-merge v0.5.0 work.
