# model-payload-canonical-hash-core Specification

## Acceptance Criteria

1. `async_model_gateway.model_registry.model_payload` exposes exactly one
   public callable for this topic:
   `hash_model_payload(model_payload: dict[str, JSONLike]) -> str`.
2. `hash_model_payload` returns a SHA-256 lowercase hex string for supported
   JSON-like payload input.
3. Equivalent payloads with different dict insertion order hash identically
   after recursive nested-dict canonicalization.
4. List order remains significant, and scalar representations such as `1` and
   `1.0` are not normalized into the same hash result.
5. Unsupported nested values and nested dict keys that are not `str` raise
   `TypeError`.
6. `src/async_model_gateway/model_registry/__init__.py` does not re-export the
   hashing callable.

## Behavioral Scenarios

### Scenario 1: Stable hash for equivalent nested payload content
- **Given**: two top-level `dict[str, JSONLike]` payloads containing the same
  nested data but different dict insertion order
- **When**: `hash_model_payload(...)` is called for each payload
- **Then**: both calls return the same SHA-256 lowercase hex digest
- **Then**: nested dict ordering differences do not change the result

### Scenario 2: List order remains part of identity
- **Given**: two payloads that differ only in the order of a nested list
- **When**: `hash_model_payload(...)` is called
- **Then**: the resulting digests are different

### Scenario 3: Unsupported nested content fails closed
- **Given**: a payload tree that contains either an unsupported value type or a
  nested dict key that is not `str`
- **When**: `hash_model_payload(...)` is called
- **Then**: the call raises `TypeError`
- **Then**: no fallback coercion or semantic normalization occurs

### Scenario 4: Public import surface stays bounded
- **Given**: the hashing core is implemented under `model_registry/model_payload`
- **When**: a caller imports `hash_model_payload`
- **Then**: the supported import surface is
  `async_model_gateway.model_registry.model_payload`
- **Then**: `model_registry/__init__.py` does not become a broader re-export
  surface

## Error / Edge Cases

- Empty top-level payloads and nested empty dict / list structures must still
  produce deterministic SHA-256 lowercase hex output.
- Scalar representations are preserved literally for hashing, so payloads that
  differ only by `1` versus `1.0` remain distinguishable.
- Unsupported values must fail with `TypeError` even when they appear several
  levels deep in nested list / dict structures.
- The hashing helper must remain internal; exposing helper-only callables is
  outside this topic contract.
