# response-cache-freshness-policy Specification

## Acceptance Criteria

1. `FreshnessPolicy` remains internal and offers only `is_fresh(*, written_at, now) -> bool`; no root or `ports` package re-export exposes it.
2. `TtlFreshnessPolicy` accepts only a strictly positive `timedelta`, raises `ValueError` for zero or negative values, and returns true only before `written_at + ttl`.
3. `InMemoryResponseCacheStore` implements the existing async `ResponseCacheStore` port without changing its signatures, writes an aware-UTC timestamp when an entry is stored, and receives its freshness policy by keyword-only injection.
4. A read evaluates the original write timestamp, never extends it, returns `None` when expired, and never returns stale `ResponseCacheEntry` content.
5. `ResponseCache`, `ResponseCacheEntry`, `ResponseCacheKey`, `ResponseCacheKeyFactory`, `ResponseCacheStore`, key/hash ownership, root/ports exports, version metadata, and dependency set remain unchanged.

## Behavioral Scenarios

### Scenario 1: Fresh response-cache hit

- **Given**: an `InMemoryResponseCacheStore` with `TtlFreshnessPolicy(timedelta(seconds=30))` and a stored key/entry whose internal write time is ten seconds before the read.
- **When**: the caller awaits `get(key=...)`.
- **Then**: the store returns that same entry and the recorded write time remains unchanged.

### Scenario 2: Exact expiry is a normal miss

- **Given**: an entry written at an aware-UTC instant and a TTL of 30 seconds.
- **When**: the store evaluates a read whose `now` equals write time plus 30 seconds.
- **Then**: the policy reports not fresh and the store returns `None`, without returning the entry or adding eviction behavior.

### Scenario 3: Public boundary remains closed

- **Given**: the existing response-cache package and ports package roots.
- **When**: their `__all__` and attributes are inspected after the internal implementation exists.
- **Then**: they expose exactly their existing public surfaces and do not expose `FreshnessPolicy`, `TtlFreshnessPolicy`, or `InMemoryResponseCacheStore`.

## Error / Edge Cases

- `timedelta(0)` and any negative TTL fail fast with `ValueError`; they do not create a policy that treats entries as fresh.
- A `now` after expiry is also a miss, even when the internal record still exists; this topic neither deletes it nor specifies eviction.
- An overwrite replaces the stored entry and establishes a new write timestamp; a prior read cannot renew either timestamp.
- No test may use dynamic module loading to reach the internal implementation; tests use ordinary direct imports.
- Any requested public re-export, timestamp field on `ResponseCacheEntry`, port signature change, capacity/eviction behavior, external I/O, timeout, retry, cancellation wrapper, or async lock is out of scope and requires replanning.
