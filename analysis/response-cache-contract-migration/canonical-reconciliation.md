# response-cache-contract-migration — Canonical Reconciliation

## Authority and routing

- This file is the strict, row-level authority for reconciling the current response-cache
  surface with the target contract. It must be read with
  `analysis/response-cache-contract-migration/technical-spec.md` before implementation.
- `requirements.md` remains the business guardrail. `technical-spec.md` remains the execution
  source of truth for signatures, ownership, failure translation, and concurrency. This file is
  authoritative only for the current/target/migration/compatibility mapping below; the technical
  specification may link to it but must not silently reproduce or alter a row.
- There is no human override. A proposed normal path, legacy import, affected source/test/doc
  path, or mapping that is absent here requires plan rework before implementation.

## Canonical mapping

| Current surface or behavior | Target contract | Required migration | Compatibility and terminal evidence |
| --- | --- | --- | --- |
| Package root exports `ResponseCache`, `ResponseCacheEntry`, `ResponseCacheKey`, and `ResponseCacheKeyFactory`. | Package root exports only `ResponseCache`, `CacheKey`, `CacheHit`, `CacheMiss`, `Remembered`, `Skipped`, and `Failed`; only `ResponseCache` is a facade. | Change `response_cache/__init__.py`; replace first-party normal imports with target names. | Root absence tests prove all four legacy names are absent. The only legacy type route is `response_cache.compat` until the separately approved removal change. |
| `ResponseCache.get(*, key) -> ResponseCacheEntry | None`. | `lookup(*, key: CacheKey, context: ContextT) -> CacheHit | CacheMiss`. | Normal callers branch on `CacheHit`/`CacheMiss`; context is invocation-only. | `LegacyResponseCacheAdapter.get` maps hit to `ResponseCacheEntry(response=value)` and miss to `None`; it neither saves nor examines context. |
| `ResponseCache.set(*, key, entry) -> None`. | `remember(*, key: CacheKey, value: str, context: ContextT) -> Remembered | Skipped | Failed`. | Normal callers use a string and branch on the closed result union. | Adapter `set` returns `None` only for `Remembered`; `Skipped(CLOSED)` raises `LegacyCacheClosedError`; `Failed(kind)` raises `LegacyCacheOperationError(kind)`. It neither saves nor examines context. |
| `ResponseCache.invalidate(*, key) -> bool`. | `CacheInvalidator.invalidate(*, key: CacheKey) -> Invalidated | NotFound`; it is not a facade method. | Move every normal invalidation caller to the separately composed invalidator. | Adapter `invalidate` maps `Invalidated` to `True` and `NotFound` to `False`; operational errors and cancellation still propagate. |
| `ResponseCacheKey` and `ResponseCacheKeyFactory` make identity through a feature-hasher collaborator. | `CacheKey(namespace, model_payload_hash, feature_hash)` is the sole identity/hash authority. | Construct `CacheKey` only from already-derived identity components; stop factory-owned feature hashing in normal cache work. | `compat.ResponseCacheKey` is an alias of `CacheKey`; `compat.ResponseCacheKeyFactory` and its `FeatureHasher`/`CanonicalFeatureHasher` are deprecated migration-only helpers. Direct old key/factory module imports are absence-tested. |
| `_canonical_feature_hasher.py` and `ports/feature_hasher.py` canonicalize features for the old factory. | No target cache collaborator hashes features. Feature hash arrives as a `CacheKey` field. | Delete both modules and remove normal feature-hasher imports. | Compatibility-only helper classes live in `compat.py`; direct imports of the deleted modules are absence-tested, and only `compat` exports the legacy helper surface. |
| `ResponseCacheEntry(response: str)` is the public cache value. | Public value is `str`; persistence uses `StoredCacheRecord`. | Delete `entry.py` and make target callers use string values / `CacheHit.value`. | `compat.ResponseCacheEntry` is a frozen one-field wrapper only for legacy adapter calls. Direct `entry` module import is absence-tested. |
| `ResponseCacheStore.get/set/invalidate` carries entry values and a boolean invalidation result. | `CacheStore.get/set/delete/delete_if_version` carries coherent whole `StoredCacheRecord` snapshots; `CacheInvalidator` owns invalidation results. | Replace store implementations and tests; no root or ports-root store export. | Adapter owns old method shape only; target store ports do not provide legacy aliases. |
| `FreshnessPolicy.is_fresh(written_at, now)` and `TtlFreshnessPolicy` decide fresh/stale at read time; in-memory store owns `_utc_now()`. | Retained internal `FreshnessPolicy.expires_at(written_at) -> datetime` derives a write-time expiry. `TtlFreshnessPolicy` is the retained positive-TTL implementation. `ResponseCache` is the unique injected aware-UTC clock owner. | Replace `is_fresh` tests and calls with expiry construction; delete `_in_memory_store._utc_now`; read compares stored `expires_at` without renewal. | No legacy freshness adapter or public export. Tests prove old `is_fresh` and old helper are absent, and fresh/stale boundary behavior remains covered through the target record path. |
| `InMemoryResponseCacheStore` stores entry plus write time, performs non-versioned stale deletion, and participates in boolean invalidation. | Internal in-memory `CacheStore` stores full records, replaces one complete record per key, and atomically compare-deletes only its observed version token. | Migrate its storage and race tests; compose a separate invalidator over `CacheStore.delete`. | It is never root-exported. The old class name is not preserved except through `compat` if a legacy test requires construction; otherwise direct old behavior is absence-tested. |
| Store/codec/token errors either propagate implicitly or have no closed classification. | Backend adapters raise only `CacheOperationalError` subclasses for expected operational conditions: `CacheStoreOperationalError`, `CacheClosedStoreError`, `CacheCodecOperationalError`, and `CacheVersionTokenOperationalError`. | Add the family in `errors.py`; each adapter translates its own expected backend error before it reaches the facade. | Lookup translates all family members to miss. Remember maps closed-store to `Skipped(CLOSED)` and the other three kinds to `Failed(STORE|CODEC|VERSION_TOKEN)`. Invalidator never translates them. Tests classify every kind and propagation route. |
| Documentation describes keyed entry `get`/`set`/`invalidate` as the normal response-cache boundary. | Documentation describes target facade, record/store ownership, context non-persistence, separate invalidator, and temporary adapter removal. | Update only `README.md`, `docs/architecture.md`, and `docs/specs/response-cache-boundary.md` after target source/tests pass. | No document may present a direct legacy import or facade method as normal. Removal change deletes adapter wording with `compat.py`. |

## Compatibility submodule contract

`async_model_gateway.response_cache.compat` has exactly this direct-import surface:

```python
__all__ = [
    "CanonicalFeatureHasher",
    "FeatureHasher",
    "LegacyCacheClosedError",
    "LegacyCacheOperationError",
    "LegacyResponseCacheAdapter",
    "ResponseCacheEntry",
    "ResponseCacheKey",
    "ResponseCacheKeyFactory",
]
```

- `ResponseCacheKey` aliases `CacheKey`; `ResponseCacheEntry` is the legacy frozen wrapper; and
  the factory/helpers exist only to let a legacy caller form that key during the transition.
- Constructing `LegacyResponseCacheAdapter` or `ResponseCacheKeyFactory` emits
  `DeprecationWarning` with the target replacement (`CacheKey`, `ResponseCache.lookup`,
  `ResponseCache.remember`, or `CacheInvalidator`) and a `stacklevel` that identifies the legacy
  caller. Importing `compat` itself does not emit a warning.
- Adapter construction receives `facade: ResponseCache` and `invalidator: CacheInvalidator`; it
  stores only those collaborators. For `get` and `set` it supplies a private per-call sentinel as
  `context`; the target facade is required to ignore it. No adapter field, record, codec payload,
  metadata, key, log, or result may retain or observe a legacy caller context.
- The terminal removal condition is: first-party imports and documentation no longer mention the
  names above; root and direct-old-module absence tests pass; compatibility mapping tests have
  become absence tests; and a separately approved change deletes `compat.py`, its warnings, its
  tests, and all legacy aliases together.
