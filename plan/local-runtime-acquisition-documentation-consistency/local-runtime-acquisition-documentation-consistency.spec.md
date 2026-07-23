# local-runtime-acquisition-documentation-consistency Specification

## Acceptance Criteria

1. `README.md`, `docs/architecture.md`, `docs/specs/model-side-boundary.md`, and
   `docs/specs/core-abstractions-boundary.md` consistently describe the local path as
   `ModelArtifact → LocalModelLoader → provider session → LoadedRuntimeModel →
   ModelExecution → result`.
2. Documentation identifies `ModelPool.acquire(...)` as the existing public local entry
   that retains private `LocalModelLoader`; it does not introduce a public API, new flow
   node, or provider-specific public type.
3. Documentation states that the ONNX local route acquires a CPU-only provider session
   through explicit `LoaderFamily.ONNX` routing, then creates a loader-local private
   opaque `LoadedRuntimeModel`; PICKLE/TORCH remain fail closed.
4. Documentation states that `LoadedRuntimeModel` exposes only `loader_family`
   publicly. Provider runtime reaches existing `ModelExecution` only through the
   non-public handoff, and `ModelExecution` direct-awaits its injected invoker to return
   that invocation result.
5. No document claims a public `execute(...)`, provider getter, runtime factory, ONNX
   invoker/adapter, provider dispatch, lifecycle, retry, timeout, remote execution, or
   orchestrator implementation.
6. No source, test, dependency, version, release, package-export, or existing-topic
   artifact changes occur. Fresh focused tests, full pytest, Pyright, Ruff, and diff
   checks pass after the four-document update.

## Behavioral Scenarios

### Scenario 1: first-read documentation distinguishes acquisition from execution

- **Given**: a reader starts at `README.md`.
- **When**: they read the local runtime summary and deferred-items section.
- **Then**: they learn that ONNX local acquisition exists through an opaque handle.
- **And**: they do not infer that provider-specific inference, an `execute(...)` API, or
  lifecycle management is complete.

### Scenario 2: architecture and model-side detail preserve internal ownership

- **Given**: a reader follows the local model path into the architecture and model-side
  specification.
- **When**: they trace the documented flow from `ModelArtifact` to result.
- **Then**: explicit `LocalModelLoader` routing obtains a provider session, preserves it
  behind `LoadedRuntimeModel`, and hands it internally to `ModelExecution`.
- **And**: they see that the injected invoker, rather than loader/provider dispatch,
  produces the returned result.

### Scenario 3: cross-document summary remains bounded

- **Given**: a reader uses `core-abstractions-boundary.md` as an index.
- **When**: they inspect its dependency direction summary.
- **Then**: it names the same acquisition-to-execution sequence without copying detailed
  provider implementation or asserting a completed orchestrator.

## Error / Edge Cases

- The word `result` refers only to the existing injected invocation seam's returned
  value; it must not imply a standardized result schema or an ONNX output adapter.
- The generic phrase `provider session` must not erase the fact that only the ONNX route
  currently performs real acquisition; PICKLE/TORCH remain `NotImplementedError`.
- Removing stale "no real local acquisition" wording must not remove the still-true
  deferrals for true provider invocation, lifecycle, timeout/retry, remote execution,
  and orchestrator wiring.
- Documentation validation reuses existing tests only; no docs parser, snapshot test, or
  new test module is introduced.
