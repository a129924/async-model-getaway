# response-cache-expired-record-reclamation Specification

## Acceptance Criteria

1. `InMemoryResponseCacheStore.get(...)` returns `None` for an existing record only after its injected `FreshnessPolicy.is_fresh(...)` returns `False`, and it removes exactly that key's internal record before returning the miss.
2. After reclamation, a repeat lookup of the same key returns `None` without calling the policy again; a subsequent `set(...)` for that key creates a new record that can be returned when the policy reports fresh.
3. A `True` policy result returns the original entry and preserves the record. A policy exception propagates unchanged, does not become a miss, and does not remove the record.
4. Reclaiming one stale key does not affect another key's fresh record. Existing successful-write timestamp, read non-renewal, overwrite, and missing-key semantics remain intact.
5. No public API, `ResponseCacheStore` signature, package export, freshness/TTL policy, dependency, version, settings, capacity/eviction, lifecycle, persistence, or orchestration behavior changes.

## Behavioral Scenarios

### Scenario 1: Lookup reclaims a confirmed stale record

- **Given**: an internal store has one successfully written record and its injected policy will return `False` for that record.
- **When**: a caller awaits `get(...)` with the same key.
- **Then**: the result is `None`, the record is removed, and a second lookup returns `None` without another policy decision.

### Scenario 2: Reclaimed key accepts a new record

- **Given**: a prior lookup reclaimed a stale record for one key.
- **When**: a caller writes a replacement entry for that key and the policy later returns `True`.
- **Then**: `get(...)` returns that replacement entry normally.

### Scenario 3: Policy failure preserves the record

- **Given**: a successfully written record and a policy that raises an exception on its first decision, then returns `True` on a later decision.
- **When**: the first caller awaits `get(...)`, then a second caller awaits `get(...)` with the same key.
- **Then**: the first call raises the original exception; the second returns the original entry, proving the first call did not reclaim it.

### Scenario 4: Reclamation is key-local

- **Given**: one stale record and one fresh record stored under distinct keys.
- **When**: the stale key is looked up and reclaimed.
- **Then**: the fresh key remains stored and returns its original entry when looked up.

## Error / Edge Cases

- Policy exceptions are not equivalent to a `False` stale decision. They must propagate without wrapping and must leave the record intact.
- A missing key remains an ordinary `None` miss and does not invoke the policy or create/delete any record.
- Reclamation is limited to the lookup key after a completed `False` decision. It must not become background cleanup, capacity eviction, public deletion, or cross-key cleanup.
- The existing `FreshnessPolicy` and `TtlFreshnessPolicy` remain the sole freshness authority; the store does not calculate expiry or alter timestamps.
- Tests import the internal store directly. Dynamic module loading is prohibited, and no public package export may be added to make tests work.
