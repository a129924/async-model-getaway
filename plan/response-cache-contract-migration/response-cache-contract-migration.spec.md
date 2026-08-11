# response-cache-contract-migration Specification

## Acceptance Criteria

1. `ResponseCache` has exactly the two keyword-only async methods `lookup(*, key, context)` and
   `remember(*, key, value, context)` with the frozen union return types in the technical spec;
   there is no root-public `get`, `set`, or `invalidate` facade method.
2. `CacheKey` alone determines cache identity and hashing. Distinct contexts cannot affect key
   equality/hash, stored record content, codec payload, metadata, expiry, or version token.
3. Every `StoredCacheRecord` is immutable and validates `schema_version == 1`, codec/payload,
   aware-UTC write and expiry timestamps, opaque per-write token, and the fixed metadata limits.
   Only internal `UnsupportedSchemaRecord(schema_version, version_token)` may represent a known
   non-1 schema returned by `CacheStore.get`; it is not a public stored record.
4. A `CacheStore` implements coherent reads of `StoredCacheRecord | UnsupportedSchemaRecord |
   None`, whole-record replacement, key-local delete, and atomic compare-delete. A stale cleanup
   racing a later remember never deletes the later record.
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
12. `ResponseCacheKeyFactory` remains only under `compat` with the predecessor-verifiable
    constructor `ResponseCacheKeyFactory(hasher)` and
    `build(*, namespace, model_payload_hash, features)`. It has no `create()` method and retains
    no namespace. `CacheStore` is not re-exported by `response_cache.ports`, and `compat` does
    not leak imported target collaborators. Direct ordinary-import coverage in
    `tests/response_cache/test_canonical_feature_hasher.py` preserves predecessor golden digests
    and pair-list ordering, rejects non-`Mapping[str, str]` pairs with `TypeError`, and verifies
    that strict UTF-8 encoding failure is `TypeError` chained from `UnicodeEncodeError`; dynamic
    loading is prohibited.
13. The immutable historical human-check remains byte-identical with SHA-256
    `f6ec59dbf3f5df4ba42359b9978c31bebd4bbf30b1645146ba1a4841508d417b`, final byte `0x7d`, and
    no final LF. Before and after validation, the topic plan's non-writing SHA-256, terminal-byte,
    no-final-LF, and no-Git-diff checks all pass; the full-scope aggregate evidence records both result
    sets. CI scans that exact file first with the local-path guard, then uses the existing
    exact-selector pre-commit command for every other file. Full-scope reviewer evidence binds the
    fixed base revision, exact reviewed head, closed scope, and reproducible binary-diff digest.
14. Fresh plan review and the Human Draft-PR check bind only the SHA-256 recomputed from the topic
    plan file bytes immediately before each artifact is written; Git blob, tree, and commit SHAs
    are not plan-SHA authority. Any plan-byte drift invalidates both gates.

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

### Scenario 9: Unsupported schema is reclaimable without weakening the record invariant

- **Given**: `CacheStore.get` returns `UnsupportedSchemaRecord(schema_version=2, version_token=A)`.
- **When**: a caller awaits `lookup` and a concurrent remember may replace token A with token B.
- **Then**: lookup returns `CacheMiss` without decoding; it attempts only
  `delete_if_version(key, A)`, and token B survives. Constructing `StoredCacheRecord` with schema
  version 2 remains a validation error.

### Scenario 10: Deprecated factory has one predecessor-verifiable operation

- **Given**: a caller imports `ResponseCacheKeyFactory` from `compat` with a feature hasher.
- **When**: it calls `build` with an explicit namespace.
- **Then**: it receives `CacheKey`; the factory has no `create` attribute, retains no namespace,
  and neither `compat` nor `response_cache.ports` exposes the target collaborators excluded by the
  package-surface contract.

### Scenario 11: Compatibility hasher preserves the predecessor pair-list contract

- **Given**: `tests/response_cache/test_canonical_feature_hasher.py` imports the compatibility
  hasher through `compat` using ordinary imports only.
- **When**: it hashes predecessor mapping inputs in different insertion orders, receives a
  non-`Mapping[str, str]` pair, or receives an unencodable Unicode value.
- **Then**: the predecessor golden digests and pair-list ordering remain stable, the non-string
  key/value input fails closed with `TypeError`, and the Unicode failure is `TypeError` chained
  from `UnicodeEncodeError`; no dynamic loading is used.

### Scenario 12: CI preserves the historical anchor while checking every path

- **Given**: the historical human-check has the locked digest, terminal byte, and no final LF.
- **When**: CI reaches repository validation.
- **Then**: it first invokes only the local-path guard on that exact file, then invokes the
  pre-existing exact-selector pre-commit command for all other files; no hook receives or changes
  the historical file, and the reviewer records matching pre/post SHA-256, `0x7d`, no-final-LF,
  and clean-Git-diff results in full-scope aggregate evidence.

### Scenario 13: Full-scope aggregate review is reproducible and non-self-referential

- **Given**: the CI-only change and this revision's planning artifacts are final at one committed
  candidate head.
- **When**: the reviewer creates the append-only full-scope aggregate evidence.
- **Then**: it records base `bfc2ba0c3f878af4b46cbea5d956926738326579`, functional head
  `535e70f19f9f316406f4188689a039db05dd17c1`, the ordered scope `README.md`, `docs`, `src`, `tests`,
  and SHA-256 of the literal binary-diff command's raw stdout output bytes, including any emitted
  final newline and excluding command text or transformed captures. The evidence file and every
  other gate artifact remain outside that digest, and later scoped drift requires a fresh review.
  The existing `final-aggregate-review.yaml` remains immutable historical provenance. A pre-PR
  `needs-rework` returns to the bounded `implement-plan` repair, replacement full-scope aggregate
  review, and fresh preflight loop without entering a PR-comment phase.

## Error / Edge Cases

- `UnsupportedSchemaRecord`, expired record, decode failure, read failure, and cleanup failure are
  all lookup misses; an unsupported schema preserves only its token for compare-delete, and a
  cleanup failure cannot change that result to an exception or hit.
- Invalid timestamp ordering, invalid metadata bounds, non-UTC timestamps, malformed identity,
  and configuration errors are defects and propagate rather than becoming cache outcomes.
- Compare-delete must fail harmlessly when the observed token no longer matches; unconditional
  stale deletion is prohibited.
- Invalidation is key-local, returns `NotFound` for absence, and never derives identity or consumes
  a context.
- Direct imports are required in tests; dynamic module loading is prohibited.
- Direct old module routes are removed by the declared file deletions. Tests verify root and
  `compat` surfaces with ordinary imports and source/path disposition, never dynamic imports.
- The historical human-check is neither formatted, normalized, staged, nor passed to pre-commit.
  A local-path finding, anchor mismatch, final-LF/nonzero-diff result, selector change, or
  post-review scoped change blocks preflight and requires the declared fresh-gate route rather
  than a historical-file rewrite.

## PR #26 full-scope delivery-evidence appendendum

### Acceptance Criteria

1. Only Reviewer creates the new append-only
   `plan/response-cache-contract-migration/response-cache-contract-migration.full-scope-aggregate-review.yaml`.
   It must not rewrite the existing immutable `response-cache-contract-migration.final-aggregate-review.yaml`.
2. It records base `bfc2ba0c3f878af4b46cbea5d956926738326579`, functional head
   `535e70f19f9f316406f4188689a039db05dd17c1`, ordered scope `[README.md, docs, src, tests]`,
   literal command
   `git diff --binary bfc2ba0c3f878af4b46cbea5d956926738326579 535e70f19f9f316406f4188689a039db05dd17c1 -- README.md docs src tests`,
   and byte-stream digest
   `9a3b02ace7ae3e69c1fa5b8bc04436d4ea846f5e27c790808de6d015f55080e8`.
   `diff_sha256` is the SHA-256 of raw stdout output bytes emitted by the literal command,
   including any final newline Git emits; it is not the command text and permits no decoding,
   re-encoding, trimming, shell substitution, newline normalization, or other transformation.
3. A fresh current-plan-SHA-256 plan review and fresh Human Draft-PR clearance precede the new
   reviewer artifact; preflight follows only an approved new artifact.
4. The artifact records a committed `delivery_head_revision` and a passing
   `git diff --exit-code 535e70f19f9f316406f4188689a039db05dd17c1 <delivery_head_revision> -- README.md docs src tests`
   result. That check repeats successfully against the then-current delivery head before preflight;
   preflight follows only this approved artifact, never the historical final aggregate.

### Behavioral Scenario: Delivery evidence preserves the reviewed functional scope

- **Given**: the fresh plan-review and Human Draft-PR gates bind the current topic-plan SHA-256.
- **When**: Reviewer records the new full-scope verdict for a committed delivery head.
- **Then**: it preserves the locked base/head/four-path command/digest, proves no functional drift
  from the functional head through delivery, and leaves existing historical, implementation,
  code-review, and final-aggregate evidence unchanged.

### Error / Edge Cases

- A changed or reordered scope path, a non-literal command, or a digest mismatch is blocking.
- A nonzero delivery-head no-functional-scope-drift result blocks preflight and returns scope or
  contract repair to `spec-and-plan-finalization`.
- Including the new artifact, an existing final aggregate, or another gate artifact in the
  four-path digest is self-referential scope creep and must be rejected.
