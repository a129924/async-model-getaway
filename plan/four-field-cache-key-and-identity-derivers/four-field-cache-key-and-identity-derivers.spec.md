# four-field-cache-key-and-identity-derivers Specification

## Acceptance Criteria

1. Public `CacheKey` is frozen/slotted and has exactly the ordered fields
   `namespace`, `model_identity_hash`, `feature_hash`, and
   `prediction_input_hash`; the former payload field and three-field constructor
   are absent.
2. The local response projection obtains model identity only from
   `RegistryEntry.model_identity_hash` after existing freshness resolution. It
   does not alter registry lookup, policy, upsert, result shape, payload hash,
   or identity-hasher behavior.
3. Private local identity derivers, including `FeatureIdentityHasher`, produce
   deterministic feature, prediction input, namespace, and dumb four-value key
   assembly without public exports or raw identity material in key fields.
   Every non-`str` feature key or value raises `TypeError` fail-closed.
4. Invalid local feature or JSON-like invocation identity fails closed before
   the first registry await and before cache lookup, execution, conversion, or
   remember; the existing shallow invocation snapshot is still the one shared
   with execution.
5. `LocalResponseGateway` no longer accepts an injected cache-key deriver; all
   repository callers and the public type witness use the migrated constructor.
6. `response_cache.compat.LegacyResponseCacheAdapter` and its necessary
   entry/error/operation bridge remain available and accept four-field keys as
   opaque values. Only `ResponseCacheKey`, feature-hasher/factory helpers, and
   their routes are removed; no new key adapter, alias, dual-read/dual-write,
   or record migration is added. The modified migration-contract and
   package-surface tests assert the same retained compat scope and cover bridge
   operation behavior with supplied four-field keys.
7. Cache/store/invalidator operational behavior, unchanged package-root exports,
   local ONNX guard behavior, and direct-await execution semantics remain
   unchanged. After a local cache miss, `Remembered`, `Skipped`, and `Failed`
   each return the generated response fail-open without another execution or
   conversion.
8. This replan invalidates any current plan-review, human-check, and RED-test
   evidence. Implementation resumes only after fresh reviewer verdict, fresh
   human check, and Tester reconfirmation or update of RED evidence, in order.

## Behavioral Scenarios

### Scenario 1: Four independent identities prevent a false local cache hit

- **Given**: two otherwise equal local requests differ in exactly one of
  namespace, registry `model_identity_hash`, feature material, or invocation
  material.
- **When**: each request reaches the internal local identity derivation.
- **Then**: the keys are unequal, the changed request cannot reuse the earlier
  response, and no raw changed material appears in any key field.

### Scenario 2: Complete registry identity is authoritative

- **Given**: freshness returns a `RegistryEntry` with its existing derived
  complete identity.
- **When**: the local gateway assembles the cache key.
- **Then**: the key receives that exact `model_identity_hash`, not
  `payload_hash`, a reconstructed hash, or a new registry result field.

### Scenario 3: Invalid identity input is side-effect free

- **Given**: local feature or invocation material cannot satisfy the locked
  internal canonical identity contract.
- **When**: `LocalResponseGateway.generate()` begins.
- **Then**: the exact failure propagates before registry freshness, cache,
  executor, converter, or remember is observed.

### Scenario 4: Feature mapping rejects unsupported key and value types

- **Given**: feature material contains either a non-`str` key or a non-`str`
  value.
- **When**: `FeatureIdentityHasher` derives feature identity.
- **Then**: it raises `TypeError` without coercion, omission, stringification,
  cache miss conversion, or any gateway collaborator call.

### Scenario 5: Migration removes only the three-field legacy routes

- **Given**: a caller uses the supported local gateway and response-cache
  package surfaces after migration.
- **When**: it inspects constructors or imports former compatibility symbols.
- **Then**: it can construct the gateway without a key deriver; old
  `cache_key_deriver`, `ResponseCacheKey`, feature-hasher, and factory imports
  are unavailable, while the retained compat entry/error/operation bridge is
  importable, covered by migration regression, and consumes the four-field key
  opaquely. Package-surface and migration assertions describe the same retained
  compat names.

### Scenario 6: Fail-open remembered-write outcomes preserve the response

- **Given**: a local cache miss has executed and converted one response.
- **When**: `ResponseCache.remember()` yields `Remembered`, `Skipped`, or
  `Failed`.
- **Then**: the gateway returns that generated response without re-executing or
  re-converting it.

### Scenario 7: Replan reopens the implementation-entry gates

- **Given**: this replan changes the locked compat boundary.
- **When**: a prior plan-review, human-check, or RED-test evidence artifact is
  considered for implementation entry.
- **Then**: it is not current evidence; Plan-Reviewer, Human, and Tester must
  respectively provide fresh review, clearance, and reconfirmed or updated RED
  evidence before an Implementer is assigned or implementation resumes.

## Error / Edge Cases

- A key changes equality and hashing if any of its four literal fields changes;
  no normalization, context, or implicit identity material is accepted.
- A non-JSON-like nested invocation value is not coerced, skipped, converted to
  a cache miss, or executed after identity failure.
- A non-`str` feature key or value is not coerced, stringified, omitted, or
  converted into a cache miss; `FeatureIdentityHasher` raises `TypeError`.
- Existing expired/unsupported-record cleanup, cache operational failure
  translation, and cancellation propagation remain response-cache behavior;
  local identity derivation adds no new async policy.
- The retained legacy operation bridge does not solve old-key records or derive
  identity; it only consumes a supplied four-field key opaquely. Old-key
  record transformation remains outside this topic.
- `Skipped` and `Failed` are intentional local remember outcomes, not gateway
  errors: the produced response must still be returned exactly once.
- Tests must not use dynamic module loading to imitate deleted imports or avoid
  collection behavior.
