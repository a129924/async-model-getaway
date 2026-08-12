# local-response-generation-with-cache-reuse Specification

## Acceptance Criteria

1. After its existing local and ONNX guards, and before first awaiting registry
   freshness, `LocalResponseGateway.generate()` materializes exactly one
   `invocation_snapshot = dict(request.invocation)`.
2. The gateway does not read `request.invocation` after materialization. It calls
   the private deriver exactly as
   `deriver(model_name=request.model_name,
   model_payload_hash=freshness.entry.payload_hash, features=request.features,
   model_artifact=request.model_artifact, invocation=invocation_snapshot)` and
   gives the existing private executor `artifact=request.model_artifact,
   invocation=invocation_snapshot`. The executor invocation container has the
   same identity as the deriver invocation argument; neither private signature
   nor public package surface changes.
3. The snapshot freezes only top-level key/value associations. Nested/unknown
   leaf objects preserve identity and are not deep-copied; the caller must not
   mutate the leaf graph while generation is running.
4. If snapshot materialization fails, that exception propagates unchanged before
   registry, deriver, cache, executor, converter, or remember observation, and
   the gateway adds no await, task, retry, timeout, catch, or fallback.
5. The deriver's opaque returned `CacheKey` is passed unchanged to cache lookup
   and miss remember; the gateway neither reconstructs it nor derives a second
   key.
6. A deterministic suspend-point test pauses registry freshness after snapshot
   materialization, mutates the original request mapping, and proves deriver and
   executor receive the same original top-level snapshot; cache identity and
   execution result cannot diverge.
7. Local/ONNX guards, fresh private cache contexts, exhaustive cache outcome
   matching, fail-open writes, privacy, direct awaits, exception/cancellation
   propagation, and independent same-key misses remain unchanged.
8. `ModelRegistry`, `ResponseCache`, `CacheKey`, `ModelPayloadHasher`,
   `ModelArtifact`, default executor, request DTO, package exports,
   `README.md`, `docs/architecture.md`, and version metadata remain unchanged.
9. Current aggregate implementation and code review evidence compares the actual
   PR baseline `d5c5b329fec43f1d46fabdb87e1afb55573eb424` with the exact
   post-commit review head and covers all cumulative declared topic paths. Old
   `addfdb3`-baseline reviews are historical/non-gating and are not rewritten.

## Behavioral Scenarios

### Scenario 1: cache identity and execution share the snapshot

- **Given**: a supported request and cache miss.
- **When**: generation materializes its snapshot before registry freshness.
- **Then**: registry ->
  `deriver(model_name=request.model_name,
  model_payload_hash=freshness.entry.payload_hash, features=request.features,
  model_artifact=request.model_artifact, invocation=invocation_snapshot)` ->
  lookup -> executor with `artifact=request.model_artifact,
  invocation=invocation_snapshot` -> converter -> remember runs. The executor
  and deriver invocation arguments have the same container identity, and
  lookup/remember receive the deriver's unchanged opaque key.

### Scenario 2: caller mutation during registry freshness cannot split behavior

- **Given**: registry signals that it has been awaited after snapshot materialization.
- **When**: the caller replaces a top-level invocation value and registry resumes.
- **Then**: deriver and executor observe the same pre-mutation snapshot, and the
  derived cache identity and response correspond to that same input.

### Scenario 3: shallow leaf semantics remain explicit

- **Given**: an invocation containing an unknown nested object.
- **When**: the gateway makes its top-level snapshot.
- **Then**: the nested object identity is preserved; caller leaf mutation during
  generation is outside the gateway contract.

### Scenario 4: snapshot materialization fails before async work

- **Given**: an invocation mapping whose `dict()` materialization raises a
  sentinel exception.
- **When**: generation is awaited after passing both guards.
- **Then**: that same exception propagates and no registry, deriver, cache,
  executor, converter, or remember call occurs.

## Error / Edge Cases

- Non-local source and non-ONNX artifact still raise `NotImplementedError` before
  snapshot materialization or collaborator observation.
- The gateway neither catches snapshot/deriver failures nor suppresses
  cancellation, and it never remembers after a pre-remember failure.
- `Remembered`, `Skipped`, and `Failed` still return converted output; unexpected
  closed outcomes reach `assert_never`.
- Tests use static imports only; dynamic module loading is not authorized.
