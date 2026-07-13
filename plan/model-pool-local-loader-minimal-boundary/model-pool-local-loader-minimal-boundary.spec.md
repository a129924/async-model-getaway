# model-pool-local-loader-minimal-boundary Specification

## Acceptance Criteria

1. `ModelPool.acquire(self, artifact: ModelArtifact) -> object` and ModelPool-only
   package exports remain unchanged.
2. `LocalModelLoader` is private, accepts no `_route_mapping` injection seam, and
   `load(self, artifact: ModelArtifact) -> object` contains exactly:

   ```python
   # TODO: Replace `object` with the agreed runtime-model contract
   # (tentatively `LoadedRuntimeModel`) once that boundary is defined.
   ```

3. `load(...)` dispatches only with explicit `match artifact.loader_family` cases for
   `PICKLE`, `TORCH`, and `ONNX`; each directly awaits its matching private
   `_load_<family>(artifact)` method. No mapping lookup, path inference, or KeyError
   dispatch exists. Its sole fallback is
   `typing_extensions.assert_never(artifact.loader_family)`, the type-checker-aware
   unreachable path for the closed `LoaderFamily` enum; it is not a runtime
   invalid-family policy or domain exception.
4. Tests monkeypatch each private family method and prove each LoaderFamily follows the
   matching branch only. The three default handlers perform no I/O and raise
   `NotImplementedError`.
5. TypeError for invalid `ModelPool.acquire` input, existing ValueError invalid-artifact
   behavior, native route failures, and cancellation are retained. No domain exception
   is added; no test manufactures a non-`LoaderFamily` fallback input.
6. `ModelArtifact` and `LoaderFamily` remain consumed unchanged; no runtime-model
   concrete type, Protocol, provider abstraction, ModelGateway, or ModelExecution is
   added.
7. The sole code-review evidence artifact is
   `plan/model-pool-local-loader-minimal-boundary/model-pool-local-loader-minimal-boundary.code-review.yaml`.
   An independent Reviewer writes it only after this revision's implementation review
   is approved and before PR routing. It accepts the revision only with a fresh
   `verdict: approved`; any covered source/test or implementation-contract planning
   revision after that verdict makes it stale and requires a replacement review.

## Behavioral Scenarios

### Scenario 1: each explicit family branch awaits its own handler

- **Given**: a `LocalModelLoader` whose `_load_pickle`, `_load_torch`, and `_load_onnx`
  methods are monkeypatched with unique async sentinel handlers
- **When**: `load(...)` receives a valid artifact for each current `LoaderFamily`
- **Then**: only that family's matching handler receives the same artifact and its
  sentinel is returned

### Scenario 2: family wins over artifact-path appearance

- **Given**: a PICKLE artifact with a path ending in `.onnx` and monkeypatched private
  handlers
- **When**: the loader is awaited
- **Then**: `_load_pickle` alone is awaited; the path/options/content do not affect
  dispatch

### Scenario 3: ModelPool preserves its existing retained-loader boundary

- **Given**: a factory monkeypatch installed before `ModelPool()` construction
- **When**: one or more artifacts are acquired
- **Then**: the factory was called once, the retained loader receives each artifact,
  and no new public injection/lifecycle surface appears

## Error / Edge Cases

- Each known default family handler is no-I/O and raises `NotImplementedError`.
- `ModelPool.acquire` rejects a non-`ModelArtifact` with `TypeError` before loader
  dispatch; invalid artifact construction remains `ValueError`.
- `case _` calls `typing_extensions.assert_never(artifact.loader_family)` as the
  closed-enum unreachable path. It must not become a `ValueError`, `KeyError`, or
  custom-domain-exception dispatch policy.
- Generic handler exceptions and `asyncio.CancelledError` propagate unchanged; no
  timeout, retry, fallback, wrapper, or `None` conversion exists.
- Tests use ordinary imports and monkeypatch private methods only; no dynamic module
  loading or `_route_mapping` reference is permitted.

## Review Evidence Contract

- The code-review artifact named in Acceptance Criterion 7 is Reviewer-owned and is
  the unique evidence location for `python-code-review` on this topic.
- It records `verdict`, `tooling_detected`, and findings for typing, lint,
  readability, error handling, anti-patterns, test quality, and observability.
- `needs-rework`, an absent artifact, or a stale artifact blocks `pr-comment`; a fresh
  `approved` verdict follows fresh approved implementation review and is the only
  quality-gate handoff to PR routing.
