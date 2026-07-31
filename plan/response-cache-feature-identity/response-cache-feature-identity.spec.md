# response-cache-feature-identity Specification

## Acceptance Criteria

1. `CanonicalFeatureHasher` exists only in `async_model_gateway.response_cache._canonical_feature_hasher`, implements the unchanged `FeatureHasher` port, and is not re-exported by either response-cache package root.
2. It validates every runtime mapping key and value as `str`, sorts entries by unmodified key, serializes the sorted sequence of string pairs with JSON `ensure_ascii=False` and compact separators, UTF-8 encodes that representation, and returns `hashlib.sha256(...).hexdigest()` as lowercase hexadecimal.
3. Equivalent `Mapping[str, str]` collections produce the same digest irrespective of insertion order. The empty mapping canonicalizes to `[]` and produces `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`.
4. A changed feature key or value changes identity in representative cases. Whitespace, case, and Unicode differences are preserved rather than coerced, trimmed, casefolded, or normalized.
5. A non-`str` key or value raises `TypeError` before a digest is returned; direct factory use with the concrete hasher propagates that failure and does not construct a key.
6. `ResponseCacheKeyFactory` remains unchanged and, when injected with this concrete hasher, preserves literal `namespace` and `model_payload_hash` while receiving the hasher's digest.

## Behavioral Scenarios

### Scenario 1: Equivalent capability collection has a stable identity

- **Given**: two mappings containing `mode: chat` and `safety: strict` with opposite insertion order.
- **When**: a caller hashes each mapping with `CanonicalFeatureHasher`.
- **Then**: both use the canonical JSON sequence `[["mode","chat"],["safety","strict"]]` before UTF-8 SHA-256 hashing and return the same lowercase hex digest.

### Scenario 2: Concrete hasher participates through the existing factory

- **Given**: `ResponseCacheKeyFactory(CanonicalFeatureHasher())`, a literal namespace, an upstream payload hash, and a valid feature mapping.
- **When**: the caller invokes the unchanged keyword-only `build(...)` method.
- **Then**: the returned `ResponseCacheKey` retains the supplied namespace and payload hash exactly and uses the concrete feature digest.

### Scenario 3: Invalid runtime identity material fails closed

- **Given**: a mapping containing a non-string key or non-string value.
- **When**: it is hashed directly or passed to a factory injected with `CanonicalFeatureHasher`.
- **Then**: `TypeError` escapes, no normalization/coercion/fallback is applied, and the factory returns no `ResponseCacheKey`.

## Error / Edge Cases

- An empty mapping is valid and must preserve the frozen `[]` golden digest.
- Sorting happens only after runtime type validation so mixed key types cannot produce an incidental sorting exception or an ambiguous serialization.
- Unicode, whitespace, and case are valid raw strings but semantically distinct hashing material.
- Tests import `_canonical_feature_hasher` directly; dynamic module loading is prohibited.
- Any request to expose the concrete class, modify port/factory/key contracts, share model-payload hashing, add TTL/store/orchestrator behavior, change digest versioning, or serialize with a different canonical form is out of scope and requires replanning.
