# response-cache-explicit-key-invalidation Specification

## Acceptance Criteria

1. `ResponseCache` exposes exactly `async def invalidate(self, *, key: ResponseCacheKey) -> bool`, directly awaits its configured store with the unchanged key, returns the store boolean unchanged, and propagates store errors and cancellation unchanged.
2. `ResponseCacheStore` exposes the same async keyword-only method only from `async_model_gateway.response_cache.ports.store`; package-root and ports-root exports remain unchanged.
3. `InMemoryResponseCacheStore.invalidate(...)` returns `True` only for an existing record whose injected `FreshnessPolicy.is_fresh(...)` returns `True`, and removes exactly that key.
4. An absent key returns `False` without a policy call. An existing record whose policy returns `False` is reclaimed first and returns `False`; a later invalidation after either fresh removal or stale reclamation remains absent and returns `False` without another policy call.
5. A policy exception or cancellation propagates unchanged and leaves the record intact. Explicit invalidation of one key cannot remove or alter another key's record.
6. `ResponseCache.get(...)` remains `ResponseCacheEntry | None`; existing identity, TTL, features, payload, entry, `get`/`set`, exports, lookup-time reclamation, and documentation exclusions remain unchanged except for the exact explicit-key invalidation wording.
7. Only `src/async_model_gateway/response_cache/_in_memory_store.py` may use private `_CacheLookupDecision(str, Enum)` with `HIT` and `MISS`: `match` maps `HIT` to the fresh entry and `MISS` to `None` for absent or policy-confirmed stale reclamation. Policy exception, cancellation, and unexpected errors propagate rather than becoming `MISS`; the enum is prohibited from `ResponseCache`, `ResponseCacheStore`, port signatures, exports, and public documentation APIs.

## Behavioral Scenarios

### Scenario 1: Facade delegates explicit-key invalidation

- **Given**: a `ResponseCache` with a configured `ResponseCacheStore` that records its received key and returns `True`.
- **When**: a caller awaits `response_cache.invalidate(key=key)`.
- **Then**: the store receives the same key exactly once and the facade returns `True` without adding failure handling or other async work.

### Scenario 2: Fresh record is explicitly invalidated

- **Given**: an `InMemoryResponseCacheStore` with an existing record whose injected policy returns `True`.
- **When**: a caller awaits `invalidate(key=key)`.
- **Then**: exactly that record is removed and the result is `True`.

### Scenario 3: Absent and stale records are unsuccessful invalidations

- **Given**: first, an absent key; then, a separately stored key whose policy returns `False`.
- **When**: each key is invalidated.
- **Then**: the absent key returns `False` without a policy call; the stale record is reclaimed and returns `False`; repeat calls after both stale reclamation and a prior fresh successful invalidation see an absent record and return `False` without another policy call.

### Scenario 4: Failed freshness decision preserves the record

- **Given**: an existing record and a policy that first raises an exception or cancellation, then reports `True`.
- **When**: the first caller awaits invalidation, then a later caller retries with the same key.
- **Then**: the first call raises the unchanged failure and does not remove the record; the later call returns `True` and removes it.

### Scenario 5: Invalidation remains key-local and port exposure remains narrow

- **Given**: two records under distinct keys and the response-cache package surfaces.
- **When**: one fresh key is invalidated and callers inspect public imports.
- **Then**: only the requested key is removed; the other remains readable; `ResponseCacheStore` remains available only from `response_cache.ports.store`.

### Scenario 6: Lookup HIT preserves its existing public union contract

- **Given**: an in-memory record whose freshness policy returns `True`.
- **When**: a caller performs lookup.
- **Then**: private `HIT` is matched to the existing fresh `ResponseCacheEntry`, and the public lookup contract remains `ResponseCacheEntry | None`.

### Scenario 7: Lookup treats completed stale reclamation as MISS

- **Given**: an in-memory record whose freshness policy returns `False`.
- **When**: a caller performs lookup.
- **Then**: the record is reclaimed and private `MISS` is matched to `None`.

### Scenario 8: Lookup treats an absent record as MISS without policy access

- **Given**: an in-memory store without a record for the lookup key and a policy test double that records calls.
- **When**: a caller performs lookup.
- **Then**: private `MISS` is matched to `None` and the policy test double receives no call.

### Scenario 9: Lookup does not treat a policy failure as MISS

- **Given**: an in-memory record and a freshness policy that raises an exception, cancellation, or another unexpected error.
- **When**: a caller performs lookup.
- **Then**: the unchanged error propagates and no `MISS` is produced.

### Scenario 10: Lookup tests retain ordinary imports

- **Given**: the declared response-cache test modules.
- **When**: lookup decision coverage is added.
- **Then**: tests use normal direct imports and no dynamic module loading.

## Error / Edge Cases

- Policy `False` is a completed stale decision, not an error and not a successful explicit invalidation; it requires reclamation followed by `False`.
- Policy exceptions and `CancelledError` are not stale signals. They propagate without wrapping, retries, cleanup, or deletion.
- A facade store error or cancellation propagates unchanged. `ResponseCache` does not convert it to `False`.
- No operation may create keys, recalculate identity, renew TTL, modify entries, clear other records, schedule cleanup, or add locks/tasks.
- Tests use direct imports of the internal store and ordinary test doubles only; dynamic module loading is prohibited.
