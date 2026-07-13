# model-pool-local-loader-minimal-boundary Specification

## Acceptance Criteria

1. `async_model_gateway.model_runtime.model_pool` re-exports only `ModelPool`; no
   other package root re-exports `ModelPool` or private `LocalModelLoader`.
2. `ModelPool.acquire` is `async def acquire(self, artifact: ModelArtifact) -> object`.
3. `pool.py` defines `def _create_local_model_loader() -> LocalModelLoader`; every
   `ModelPool.__init__` calls it exactly once and owns its exact returned private local
   loader for the pool instance lifetime, then directly awaits it without cache,
   reuse, close/unload, timeout, retry, or task orchestration.
4. `LocalModelLoader` dispatches only from explicit `artifact.loader_family`; every
   locked `LoaderFamily` has its own observable internal route and no path inference.
5. Default routes perform no I/O and raise `NotImplementedError`; non-artifact input
   raises `TypeError`, while route failures and cancellation propagate unchanged.
6. `ModelArtifact` and `LoaderFamily` remain consumed shared read contracts with no
   changes to their source, tests, package exports, fields, or vocabulary.
7. The only test-only loader construction seam is
   `LocalModelLoader(*, _route_mapping: Mapping[LoaderFamily, Callable[[ModelArtifact], Awaitable[object]]] | None = None)`.
   A supplied mapping must contain all and only current `LoaderFamily` keys before
   any route is awaited; missing, extra, or non-family keys raise `ValueError`, while
   a non-`Mapping` input or non-callable route value raises `TypeError`.
8. Targeted `model_pool` behavior validation runs
   `uv run pytest --no-cov tests/model_runtime/model_pool -v`; `uv run pytest -v`
   remains the required repository-wide coverage gate before ruff and pyright.

## Behavioral Scenarios

### Scenario 1: explicit family route is acquired through ModelPool

- **Given**: `LocalModelLoader(_route_mapping=...)` with a distinct async sentinel
  route for each locked `LoaderFamily`, and a zero-argument monkeypatch of
  `async_model_gateway.model_runtime.model_pool.pool._create_local_model_loader`
  that returns that loader before `ModelPool()` construction
- **When**: a caller awaits `pool.acquire(artifact)` for an artifact with one family
- **Then**: the factory is called once during construction and the pool awaits its
  retained returned loader exactly once
- **And**: the loader invokes only the route for `artifact.loader_family`
- **And**: the caller receives the identical opaque sentinel object

### Scenario 2: explicit family overrides path appearance

- **Given**: an artifact with `loader_family=LoaderFamily.PICKLE` and an artifact path
  ending in `.onnx`
- **When**: the private loader dispatches it through an injected route mapping
- **Then**: only the PICKLE route is observed
- **And**: no suffix, content, loader options, or object-shape inference occurs

### Scenario 3: default routes stay intentionally unavailable

- **Given**: an ordinary `ModelPool()` with no test route injection
- **When**: the caller awaits acquire for any locked family
- **Then**: the selected default route raises `NotImplementedError`
- **And**: no artifact file, serialization library, provider adapter, cache, or
  lifecycle cleanup is touched

### Scenario 4: failures retain their native async surface

- **Given**: an injected route that raises a specific exception or
  `asyncio.CancelledError`
- **When**: the caller awaits `pool.acquire(artifact)`
- **Then**: the exact exception propagates unchanged
- **And**: no timeout, retry, fallback, wrapping, or `None` conversion occurs

## Error / Edge Cases

- `acquire` rejects a non-`ModelArtifact` before route dispatch with `TypeError`.
- A private `_route_mapping` with missing, extra, or non-family keys raises
  `ValueError` before any route is awaited; non-`Mapping` input and non-callable route
  values raise `TypeError`, rather than silently falling back.
- The default no-I/O `NotImplementedError` is deliberate and does not claim that the
  artifact is malformed or that a different family should be guessed.
- Concurrent acquisition, loader cache/reuse, resource ownership beyond the retained
  in-memory collaborator, close/unload, timeout, retry, and provider-specific errors
  are not established by this topic.
