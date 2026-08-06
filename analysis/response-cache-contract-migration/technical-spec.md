# response-cache-contract-migration — Technical Specification

## Analysis Routing

- Mode: strict.
- Business guardrail: `analysis/response-cache-contract-migration/requirements.md`.
- Execution source of truth: this file.
- Canonical current-to-target mapping: `analysis/response-cache-contract-migration/canonical-reconciliation.md`.
- Human override: none.
- The reconciliation file is mandatory for any legacy or current-surface decision. A path, import,
  or mapping not declared in it and in the topic plan requires plan rework; it is not an
  implementer discretion.

## Target Contract

### Public facade and value contract

`async_model_gateway.response_cache` re-exports `ResponseCache`, `CacheKey`, and the closed
lookup/write outcome types. It does not re-export any store, codec, token factory, invalidator,
in-memory implementation, compatibility adapter, or legacy type.

```python
ContextT = TypeVar("ContextT")

class ResponseCache:
    def __init__(
        self,
        *,
        store: CacheStore,
        codec: CacheCodec,
        version_token_factory: VersionTokenFactory,
        freshness_policy: FreshnessPolicy,
        clock: Callable[[], datetime],
    ) -> None: ...

    async def lookup(
        self, *, key: CacheKey, context: ContextT
    ) -> CacheHit | CacheMiss: ...

    async def remember(
        self, *, key: CacheKey, value: str, context: ContextT
    ) -> Remembered | Skipped | Failed: ...
```

- `CacheKey` is a frozen, slotted value with exactly `namespace`, `model_payload_hash`, and
  `feature_hash`. It is the sole identity and hash authority.
- `CacheHit(value: str)` and fieldless `CacheMiss` are lookup outcomes.
- `Remembered` is fieldless. `Skipped(reason: CacheSkipReason)` accepts only
  `CacheSkipReason.CLOSED`. `Failed(kind: CacheFailureKind)` accepts only
  `STORE`, `CODEC`, or `VERSION_TOKEN`.
- `context` is not retained after an operation. It must not affect cache identity, hashing,
  stored-record construction, codec payload, metadata, expiry, version token, or cleanup.
- `value` is the existing response string. This migration deliberately does not introduce a
  second public entry/value abstraction.

### Stored record and collaborator ports

```python
@dataclass(frozen=True, slots=True)
class StoredCacheRecord:
    schema_version: int
    codec_id: str
    payload: bytes
    written_at: datetime
    expires_at: datetime
    version_token: CacheVersionToken
    metadata: tuple[tuple[str, str], ...]

class CacheCodec(Protocol):
    codec_id: str
    def encode(self, *, value: str) -> bytes: ...
    def decode(self, *, payload: bytes) -> str: ...

class VersionTokenFactory(Protocol):
    def new(self) -> CacheVersionToken: ...

class CacheStore(Protocol):
    async def get(self, *, key: CacheKey) -> StoredCacheRecord | None: ...
    async def set(self, *, key: CacheKey, record: StoredCacheRecord) -> None: ...
    async def delete(self, *, key: CacheKey) -> bool: ...
    async def delete_if_version(
        self, *, key: CacheKey, version_token: CacheVersionToken
    ) -> bool: ...

class CacheInvalidator(Protocol):
    async def invalidate(self, *, key: CacheKey) -> Invalidated | NotFound: ...
```

```python
class FreshnessPolicy(Protocol):
    def expires_at(self, *, written_at: datetime) -> datetime: ...
```

- `CacheVersionToken` is a frozen opaque value. Only `VersionTokenFactory` constructs it; it
  is not decoded, ordered, serialized to public callers, or supplied by `ResponseCache` callers.
- `schema_version` is exactly `1`; `codec_id` identifies the sole codec used to create the
  payload; both `written_at` and `expires_at` are aware UTC timestamps and `expires_at` is later
  than `written_at`.
- metadata has the bounds from the requirements baseline: at most eight pairs, 64/256 UTF-8
  bytes per key/value, and 2 KiB total. Metadata is record-owned implementation data, not an
  input path for `context`.
- `CacheStore.get` returns one coherent complete record or `None`. `set` is whole-record,
  per-key replacement. `delete_if_version` is atomic compare-delete. `delete` is ordinary
  key-local deletion and is used only by invalidation, never stale cleanup.
- `CacheCodec`, `VersionTokenFactory`, and `CacheStore` ports are submodule-public only.
  `CacheInvalidator` is a separate submodule-public port; it is not an additional facade.
- `ResponseCache` receives exactly five keyword-only collaborators: `store`, `codec`,
  `version_token_factory`, `freshness_policy`, and `clock`. It retains the first four only for
  operations. `clock` is called exactly once by successful-path `remember` before record
  construction; its returned timestamp must be aware UTC or record construction raises its
  ordinary defect unchanged. No store, codec, token factory, invalidator, or policy reads a clock.
  Therefore the facade is the unique owner of `written_at`; it derives `expires_at` by calling the
  retained policy with that same value. It reads `codec.codec_id`, encodes only `value`, obtains
  one new token, and writes metadata as the empty tuple. It never obtains any of these values from
  `context`.
- `FreshnessPolicy` is retained only as the internal write-time expiry collaborator. Its old
  read-time `is_fresh` boundary is replaced: `TtlFreshnessPolicy` computes a strictly later
  `expires_at`, and lookup compares a record's stored timestamp without read renewal. Neither
  policy is package-root or ports-root public.

## Operational Failure Boundary

Backend adapters must translate expected backend/codec/token operational failures into the
closed `CacheOperationalError` family at their owning boundary. Programmer misuse, invariant
violations, malformed cache configuration, and unexpected defects are not members of that family
and propagate unchanged. `asyncio.CancelledError` always propagates unchanged.

`src/async_model_gateway/response_cache/errors.py` owns the family and no other module declares
lookalike operational exceptions:

```python
class CacheOperationalError(Exception):
    kind: CacheFailureKind

class CacheStoreOperationalError(CacheOperationalError): ...       # STORE
class CacheClosedStoreError(CacheStoreOperationalError): ...        # STORE + closed signal
class CacheCodecOperationalError(CacheOperationalError): ...        # CODEC
class CacheVersionTokenOperationalError(CacheOperationalError): ... # VERSION_TOKEN
```

- A concrete store translates its expected backend failures to `CacheStoreOperationalError`; its
  known closed condition is the narrower `CacheClosedStoreError`. The codec and token factory
  respectively translate only their own expected failures. `ResponseCache` does no broad catch:
  it catches this family at its facade boundary and classifies the stored `kind`.
- `lookup` maps every member of the family (including a closed store) to `CacheMiss`. `remember`
  maps `CacheClosedStoreError` to `Skipped(CLOSED)` and the other subclasses to exactly
  `Failed(STORE|CODEC|VERSION_TOKEN)`. A cleanup family error is still miss. The invalidator has
  no outcome translation and propagates all family members. Tests must inject each subclass and
  assert its stated target path.

| Operation / condition | Observable target result | Record side effect |
| --- | --- | --- |
| lookup absent | `CacheMiss` | none |
| lookup fresh supported record | `CacheHit(value)` | none; no read-renewal |
| lookup expired or unsupported-schema record | `CacheMiss` | best-effort `delete_if_version` using observed token |
| lookup codec/store/record operational failure | `CacheMiss` | no mandatory cleanup |
| lookup cleanup operational failure | `CacheMiss` | preserve any concurrent replacement; no retry |
| lookup cancellation or defect | propagate unchanged | no translation |
| remember successful encode/token/store write | `Remembered` | one whole-record replacement with new token |
| remember closed store condition | `Skipped(CLOSED)` | no write |
| remember store/codec/token operational failure | `Failed(STORE|CODEC|VERSION_TOKEN)` | no partial replacement requirement |
| remember cancellation or defect | propagate unchanged | no translation |
| invalidator existing key | `Invalidated` | `CacheStore.delete` removes that key |
| invalidator absent key | `NotFound` | none |
| invalidator operational failure, cancellation, or defect | propagate unchanged | no translated outcome |

## Async and Concurrency Baseline

- The facade and store are async because cache I/O is async-capable. Codec, token construction,
  envelope validation, identity construction, and expiry comparison stay synchronous.
- No component creates a background task, worker, queue, shared client lifecycle, timeout,
  retry, cancellation shield, fan-out, batching, or cross-key coordinator.
- The caller owns cancellation. `ResponseCache` owns no store lifecycle and does not close,
  reset, flush, or reconnect a store. A closed collaborator is reported only through the defined
  `remember -> Skipped(CLOSED)` outcome.
- A stale lookup may observe an old record while another remember replaces it. Cleanup must call
  atomic `delete_if_version` with the observed token, so a new whole-record replacement survives.
  In-memory storage supplies the same coherence and atomicity without background ownership.

## Canonical Reconciliation

The complete row-level current/target/migration/compatibility mapping is deliberately kept in
`analysis/response-cache-contract-migration/canonical-reconciliation.md`. It is strict input to
this specification and the plan; it supersedes the former duplicated table in this file.

## Legacy Compatibility Lifecycle

`LegacyResponseCacheAdapter` is a temporary, explicitly deprecated, submodule-only bridge.
Its exact direct-import surface, warning trigger, constructor collaborators, per-method context
strategy, result/error maps, and terminal removal condition are frozen in the reconciliation file.
It is the exclusive place where the old `get`, `set`, and `invalidate` method names, old key,
factory, entry, and feature-hash helpers can be imported or exercised. It receives the new facade
and separate invalidator; it does not duplicate store/codec/token logic or retain/observe context.

Terminal removal condition: all first-party imports and documentation examples use `CacheKey`,
`lookup`, `remember`, and `CacheInvalidator`; public-export and compatibility tests prove no
root legacy exports remain; migration tests are deleted or rewritten as absence tests; and a
separate approved removal change deletes `compat.py`, legacy aliases, deprecation warnings, and
the old method surface together. Until that change, the adapter must publish a deprecation warning
with its replacement paths and must have no package-root re-export.

## Planned File Placement

| Path | Target responsibility |
| --- | --- |
| `src/async_model_gateway/response_cache/key.py` | `CacheKey` identity authority only; legacy aliases live exclusively in `compat.py` |
| `src/async_model_gateway/response_cache/errors.py` | closed operational error family and closed-store signal |
| `src/async_model_gateway/response_cache/outcomes.py` | closed facade and invalidator outcomes |
| `src/async_model_gateway/response_cache/record.py` | immutable `StoredCacheRecord` and opaque token value |
| `src/async_model_gateway/response_cache/cache.py` | the two-method `ResponseCache` facade and outcome translation |
| `src/async_model_gateway/response_cache/invalidation.py` | store-backed invalidator implementation, separate from facade |
| `src/async_model_gateway/response_cache/compat.py` | temporary deprecated legacy adapter only |
| `src/async_model_gateway/response_cache/ports/codec.py` | `CacheCodec` port |
| `src/async_model_gateway/response_cache/ports/version_token_factory.py` | `VersionTokenFactory` port |
| `src/async_model_gateway/response_cache/ports/store.py` | `CacheStore` and its coherence guarantees |
| `src/async_model_gateway/response_cache/ports/invalidator.py` | `CacheInvalidator` port |
| `src/async_model_gateway/response_cache/_in_memory_store.py` | internal coherent `CacheStore` implementation |
| `src/async_model_gateway/response_cache/freshness_policy.py` | retained internal write-time expiry-policy protocol |
| `src/async_model_gateway/response_cache/ttl_freshness_policy.py` | retained internal positive-TTL expiry implementation |

No source, test, or documentation path above is modified by this planning task.
