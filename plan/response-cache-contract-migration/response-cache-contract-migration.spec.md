# response-cache-contract-migration Specification

## Acceptance Criteria

1. `ResponseCache` has exactly the two keyword-only async methods `lookup(*, key, context)` and
   `remember(*, key, value, context)` with the frozen union return types in the technical spec;
   there is no root-public `get`, `set`, or `invalidate` facade method.
2. `CacheKey` alone determines cache identity and hashing. Distinct contexts cannot affect key
   equality/hash, stored record content, codec payload, metadata, expiry, or version token.
3. Every `StoredCacheRecord` is immutable and validates schema/codec/payload, aware-UTC write and
   expiry timestamps, opaque per-write token, and the fixed metadata limits.
4. A `CacheStore` implements coherent reads, whole-record replacement, key-local delete, and
   atomic compare-delete. A stale cleanup racing a later remember never deletes the later record.
5. Lookup gives `CacheHit` only for a supported fresh decoded record. Absent, expired, unsupported,
   and known operational failure paths yield `CacheMiss`; cleanup failure remains miss; cancellation
   and defects propagate.
6. Remember returns `Remembered`, `Skipped(CLOSED)`, or a closed `Failed` kind as specified; it
   neither swallows cancellation nor converts programmer/configuration defects into outcomes.
7. Invalidation is exposed only through `CacheInvalidator`, with `Invalidated`/`NotFound` semantics
   and no participation in `ResponseCache`'s root facade.
8. The deprecated legacy adapter is the only old-surface route and meets the terminal removal
   condition before a later removal change can delete it. No test uses dynamic module loading.
9. `ResponseCache` is constructed only with keyword-only store, codec, version-token factory,
   retained expiry policy, and injected clock collaborators. It alone calls the clock once per
   successful remember path, validates aware UTC, derives `expires_at`, reads `codec_id`, creates
   the version token, and supplies empty metadata; no context is retained or observed.
10. `CacheOperationalError` lives only in `response_cache/errors.py`: store (including the
    closed-store signal), codec, and version-token subclasses are independently test-classifiable.
    Lookup maps them to miss, remember maps closed store to `Skipped(CLOSED)` and the others to
    the matching `Failed` kind, while invalidation and cancellation propagate.
11. The retained internal `FreshnessPolicy` derives write-time expiry and
    `TtlFreshnessPolicy` preserves strict positive TTL behavior. No read-time `is_fresh` or
    in-memory clock owner remains.

## Behavioral Scenarios

### Scenario 1: Fresh lookup is context-independent

- **Given**: a fresh supported record for one `CacheKey` and two unequal context instances.
- **When**: each caller awaits `lookup` with that key and its context.
- **Then**: each receives the same `CacheHit(value)`, and neither context is retained or serialized.

### Scenario 2: Remember replaces one complete record

- **Given**: an existing record for a key.
- **When**: a caller awaits `remember` with a new response.
- **Then**: the store receives one new complete envelope with a new opaque token and returns
  `Remembered`; later lookup decodes only the replacement value.

### Scenario 3: Stale cleanup cannot delete a concurrent replacement

- **Given**: lookup has read an expired record with token A and another caller writes a fresh
  replacement with token B before cleanup executes.
- **When**: the original lookup runs cleanup.
- **Then**: `delete_if_version(key, A)` does not delete token B, and the original lookup remains
  `CacheMiss`.

### Scenario 4: Operational outcomes are deliberately closed

- **Given**: cache/store/codec collaborators that report known store, codec, token, and closed
  conditions.
- **When**: callers invoke lookup or remember.
- **Then**: lookup is `CacheMiss`; closed remember is `Skipped(CLOSED)`; other remember failures
  are `Failed` with the matching closed kind; no timeout/retry/background behavior is introduced.

### Scenario 5: Cancellation remains caller-owned

- **Given**: an awaited store operation that raises `asyncio.CancelledError`.
- **When**: lookup, remember, or invalidation is awaited.
- **Then**: cancellation reaches the caller unchanged and no outcome translation, retry, shield,
  or background cleanup occurs.

### Scenario 6: Legacy callers have one temporary bridge

- **Given**: an old caller importing only the documented compatibility submodule.
- **When**: it uses legacy `get`, `set`, or `invalidate`.
- **Then**: the adapter maps to the target facade/invalidator according to the technical spec,
  emits its deprecation signal, and package-root imports do not expose the old normal path.

### Scenario 7: One facade owns generated record values

- **Given**: a facade with a recording aware-UTC clock, codec, version-token factory, and expiry
  policy, and a context object whose access would fail the test.
- **When**: the caller awaits `remember`.
- **Then**: the facade calls the clock once, supplies `written_at`, later `expires_at`, codec id,
  encoded bytes, new token, and empty metadata in one stored record; the context is not accessed
  or retained.

### Scenario 8: Legacy maps do not create a context channel

- **Given**: a direct import of `response_cache.compat` and an adapter configured with target
  facade plus invalidator.
- **When**: it constructs the adapter/factory and calls old `get`, `set`, and `invalidate`.
- **Then**: construction emits `DeprecationWarning`; get and set supply only an ignored private
  sentinel; results map exactly as reconciled; invalidation has no context; and neither adapter nor
  target persistence values expose a legacy caller context.

## Error / Edge Cases

- Unsupported schema, expired record, decode failure, read failure, and cleanup failure are all
  lookup misses; a cleanup failure cannot change that result to an exception or hit.
- Invalid timestamp ordering, invalid metadata bounds, non-UTC timestamps, malformed identity,
  and configuration errors are defects and propagate rather than becoming cache outcomes.
- Compare-delete must fail harmlessly when the observed token no longer matches; unconditional
  stale deletion is prohibited.
- Invalidation is key-local, returns `NotFound` for absence, and never derives identity or consumes
  a context.
- Direct imports are required in tests; dynamic module loading is prohibited.
- Direct old module routes are removed by the declared file deletions. Tests verify root and
  `compat` surfaces with ordinary imports and source/path disposition, never dynamic imports.
