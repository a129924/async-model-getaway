# response-cache-feature-identity Specification

## Acceptance Criteria

1. `CanonicalFeatureHasher` exists only in `async_model_gateway.response_cache._canonical_feature_hasher`, implements the unchanged `FeatureHasher` port, and is not re-exported by either response-cache package root.
2. It validates every runtime mapping key and value as `str`; for every accepted built-in string or `str` subclass, it obtains the identity material with `str.__str__(key)` and `str.__str__(value)` without calling an override of `__str__`; then it sorts that built-in material by key.
3. It serializes the sorted sequence of base-string pairs with JSON `ensure_ascii=False` and compact separators, strictly UTF-8 encodes the exact serialization, and returns `hashlib.sha256(...).hexdigest()` as lowercase hexadecimal. The empty mapping remains `[]` and produces `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`.
4. Equivalent `Mapping[str, str]` collections produce the same digest irrespective of insertion order, `str` subclass comparison behavior, or overridden `__str__`; a changed base key or value remains a distinct identity even if subclass `__str__` overrides would produce the same text.
5. A non-`str` key or value raises `TypeError` before a digest is returned. An accepted string that makes the canonical serialization fail strict UTF-8 encoding, including an unpaired surrogate, raises `TypeError` with the original `UnicodeEncodeError` as its direct cause.
6. `ResponseCacheKeyFactory` remains unchanged. When injected with the concrete hasher, it preserves literal `namespace` and `model_payload_hash`, constructs no key on either hasher failure, and propagates the hasher's `TypeError` and chained cause without catching, wrapping, or translating them.

## Behavioral Scenarios

### Scenario 1: Equivalent capability collection has a stable identity

- **Given**: two mappings containing `mode: chat` and `safety: strict` with opposite insertion order.
- **When**: a caller hashes each mapping with `CanonicalFeatureHasher`.
- **Then**: both use the canonical JSON sequence `[["mode","chat"],["safety","strict"]]` before UTF-8 SHA-256 hashing and return the same lowercase hex digest.

### Scenario 2: A hostile string subclass cannot alter identity material

- **Given**: a `str` subclass for a feature key/value that overrides `__str__` to return different or colliding text, and an equivalent mapping of built-in strings.
- **When**: a caller hashes both mappings.
- **Then**: the subclass override is not invoked; the digest is derived from the subclass's base-string content and equals the built-in mapping's digest. Distinct base-string content remains distinct even if the override returns the same text for both.

### Scenario 3: Concrete hasher participates through the existing factory

- **Given**: `ResponseCacheKeyFactory(CanonicalFeatureHasher())`, a literal namespace, an upstream payload hash, and a valid feature mapping.
- **When**: the caller invokes the unchanged keyword-only `build(...)` method.
- **Then**: the returned `ResponseCacheKey` retains the supplied namespace and payload hash exactly and uses the concrete feature digest.

### Scenario 4: Non-UTF-8-encodable identity material fails closed

- **Given**: a feature mapping containing a valid `str` with an unpaired surrogate.
- **When**: it is hashed directly or passed to a factory injected with `CanonicalFeatureHasher`.
- **Then**: the strict UTF-8 boundary raises `TypeError` from the original `UnicodeEncodeError`; no digest or `ResponseCacheKey` is returned, and the factory adds no wrapper.

## Error / Edge Cases

- An empty mapping is valid and must preserve the frozen `[]` golden digest.
- Sorting happens only after runtime type validation and base-string material extraction, so mixed key types cannot produce an incidental sorting exception and subclass comparisons cannot alter ordering.
- Valid Unicode, whitespace, and case are preserved as raw identity material. `ensure_ascii=False` remains required; changing it to avoid a surrogate error is forbidden.
- The implementation catches only `UnicodeEncodeError` from strict UTF-8 encoding and raises `TypeError` with exception chaining. It does not catch or translate unrelated errors.
- Tests assert direct-hasher and factory-propagation behavior, including `TypeError.__cause__` being a `UnicodeEncodeError`; tests import `_canonical_feature_hasher` directly and dynamic module loading is prohibited.
- Any request to expose the concrete class, modify port/factory/key contracts, share model-payload hashing, add TTL/store/orchestrator behavior, change digest versioning, or serialize with a different canonical form is out of scope and requires replanning.
