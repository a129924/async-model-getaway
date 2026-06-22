# model-payload-hasher-class-surface Specification

## Acceptance Criteria

1. `async_model_gateway.model_registry.model_payload` exposes
   `ModelPayloadHasher` as the only public hashing owner for this topic.
2. `ModelPayloadHasher.hash_model_payload(...)` returns a SHA-256 lowercase hex
   string for supported `dict[str, JSONLike]` payload input.
3. Equivalent payloads with different nested-dict insertion order hash
   identically after recursive canonicalization.
4. List order remains significant, and scalar representations such as `1` and
   `1.0` are not normalized into the same digest.
5. Unsupported nested values and nested dict keys that are not `str` raise
   `TypeError`.
6. The standalone public function `hash_model_payload(...)` is no longer part
   of the allowed public import surface.
7. `model_registry/__init__.py` does not re-export the hashing owner.
8. Repo-visible documents describe the class-first public owner consistently.

## Behavioral Scenarios

### Scenario 1: Stable hash for equivalent nested payload content
- **Given**: two top-level `dict[str, JSONLike]` payloads containing the same
  nested data but different dict insertion order
- **When**: `ModelPayloadHasher().hash_model_payload(...)` is called for each
  payload
- **Then**: both calls return the same SHA-256 lowercase hex digest
- **Then**: nested dict ordering differences do not change the result

### Scenario 2: Removed function-first public surface
- **Given**: the hashing core is imported from
  `async_model_gateway.model_registry.model_payload`
- **When**: a caller inspects the allowed public surface
- **Then**: `ModelPayloadHasher` is available
- **Then**: `hash_model_payload` is not exposed from that public package

### Scenario 3: Unsupported nested content fails closed
- **Given**: a payload tree that contains either an unsupported value type or a
  nested dict key that is not `str`
- **When**: `ModelPayloadHasher().hash_model_payload(...)` is called
- **Then**: the call raises `TypeError`
- **Then**: no fallback coercion or semantic normalization occurs

## Error / Edge Cases

- Empty top-level payloads and nested empty dict / list structures still
  produce deterministic SHA-256 lowercase hex output.
- Scalar representations are preserved literally for hashing, so payloads that
  differ only by `1` versus `1.0` remain distinguishable.
- Unsupported values still fail with `TypeError` even when they appear several
  levels deep in nested list / dict structures.
- Repo-visible documents must not keep the stale function-first wording after
  the class-first contract lands.
