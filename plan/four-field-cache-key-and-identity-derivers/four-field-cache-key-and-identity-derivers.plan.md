> Semantic warning: neither
> `analysis/four-field-cache-key-and-identity-derivers/requirements.md` nor
> `analysis/four-field-cache-key-and-identity-derivers/technical-spec.md`
> exists. This plan uses the human-confirmed four-field migration baseline and
> the repository's prediction-workflow boundary; it does not silently replace
> an analysis-layer source of truth.

# four-field-cache-key-and-identity-derivers

## Goal / Outcome

- Replace the implemented three-field `CacheKey` with the four-field identity
  carrier `CacheKey(namespace, model_identity_hash, feature_hash,
  prediction_input_hash)` and migrate every in-repository caller.
- Make the local response projection derive its cache identity internally,
  take complete model identity only from `RegistryEntry.model_identity_hash`,
  and remove only the retired three-field factory/hash route while retaining
  the necessary legacy entry/error/operation bridge without a key adapter or
  storage migration.

## Scope

- **In scope**:
  - Create this plan, non-trivial behavior specification, and step tracker.
  - In the later approved implementation, change the public `CacheKey` field
    set; add internal local-response identity derivers; migrate the local
    gateway, its request/executor typing, all production/test/typecheck
    constructors, and all cache-key assertions.
  - Modify `response_cache.compat` to retain `LegacyResponseCacheAdapter` and
    its necessary entry/error/legacy-operation bridge while removing only
    `ResponseCacheKey`, `FeatureHasher`, `CanonicalFeatureHasher`, and
    `ResponseCacheKeyFactory` plus their imports, exports, and dedicated tests.
  - Require RED-first authoring, then implementation review before PR routing.

- **Out of scope**:
  - A new CacheKey compatibility adapter, deprecated key alias, dual-read/
    dual-write, cache record/storage migration, invalidation-policy change, or
    persistence work. The pre-existing legacy operation bridge is retained only
    as explicitly scoped below.
  - `PredictionOrchestrator`, `Predictor`, `ResultCodec`, pandas, remote
    execution, feature-vocabulary semantics, artifact identity, deep immutable
    snapshots, timeout/retry/singleflight, or broader workflow wiring.
  - Registry lookup/freshness/store behavior, the `ModelIdentityHasher`
    algorithm, model-payload hashing, dependencies, documentation, README,
    version, release, commit, push, or PR work.

### Executable file inventory

| Classification | Exact paths | Contract |
| --- | --- | --- |
| Written now | `plan/four-field-cache-key-and-identity-derivers/four-field-cache-key-and-identity-derivers.plan.md`; `plan/four-field-cache-key-and-identity-derivers/four-field-cache-key-and-identity-derivers.spec.md`; `plan/four-field-cache-key-and-identity-derivers/four-field-cache-key-and-identity-derivers.step.md` | Planning actor creates only these three topic-planning artifacts in this pass. |
| Created during implementation | `src/async_model_gateway/local_response/_identity_derivers.py`; `tests/local_response/test_identity_derivers.py` | Implementer adds private, synchronous local identity derivation and its focused direct-import coverage. Neither is package/root exported. |
| Modified during implementation — production | `src/async_model_gateway/response_cache/key.py`; `src/async_model_gateway/response_cache/compat.py`; `src/async_model_gateway/local_response/gateway.py`; `src/async_model_gateway/local_response/request.py`; `src/async_model_gateway/local_response/_local_onnx_executor.py` | Replace the key fields, remove only compat's retired three-field route, preserve the legacy entry/error/operation bridge with opaque four-field keys, and migrate the local public projection. |
| Modified during implementation — tests/type witness | `tests/response_cache/test_key.py`; `tests/response_cache/test_cache.py`; `tests/response_cache/test_in_memory_store.py`; `tests/response_cache/test_response_cache_freshness_policy.py`; `tests/response_cache/test_response_cache_contract_migration.py`; `tests/response_cache/test_response_cache_package_surface.py`; `tests/model_registry/test_freshness_policy.py`; `tests/local_response/test_gateway.py`; `tests/local_response/test_local_response_package_surface.py`; `tests/typecheck/local_response_generation_with_cache_reuse.py` | Migrate every current constructor, key-shape assertion, caller witness, local gateway contract assertion, and compat surface/migration assertion. The two compat tests must retain and cover the legacy entry/error/operation bridge as an opaque four-field-key consumer. |
| Deleted during implementation | `tests/response_cache/test_canonical_feature_hasher.py`; `tests/response_cache/test_key_factory.py` | Remove only tests whose sole subject is the retired three-field feature-hasher/factory route. No successor CacheKey adapter or alias is permitted. |
| Future gate artifacts — invalidated and not written now | `plan/four-field-cache-key-and-identity-derivers/four-field-cache-key-and-identity-derivers.plan-review.json`; `plan/four-field-cache-key-and-identity-derivers/four-field-cache-key-and-identity-derivers.human-check.json`; `plan/four-field-cache-key-and-identity-derivers/four-field-cache-key-and-identity-derivers.red-tests.yaml`; `plan/four-field-cache-key-and-identity-derivers/four-field-cache-key-and-identity-derivers.implementation-review.yaml` | This replan invalidates any current evidence at these paths. Reviewer, then Human, then Tester must respectively create fresh review, fresh human clearance, and reconfirmed or updated RED evidence before implementation resumes; planning authoring must not prefill any. |
| ReadOnly / preserve and validate — public/cache consumers | `src/async_model_gateway/response_cache/__init__.py`; `src/async_model_gateway/response_cache/cache.py`; `src/async_model_gateway/response_cache/_in_memory_store.py`; `src/async_model_gateway/response_cache/invalidation.py`; `src/async_model_gateway/response_cache/ports/__init__.py`; `src/async_model_gateway/response_cache/ports/store.py`; `src/async_model_gateway/response_cache/ports/invalidator.py`; `src/async_model_gateway/response_cache/record.py`; `src/async_model_gateway/response_cache/outcomes.py`; `src/async_model_gateway/response_cache/errors.py`; `src/async_model_gateway/response_cache/freshness_policy.py`; `src/async_model_gateway/response_cache/ttl_freshness_policy.py`; `tests/response_cache/test_entry.py` | Cache/store/invalidator operations continue consuming an opaque `CacheKey`; no facade, port, outcome, record, TTL, or root-export expansion is authorized. |
| ReadOnly / preserve and validate — registry and runtime | `src/async_model_gateway/model_registry/__init__.py`; `src/async_model_gateway/model_registry/entry.py`; `src/async_model_gateway/model_registry/registry.py`; `src/async_model_gateway/model_registry/model_identity/__init__.py`; `src/async_model_gateway/model_registry/model_identity/canonical_hash.py`; `src/async_model_gateway/model_registry/model_payload/__init__.py`; `src/async_model_gateway/model_registry/model_payload/canonical_hash.py`; `src/async_model_gateway/model_registry/freshness_policy.py`; `src/async_model_gateway/model_registry/freshness_result.py`; `src/async_model_gateway/model_registry/ports/store.py`; `src/async_model_gateway/model_registry/stores/in_memory.py`; `src/async_model_gateway/model_runtime/_local_runtime_composition.py`; `src/async_model_gateway/model_runtime/model_artifact/__init__.py`; `tests/model_registry/model_identity/test_canonical_hash.py`; `tests/model_registry/model_payload/test_canonical_hash.py`; `tests/model_registry/test_registry.py`; `tests/model_runtime/model_artifact/test_loader_family.py`; `tests/model_runtime/model_artifact/test_model_artifact.py`; `tests/model_runtime/model_artifact/test_model_artifact_package_surface.py`; `tests/model_runtime/model_execution/test_model_execution.py`; `tests/model_runtime/model_execution/test_model_execution_package_surface.py`; `tests/model_runtime/model_pool/fixtures/build_minimal_identity_model.py`; `tests/model_runtime/model_pool/fixtures/minimal_identity.onnx`; `tests/model_runtime/model_pool/test_model_pool.py`; `tests/model_runtime/model_pool/test_model_pool_package_surface.py`; `tests/model_runtime/model_pool/test_onnx_local_runtime_acquisition.py`; `tests/model_runtime/model_pool/test_onnx_model_loader.py`; `tests/model_runtime/runtime_model/test_loaded_runtime_model.py`; `tests/model_runtime/runtime_model/test_runtime_model_package_surface.py`; `tests/model_runtime/test_local_runtime_composition.py` | `RegistryEntry.model_identity_hash` remains the complete-model identity authority; lookup, policy, upsert, payload hashing, artifact loading, and execution composition do not change. |
| ReadOnly / preserve and validate — project and unrelated coverage | `README.md`; `docs/architecture.md`; `docs/specs/prediction-workflow-boundary.md`; `docs/specs/response-cache-boundary.md`; `pyproject.toml`; `uv.lock`; `src/async_model_gateway/__init__.py`; `src/async_model_gateway/__version__.py`; `tests/response_cache/test_ttl_freshness_policy.py`; all existing `plan/**` outside this topic | No documentation, package metadata, dependency, release, or historical-evidence change is authorized. |
| Out of scope / no path authorization | Any path not named above | New path or contract drift returns to `spec-and-plan-finalization`. |

## Locked Decisions

- D1 verdict: `non-trivial`. This is an explicit breaking public-key and local
  projection migration; it uses the Python planning extension.
- `CacheKey` remains a frozen slotted public dataclass, but its exact ordered
  fields become `namespace`, `model_identity_hash`, `feature_hash`, and
  `prediction_input_hash`. It performs no coercion, normalization, hidden
  derivation, context capture, or legacy positional compatibility.
- `RegistryEntry.model_identity_hash` is the sole model-identity authority.
  `LocalResponseGateway` reads it from the fresh registry entry after
  `resolve_freshness`; it must not substitute `payload_hash`, rehash its fields,
  or add a registry result field.
- `local_response._identity_derivers` is an internal-only synchronous module.
  Its private `FeatureIdentityHasher` owns canonical feature identity; the
  module owns canonical JSON-like invocation identity, fixed local namespace
  derivation, and dumb four-value `CacheKey` assembly. None is exported by
  `local_response`, `response_cache`, a ports package, or the root package.
- `FeatureIdentityHasher` accepts feature mapping material only when every key
  and every value is `str`. A non-`str` key or value fails closed with
  `TypeError`; it is never coerced, stringified, skipped, or converted into a
  cache miss.
- Feature and prediction-input derivation fail closed before cache lookup or
  execution. Their canonical material is deterministic, preserves literal
  values without normalization/coercion, and never puts raw invocation,
  feature, model, or artifact material in a key field. The existing local
  projection keeps its single shallow `dict(request.invocation)` snapshot;
  deeper target-orchestrator snapshots are deferred.
- `LocalResponseRequest.invocation` and `_LocalResponseExecutor` migrate from
  unconstrained `dict[str, object]` to the existing JSON-like value vocabulary.
  The exact snapshot object is supplied to both input identity derivation and
  execution; invalid nested material stops before the registry await, cache
  lookup, executor, converter, or remember.
- `LocalResponseGateway.__init__` removes the public keyword-only
  `cache_key_deriver` collaborator. Its remaining collaborators are
  `registry`, `response_cache`, `convert_onnx_result`, and optional `executor`.
  No public replacement deriver, adapter, or injection seam is added.
- `response_cache.compat` is modified, not deleted. It retains
  `LegacyResponseCacheAdapter`, `ResponseCacheEntry`,
  `LegacyCacheClosedError`, and `LegacyCacheOperationError`, which accept the
  new four-field `CacheKey` only as an opaque value. It removes
  `ResponseCacheKey`, `FeatureHasher`, `CanonicalFeatureHasher`, and
  `ResponseCacheKeyFactory` with their imports/exports/tests; no new key alias
  or adapter is introduced. Existing cache records are not transformed or read
  through a legacy key.
- `tests/response_cache/test_response_cache_contract_migration.py` is a
  Modified compatibility regression, not ReadOnly: it must exercise the
  retained adapter entry/error/operation bridge using supplied four-field keys.
  Together with `tests/response_cache/test_response_cache_package_surface.py`,
  it must assert exactly the retained compat names and the approved removed
  names; neither test may expand the retained scope.
- The async boundary remains unchanged: registry/cache/executor calls remain
  direct awaits; no task, lock, timeout, retry, cancellation policy, resource
  owner, or concurrent fan-out is introduced.
- Stable-library intent is absent. `README.md`, `VERSION`, release metadata,
  and the release workflow are not changed.
- Analysis routing is incomplete optional-analysis mode: the human-confirmed
  baseline and `docs/specs/prediction-workflow-boundary.md` govern this plan.

## Boundaries / Exclusions

- Planning actor writes only the three Written-now artifacts. Reviewer, human,
  test author, and implementation reviewer own their future evidence paths.
- Implementer may change only the Created/Modified/Deleted paths above. A
  source-level semantic change to model registry, result representation,
  response-cache operation, store persistence, or orchestration requires a new
  topic.
- Tests must use normal imports; no dynamic module loading is authorized.
- No role may infer an approval, human check, human merge, release, or evidence
  result from this plan or from chat.
- This replan invalidates any current plan-review, human-check, and RED-test
  evidence for this topic. The route back to implementation is fresh plan
  review, fresh human check, then Tester reconfirmation or update of RED
  evidence, all before an Implementer may be assigned. Existing candidate RED
  tests and historical evidence are preserved until their proper owners act.

## Status / Allowed Transitions

- **Current**: `review-ready`
- **Execution model**: `spec-and-plan-finalization -> implement-plan ->
  pr-comment -> pr-comment-review-pr-comments-and-fix`; this topic stops at
  `merged` and has no release phase.
- **Allowed transitions**:
  - `planned` -> `creator-in-progress`
  - `creator-in-progress` -> `review-ready`
  - `review-ready` -> `reviewer-in-progress`
  - `reviewer-in-progress` -> `approved`
  - `reviewer-in-progress` -> `needs-rework`
  - `needs-rework` -> `creator-in-progress`
  - `approved` -> `creator-in-progress`
  - `approved` -> `publish-in-progress`
  - `publish-in-progress` -> `pr-open`
  - `publish-in-progress` -> `merged`
  - `pr-open` -> `needs-rework`
  - `pr-open` -> `merged`

Routing notes:

- This replan invalidates any current plan-review, human-check, and RED-test
  evidence. An independent fresh plan-review verdict, fresh repo-visible human
  check, then Tester reconfirmation or update of RED evidence are required in
  that order before an Implementer may be assigned or `implement-plan` resumes.
- Independent implementation review remains required before `pr-comment`.

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/four-field-cache-key-and-identity-derivers/four-field-cache-key-and-identity-derivers.plan.md` | Planning actor | Repo-visible execution contract |
| Behavior specification | `plan/four-field-cache-key-and-identity-derivers/four-field-cache-key-and-identity-derivers.spec.md` | Planning actor | Non-trivial behavior contract |
| Step tracker | `plan/four-field-cache-key-and-identity-derivers/four-field-cache-key-and-identity-derivers.step.md` | Implementer | Progress and gate tracking |
| Plan review | `plan/four-field-cache-key-and-identity-derivers/four-field-cache-key-and-identity-derivers.plan-review.json` | Reviewer | Future planning-gate verdict |
| Human check | `plan/four-field-cache-key-and-identity-derivers/four-field-cache-key-and-identity-derivers.human-check.json` | Human | Future implementation-entry authorization |
| RED evidence | `plan/four-field-cache-key-and-identity-derivers/four-field-cache-key-and-identity-derivers.red-tests.yaml` | Tester | Fresh RED-first reconfirmation or update required before Implementer assignment |
| Implementation review | `plan/four-field-cache-key-and-identity-derivers/four-field-cache-key-and-identity-derivers.implementation-review.yaml` | Independent reviewer | Future pre-PR implementation gate |
| Implementation inventory | All exact Created/Modified/Deleted paths in the executable inventory | Implementer | Only approved source/test changes |

`README.md`, `VERSION`, `pyproject.toml`, `uv.lock`, and documentation do not
change. If later work needs a path outside this table or the inventory, it must
return to planning.

## Implementation Steps

1. Only after fresh plan review and fresh human check, Tester reconfirms or
   updates RED tests in the declared local-response and response-cache test
   files plus `tests/local_response/test_identity_derivers.py`, and records
   fresh RED evidence before an Implementer is assigned. Cover the new field
   shape, complete-model identity authority, deterministic internal derivation,
   `FeatureIdentityHasher` non-`str` key/value `TypeError`, invalid identity
   material ordering, all three fail-open remember outcomes, caller migration,
   and removed compat imports without dynamic loading.
2. Add `src/async_model_gateway/local_response/_identity_derivers.py` with the
   locked private synchronous derivation responsibilities, including
   `FeatureIdentityHasher`. Keep the module unexported; make its feature
   mapping validation fail closed with `TypeError` for non-`str` keys or values;
   and make its key assembler consume only four already-derived string
   identities.
3. Change `src/async_model_gateway/response_cache/key.py` to the exact
   four-field frozen/slotted `CacheKey`; migrate every response-cache test
   helper and assertion while leaving cache/store/invalidation behavior and
   signatures unchanged.
4. Migrate `src/async_model_gateway/local_response/request.py`,
   `_local_onnx_executor.py`, and `gateway.py`: remove `_CacheKeyDeriver` and
   constructor injection, validate/derive before the first registry await,
   read `freshness.entry.model_identity_hash`, and use one invocation snapshot
   for identity and execution.
5. Modify `src/async_model_gateway/response_cache/compat.py` to retain only the
   legacy entry/error/operation bridge over opaque four-field keys; remove its
   `ResponseCacheKey`, feature-hasher, and key-factory imports/exports, delete
   their two dedicated tests, and modify
   `tests/response_cache/test_response_cache_contract_migration.py` and
   `tests/response_cache/test_response_cache_package_surface.py` to cover the
   retained bridge and exactly the compat-retained surface. Do not change
   `tests/response_cache/test_entry.py`.
6. Migrate the local gateway tests, package-surface contract, registry
   key-shape regression, and public type witness. In
   `tests/local_response/test_gateway.py`, regress that `Remembered`,
   `Skipped`, and `Failed` each remain fail-open: after a miss, each returns the
   generated response without changing execution order. Run the declared
   validation commands and update the step tracker truthfully for implementation
   review.

## Validation / Acceptance Checks

- The three plan artifacts exist, have exact paths, and this plan is
  `review-ready`. This replan invalidates any current plan-review, human-check,
  and RED-test evidence; none may be treated as current implementation entry.
- Before implementation resumes, Plan-Reviewer records a fresh review verdict,
  Human records a fresh check, and Tester reconfirms or updates RED evidence in
  that order; no Implementer may be assigned earlier. Planning authoring
  neither creates nor deletes those gate files.
- The implementation inventory is complete: every current `CacheKey`
  constructor and legacy compat caller is either migrated, retained as an
  opaque consumer, or deleted exactly as classified.
- `CacheKey` has exactly four ordered fields, and changing any one field
  changes equality/hash identity; three-field construction and
  `model_payload_hash` access fail.
- Local identity uses `RegistryEntry.model_identity_hash` and never raw
  payload hash or rehashed registry fields. Feature/input failures happen
  before registry/cache/execution side effects, and raw material is absent from
  key fields. `FeatureIdentityHasher` rejects every non-`str` feature key and
  value with `TypeError` before the first registry await.
- The gateway public constructor no longer accepts `cache_key_deriver`; all
  in-repository callers and the type witness compile against the replacement.
- The retired `ResponseCacheKey`, feature-hasher, and key-factory routes are
  absent. `response_cache.compat.LegacyResponseCacheAdapter` plus its necessary
  entry/error/operation bridge remains available, is covered by the modified
  migration contract test with four-field opaque keys, and treats those keys as
  opaque. Package-surface and migration assertions agree on exactly this
  retained compat scope; no substitute key adapter/alias or old-record
  migration appears.
- Existing response-cache operational outcomes, async direct-await behavior,
  model-registry freshness behavior, package-root exports, and local ONNX
  guard semantics remain unchanged. After a cache miss, each `Remembered`,
  `Skipped`, and `Failed` remember outcome returns the generated local response
  fail-open with no additional execution or conversion.
- `uv run pytest`, `uv run pyright`, and `uv run ruff check src tests` pass
  after implementation; focused RED and migration tests fail first and then
  pass only after the approved implementation.

## Reviewer Handoff

```json
{
  "verdict": "approved|needs-rework",
  "blocking_issues": [],
  "copilot_feedback_triage": {
    "ADDRESS": [],
    "DISCUSS": [],
    "SKIP": []
  }
}
```

## Post-merge / release actions

No release workflow required. Do not change version, tags, lockfile, release
state, README, or documentation after merge under this topic.

## Open Questions / Unresolved Items

None. The plan deliberately limits the local projection to its current shallow
invocation snapshot; target deep snapshots and broader workflow owners are
separate topics.

## Goal

Implement the human-confirmed four-field cache-key replacement and migrate the
bounded local response projection without retaining legacy cache identity APIs.

## Non-goals

- No storage, record, persistence, eviction, invalidation, or TTL migration.
- No new CacheKey compatibility adapter, key alias, dual-read, dual-write, or
  old-key fallback; retain only the locked legacy entry/error/operation bridge.
- No orchestrator, predictor, result codec, remote execution, pandas, or
  complete target-workflow implementation.
- No registry lookup/freshness/payload/identity-hasher change.
- No dependency, documentation, version, release, commit, push, or PR change.

## Current Context

`response_cache.key.CacheKey` is currently a frozen slotted three-field public
dataclass. `response_cache.compat` currently combines the legacy entry/error/
operation bridge with a deprecated three-field key factory and feature hasher.
The replan retains the former as an opaque-key bridge and removes only the
latter. The local gateway currently accepts an injected private `_CacheKeyDeriver`, snapshots a
top-level invocation mapping, awaits registry freshness, and passes only
`freshness.entry.payload_hash` to that collaborator. The registry already
provides a derived read-only `RegistryEntry.model_identity_hash` authority.

## Requirements

1. `CacheKey` exposes exactly namespace, model identity hash, feature hash, and
   prediction-input hash, in that order, with no legacy field or constructor.
2. Every in-repository constructor/caller is migrated or deliberately deleted
   according to the executable inventory; all opaque cache consumers keep their
   operation signatures.
3. Local derivation is private, deterministic, synchronous, fail-closed, and
   occurs before cache/execution side effects; `FeatureIdentityHasher` raises
   `TypeError` for each non-`str` feature key or value, and its assembler has no
   hashing or normalization policy.
4. Local cache identity consumes `RegistryEntry.model_identity_hash` exactly;
   registry behavior remains unchanged.
5. Local request identity/execution share the existing one snapshot, and invalid
   JSON-like input stops before the registry await.
6. `compat` retains only its legacy entry/error/operation bridge over opaque
   four-field keys; its `ResponseCacheKey`, feature-hasher, and key-factory
   routes are absent, with no new key adapter/alias or storage migration.
   The modified compat migration and package-surface tests agree on, and cover,
   the retained bridge.
7. After a cache miss, the local gateway returns the generated response for
   `Remembered`, `Skipped`, and `Failed` remember outcomes without an extra
   execution or conversion.
8. Fresh plan review, fresh human check, and fresh RED reconfirmation or update
   occur in that order before Implementer assignment; implementation-review
   evidence still precedes PR routing.

## Decisions

- Async-planning status: exempt — cite exemption evidence: this topic changes
  synchronous dataclass shape, canonical in-memory identity derivation, and
  existing direct-await call inputs only; it introduces no async boundary,
  resource lifecycle, concurrency model, timeout, cancellation, retry, or
  external I/O policy.
- Module/package placement: private derivers live only in
  `src/async_model_gateway/local_response/_identity_derivers.py`; key shape
  remains in `response_cache/key.py`; local call-site migration remains in the
  existing local-response modules.
- New public API: no. `CacheKey` is an existing public type with a breaking
  replacement field set; no new root/package export or public deriver is added.
- Interface changes: yes. `CacheKey` replaces `model_payload_hash` with
  `model_identity_hash` and adds `prediction_input_hash`; the public local
  gateway constructor removes `cache_key_deriver`; the local invocation
  contract narrows to JSON-like material.
- Breaking changes allowed: yes — the human-confirmed migration replaces the
  old key route and removes its factory/hash helpers while retaining the
  necessary legacy entry/error/operation bridge as an opaque-key consumer; no
  new key adapter or alias is promised.
- New dependencies: no — standard library plus already-installed project code.
- Error handling strategy: identity validation/canonicalization errors propagate
  unchanged before the first registry await; `FeatureIdentityHasher` raises
  `TypeError` for every non-`str` feature key/value; no cache miss, fallback
  key, execution, write, or error translation is manufactured.
- Typing strategy: strict Python 3.10 annotations; existing JSON-like type
  vocabulary; no `Any`, coercion, dynamic import, public Protocol, or new
  dependency.

## Public Contract / API Changes

```python
@dataclass(frozen=True, slots=True)
class CacheKey:
    namespace: str
    model_identity_hash: str
    feature_hash: str
    prediction_input_hash: str

class LocalResponseGateway:
    def __init__(
        self,
        *,
        registry: ModelRegistry,
        response_cache: ResponseCache,
        convert_onnx_result: _OnnxResultConverter,
        executor: _LocalResponseExecutor | None = None,
    ) -> None: ...
```

`CacheKey` is intentionally breaking: `model_payload_hash`, three-argument
construction, and `cache_key_deriver` are removed. The existing compat module
retains only its entry/error/operation bridge and consumes the new key opaquely;
it exports no legacy key alias, feature hasher, or factory. The package/root
export lists otherwise remain unchanged.

## Affected Files / Modules

Likely affected files:

- `src/async_model_gateway/response_cache/key.py`
- `src/async_model_gateway/local_response/_identity_derivers.py`
- `src/async_model_gateway/local_response/gateway.py`
- `src/async_model_gateway/local_response/request.py`
- `src/async_model_gateway/local_response/_local_onnx_executor.py`
- `src/async_model_gateway/response_cache/compat.py` (modified)
- all exact test/typecheck paths classified Modified, Created, or Deleted in
  the executable file inventory

Candidate files to inspect:

- `src/async_model_gateway/model_registry/entry.py`
- `src/async_model_gateway/model_registry/registry.py`
- `src/async_model_gateway/response_cache/cache.py`
- `src/async_model_gateway/response_cache/_in_memory_store.py`
- `src/async_model_gateway/response_cache/ports/store.py`
- `src/async_model_gateway/response_cache/ports/invalidator.py`

## Implementation Steps

1. After review approval and the human check, author RED tests in the declared
   local-response and response-cache test files plus
   `tests/local_response/test_identity_derivers.py`; record fresh RED evidence.
   Cover the new field shape, complete-model identity authority, deterministic
   internal derivation, invalid identity material ordering, caller migration,
   and removed compat imports without dynamic loading.
2. Add `src/async_model_gateway/local_response/_identity_derivers.py` with the
   locked private synchronous derivation responsibilities. Keep the module
   unexported and make its key assembler consume only four already-derived
   string identities.
3. Change `src/async_model_gateway/response_cache/key.py` to the exact
   four-field frozen/slotted `CacheKey`; migrate every response-cache test
   helper and assertion while leaving cache/store/invalidation behavior and
   signatures unchanged.
4. Migrate `src/async_model_gateway/local_response/request.py`,
   `_local_onnx_executor.py`, and `gateway.py`: remove `_CacheKeyDeriver` and
   constructor injection, validate/derive before the first registry await,
   read `freshness.entry.model_identity_hash`, and use one invocation snapshot
   for identity and execution.
5. Modify `src/async_model_gateway/response_cache/compat.py` to retain only the
   legacy entry/error/operation bridge over opaque four-field keys; remove its
   `ResponseCacheKey`, feature-hasher, and key-factory imports/exports, delete
   their two dedicated tests, and update package-surface assertions without
   changing `tests/response_cache/test_entry.py` or the retained operation test.
6. Migrate the local gateway tests, package-surface contract, registry
   key-shape regression, and public type witness. Run the declared validation
   commands and update the step tracker truthfully for implementation review.

## Test Plan

Test files: `tests/local_response/test_identity_derivers.py`,
`tests/local_response/test_gateway.py`,
`tests/local_response/test_local_response_package_surface.py`,
`tests/response_cache/test_key.py`, `tests/response_cache/test_cache.py`,
`tests/response_cache/test_in_memory_store.py`,
`tests/response_cache/test_response_cache_freshness_policy.py`,
`tests/response_cache/test_response_cache_contract_migration.py`,
`tests/response_cache/test_response_cache_package_surface.py`,
`tests/model_registry/test_freshness_policy.py`, and
`tests/typecheck/local_response_generation_with_cache_reuse.py`.

- Happy path: four distinct already-derived identities assemble a key; local
  cache hit/miss uses the internal key and complete registry identity; each
  `Remembered`, `Skipped`, and `Failed` outcome returns the miss-generated
  response fail-open without another execution or conversion.
- Invalid input: each non-`str` `FeatureIdentityHasher` key/value and malformed
  invocation identity material raises `TypeError` before registry/cache/executor
  calls; legacy three-field construction and the retired compat key/factory/hash
  imports fail while the operation bridge stays importable.
- Edge case: changed namespace, model identity, feature, or prediction input
  changes key equality/hash; ordering-equivalent feature/input material remains
  deterministic without leaking raw values.
- Regression: cache/store/invalidator behavior, registry freshness result shape,
  local ONNX guards, one shared invocation snapshot, and all three fail-open
  remember outcomes stay unchanged.
- Backward compatibility: deliberately assert preserved root exports, unchanged
  cache operation signatures, and the retained compat entry/error/operation
  bridge with supplied four-field opaque keys in
  `tests/response_cache/test_response_cache_contract_migration.py`; make its
  assertions agree with `tests/response_cache/test_response_cache_package_surface.py`
  on the retained names and approved breaking removals (`model_payload_hash`,
  legacy compat key/factory/hash routes, injected deriver).

## Validation Commands

```sh
uv run pytest
uv run pyright
uv run ruff check src tests
```

## Risks

- Missing one constructor or shape assertion can leave an untested three-field
  call site or cause strict type checking to fail.
- Reusing payload hash instead of the derived model identity could collide
  across model name/source kind while appearing to work in local tests.
- Removing the retained entry/error/operation bridge, or leaving a key alias,
  hasher, or factory in it, would respectively break its required legacy
  operations or preserve ambiguous three-field identity semantics.
- Omitting a non-`str` feature key/value assertion can let canonical feature
  identity stringify unsupported material; omitting a `Skipped` or `Failed`
  path can silently regress the gateway's fail-open response behavior.

## Rollback Plan

Before merge, revert only the Created/Modified/Deleted implementation paths and
this topic's artifacts as one change set. Revert the compat edit together with
the removed helper tests; do not delete the retained operation bridge, attempt
a partial key-schema rollback, or transform cache records.

## Open Questions

None.
