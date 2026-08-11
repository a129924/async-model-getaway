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
| `ResponseCacheKey` and `ResponseCacheKeyFactory` make identity through a feature-hasher collaborator. | `CacheKey(namespace, model_payload_hash, feature_hash)` is the sole identity/hash authority. | Construct `CacheKey` only from already-derived identity components; stop factory-owned feature hashing in normal cache work. The compatibility factory has only the predecessor-verifiable shape `ResponseCacheKeyFactory(hasher)` plus `build(*, namespace, model_payload_hash, features)`; remove `create()` and do not retain namespace state. | `compat.ResponseCacheKey` is an alias of `CacheKey`; `compat.ResponseCacheKeyFactory` and its `FeatureHasher`/`CanonicalFeatureHasher` are deprecated migration-only helpers. Tests prove that `create` is absent, `build` requires explicit namespace, and direct old key/factory module imports are absent. |
| `_canonical_feature_hasher.py` and `ports/feature_hasher.py` canonicalize features for the old factory. | No target cache collaborator hashes features. Feature hash arrives as a `CacheKey` field. | Delete both modules and remove normal feature-hasher imports. | Compatibility-only helper classes live in `compat.py`; direct imports of the deleted modules are absence-tested, and only `compat` exports the legacy helper surface. |
| `ResponseCacheEntry(response: str)` is the public cache value. | Public value is `str`; persistence uses `StoredCacheRecord`. | Delete `entry.py` and make target callers use string values / `CacheHit.value`. | `compat.ResponseCacheEntry` is a frozen one-field wrapper only for legacy adapter calls. Direct `entry` module import is absence-tested. |
| `ResponseCacheStore.get/set/invalidate` carries entry values and a boolean invalidation result. | `CacheStore.get` returns `StoredCacheRecord | UnsupportedSchemaRecord | None`; `set/delete/delete_if_version` operate on coherent whole `StoredCacheRecord` snapshots, and `CacheInvalidator` owns invalidation results. | Add the narrow internal `UnsupportedSchemaRecord(schema_version, version_token)` read result. It is the only way a store reports a known non-1 schema while preserving the observed token for compare-delete; `StoredCacheRecord` continues to reject every schema other than `1`. No root or ports-root store export. | Lookup maps an unsupported-schema result to `CacheMiss` after best-effort atomic `delete_if_version` with that observed token. The adapter owns old method shape only; target store ports do not provide legacy aliases. |
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

## PR #26 reconciliation decisions

The three actionable review comments are resolved only by the following frozen changes; none is
an invitation to widen the response-cache migration.

1. The deprecated factory keeps its predecessor-verifiable `hasher` collaborator and explicit
   `build(*, namespace, model_payload_hash, features)` operation only. `create()` and a retained
   namespace constructor argument are removed.
2. Unsupported persisted schemas are represented only by internal
   `UnsupportedSchemaRecord(schema_version, version_token)` from `CacheStore.get`. This preserves
   `StoredCacheRecord(schema_version == 1)` as an invariant while allowing lookup to perform its
   token-guarded cleanup and return `CacheMiss`.
3. Target import surfaces remain narrow: `CacheStore` is imported from
   `response_cache.ports.store`, not re-exported by `response_cache.ports`; `compat` must not
   expose imported target collaborators as accidental attributes. Package-surface tests prove
   both negative contracts with ordinary imports.

## Delivery-governance reconciliation

This narrow governance revision does not alter any Cache BC row above. It freezes the delivery
evidence for those rows and authorizes one later CI-only change after the fresh planning gates.

1. `plan/response-cache-contract-migration/response-cache-contract-migration.human-check.json`
   is immutable historical provenance. Its required SHA-256 is
   `f6ec59dbf3f5df4ba42359b9978c31bebd4bbf30b1645146ba1a4841508d417b`, its final byte is
   `0x7d`, and it has no final LF. Before and after CI validation, the Implementer must run the
   exact non-writing commands declared by the topic plan: `shasum -a 256` for this path, a
   last-byte check that asserts `0x7d` (and thus no final LF), and
   `git diff --exit-code -- <historical-path>`. The CI workflow must first run the local-path
   guard directly against that exact path; this read-only invocation must not normalize, stage,
   format, restore, or otherwise write the file. It must then run the existing exact pre-commit
   selector unchanged for every other repository file, excluding only that exact historical path.
2. The only later implementation path added by this revision is `.github/workflows/ci.yml`.
   It adds the separate local-path-guard step before the already-existing exact-selector
   pre-commit step. No source, test, human, reviewer, preflight, or historical artifact is a
   CI implementation target.
3. The SHA authority for plan review and Human Draft-PR clearance is the SHA-256 of the topic
   plan file's current bytes, as recomputed with `shasum -a 256` immediately before each actor
   writes. It is never a Git blob, tree, or commit SHA. The fresh review and Human check must
   record the same recomputed value in `reviewed_plan_sha256`; a plan-byte change invalidates both
   gates and requires that sequence again.
4. The final code-review gate is a new reviewer-owned aggregate artifact at
   `plan/response-cache-contract-migration/response-cache-contract-migration.final-aggregate-review.yaml`.
   It must bind one reviewed candidate with base revision
   `dbba2efb6ab4a8b802dfdb122e561ad576fdea53`, the exact reviewed committed head revision,
   the closed scope below, and the SHA-256 of the exact `git diff --binary <base> <head> --
   <scope>` byte stream. The reviewer records the actual head and digest only after all scoped
   changes are final; later scoped changes invalidate the evidence.
   It also records both immutable-anchor command-result sets (`pre` and `post`): SHA-256,
   `terminal_byte_hex: "0x7d"`, `final_lf_present: false`, and successful no-diff result, plus
   an equality assertion. A formatter or any other mutation command is not an anchor check.
5. The aggregate scope is exactly `.github/workflows/ci.yml`, the two revised analysis files,
   the topic plan and Python specification, the six already-locked response-cache source paths,
   and the six already-locked response-cache test paths declared in the topic plan. Gate
   artifacts, including the aggregate artifact itself, are deliberately outside this digest so
   the evidence is reproducible and non-self-referential.
6. A pre-PR aggregate `needs-rework` is an `implement-plan` gate failure, not a transition to
   `pr-open` or a PR-comment workflow. The bounded CI-only repair returns to `implement-plan`,
   then a fresh aggregate review, then a fresh preflight while status remains
   `publish-in-progress`. Any repair that changes scope or contract returns through
   `spec-and-plan-finalization` and the canonical planning rework route.
