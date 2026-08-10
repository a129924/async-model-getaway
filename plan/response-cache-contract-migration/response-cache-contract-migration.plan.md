# response-cache-contract-migration

## Goal / Outcome

在不擴張 response-cache migration 範圍下，將 PR #26 的三則 actionable review comments
reconcile 到 strict analysis、Python specification 與可執行 plan：deprecated factory 保留唯一
可驗證的 predecessor 形狀；unsupported schema 可安全回收而不破壞 record invariant；target
submodule 的 import surface 不外洩。完成後，本 revision 必須重新取得 fresh plan-review 與
後續 Draft-PR evidence；既有 historical human check 不得變更。

## Scope

- **In scope**：只修訂 `canonical-reconciliation.md`、`technical-spec.md`、本 topic plan 與
  Python spec，將下列三則 PR #26 comments 凍結為唯一 follow-up implementation contract：
  1. 移除 `compat.ResponseCacheKeyFactory.create()`，只留下
     `ResponseCacheKeyFactory(hasher)` 和
     `build(*, namespace, model_payload_hash, features)`；
  2. 以狹義 internal `UnsupportedSchemaRecord(schema_version, version_token)` 作為
     `CacheStore.get` read result，lookup 對其 token-guarded compare-delete 後回
     `CacheMiss`，而 `StoredCacheRecord.schema_version == 1` 維持 invariant；
  3. `CacheStore` 不由 `response_cache.ports` root re-export，且 `compat` 不會把匯入的
     target collaborators 變成 accidental attributes。
- **Out of scope**：本 planning/reconciliation revision 不修改 Python source、tests、CI、
  documentation、review/human/preflight evidence 或任何 historical artifact；不重新規劃
  cache identity、facade 方法、atomicity、context persistence、cancellation、legacy placement、
  persistence、settings、eviction、timeout、retry、background task 或 release。
- **Analysis routing**：strict mode。`analysis/response-cache-contract-migration/technical-spec.md`
  是 execution source of truth；`requirements.md` 是 business guardrail；
  `canonical-reconciliation.md` 是 current/target/migration/compatibility row authority。無
  human override。

## Locked Decisions

- 本題仍是 D1 `non-trivial` Python retrofit。這次只 rebase planning contract，不能把已完成的
  base migration 或其 evidence 當作本 revision 的 approval。
- `ResponseCacheKeyFactory` 是 deprecated `compat`-only bridge。它的 constructor 只接收
  `hasher: FeatureHasher`，不保存 namespace；`build` 的 keyword-only `namespace` 是唯一 key
  建構入口，`create` 必須不存在。normal callers 一律直接建構 `CacheKey`。
- `UnsupportedSchemaRecord` 放在 `response_cache.record` 作為 non-exported internal type，
  只有 `schema_version` 和 `version_token`；其 schema 必須是 non-boolean integer 且不可為 1。
  `StoredCacheRecord` 仍只接受 schema 1，兩者不可互換。
- `CacheStore.get` 的 target return union 是
  `StoredCacheRecord | UnsupportedSchemaRecord | None`。unsupported-schema lookup 不 decode、
  不建立 invalid `StoredCacheRecord`，只以 observed token 呼叫 atomic
  `delete_if_version`，無論 delete 成功、token mismatch 或已翻譯的 cleanup operational error 都
  回 `CacheMiss`；cancellation 與 defects 仍原樣 propagate。
- `CacheStore` 只從 `response_cache.ports.store` 直接 import；`ports.__init__` 不 re-export
  它。`compat.py` 對 target imports 使用 private aliases，`compat.__all__` 不變，且 module
  attributes 不得暴露 `ResponseCache`、`CacheKey`、outcomes 或 `CacheInvalidator`。
- 本 revision 不改 public facade、`CacheKey` identity/hash、whole-record replacement、atomicity、
  invocation-only context、clock/freshness ownership、cancellation 或 legacy adapter placement。
  它不新增 dependencies、stable-library release intent、README/VERSION work 或 release workflow。
- 既有
  `plan/response-cache-contract-migration/response-cache-contract-migration.human-check.json`
  是 immutable historical evidence，Planning actor、Implementer、Reviewer、Main Agent 均不得改寫。
  既有 fresh-human-check、forward-preflight、step tracker 和 implementation review 是先前的
  implementation-entry evidence，不能替代這次 revision 的 fresh plan review 或 Draft-PR gates。
- 本 plan SHA 改變後，現有 `plan-review.json`、`draft-pr-human-check.json`、`code-review.yaml`
  與 `draft-pr-preflight.yaml` 都不能核准本 revision。順序固定為：fresh independent
  plan-review → Human 建立 current-plan-bound Draft-PR human check → bounded implementation →
  fresh code review → Main Agent Draft-PR preflight → `pr-open`。Planning actor 不得預填任何
  evidence。

## Boundaries / Exclusions

- Planning actor 僅可修改本 plan 及本 revision 在 Artifact Paths 列出的 analysis/spec artifacts；
  不實作、不建立 reviewer/human/preflight artifacts，也不改 step tracker。
- Implementer 僅在 fresh plan review 與 Human Draft-PR check 已通過後修改 closed list 中的
  source/test files；不得回寫 planning、historical human check 或任何既有 evidence。
- Reviewer 只產生 fresh `plan-review.json` 與 code-review verdict；Human 只產生 explicit
  Draft-PR human check 與 human merge；Main Agent 只在 fresh code review approved 後建立
  preflight。
- 不得以新 public export、dynamic module loading、unconditional stale delete、schema-1
  `UnsupportedSchemaRecord`、context observation 或 namespace-retaining factory 解決 comment。
- 既有 `response-cache-contract-migration.step.md` 已完整記錄 base migration。這個
  post-implementation PR-comment revision 不重新開啟 `implement-plan` entry gate，也不新增或
  改寫 tracker；本 plan 的 bounded follow-up evidence 由 fresh review / human / code-review /
  preflight gates 記錄。

## Status / Allowed Transitions

- **Current**：`review-ready`。本 plan、analysis 與 Python spec 都改變，下一個有效動作是
  Reviewer 在 declared path 寫入 fresh JSON-only plan review。舊 review 或任一 historical
  human-check 不具本 revision 的 authority。
- **Required route**：`review-ready` → `reviewer-in-progress`。fresh `plan-review.json` 可以先記錄
  `approved` verdict，但 topic 必須維持 `reviewer-in-progress`，直到 Human 在
  `plan/response-cache-contract-migration/response-cache-contract-migration.draft-pr-human-check.json`
  建立 current-plan-SHA-bound Draft-PR human check；兩個 fresh gates 都成立後，才可
  `reviewer-in-progress` → `approved` → `publish-in-progress`。完成 closed implementation list
  後，Reviewer 的 fresh `code-review.yaml` 必須為 approved，Main Agent 才能建立 preflight；
  preflight passed 才可 `publish-in-progress` → `pr-open`。
- **Rework route**：plan review 的 `needs-rework` 依 canonical route 回
  `creator-in-progress`。code review 的 `needs-rework` 不得把
  `publish-in-progress` 轉為 `creator-in-progress`；Main Agent 必須依 canonical
  `pr-comment-review-pr-comments-and-fix` workflow 與既有 role separation，將仍在 closed
  implementation list 內的修復交由 Implementer，並要求 Reviewer 對修復後結果重新產生 fresh
  code-review verdict。任何 scope／contract 變更、觸及 public facade/identity/async baseline，或
  historical human-check byte 變更，都需要回到 `spec-and-plan-finalization`。
- **Merge route**：`pr-open` → `merged` 仍需要 Human 在
  `plan/response-cache-contract-migration/response-cache-contract-migration.human-merge.json`
  明確通過 pre-merge gate。無 release workflow。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Business baseline | `analysis/response-cache-contract-migration/requirements.md` | Existing analysis authority | Strict business guardrail; not modified by this revision. |
| Reconciliation baseline | `analysis/response-cache-contract-migration/canonical-reconciliation.md` | Planning actor | Update the three PR #26 mappings and compatibility/import-surface decisions. |
| Technical baseline | `analysis/response-cache-contract-migration/technical-spec.md` | Planning actor | Update the exact store read union, internal type, factory shape, and negative exports. |
| Topic plan | `plan/response-cache-contract-migration/response-cache-contract-migration.plan.md` | Planning actor | Current execution and fresh-gate contract. |
| Python specification | `plan/response-cache-contract-migration/response-cache-contract-migration.spec.md` | Planning actor | Non-trivial acceptance and behavioral contract. |
| Plan review | `plan/response-cache-contract-migration/response-cache-contract-migration.plan-review.json` | Reviewer | Replace stale verdict with a fresh JSON-only review for this plan SHA. |
| Historical human check | `plan/response-cache-contract-migration/response-cache-contract-migration.human-check.json` | Human | Immutable historical evidence; never modify or use as this revision's approval. |
| Historical implementation tracker | `plan/response-cache-contract-migration/response-cache-contract-migration.step.md` | Implementer (historical) | Completed base-migration record; intentionally not modified or reopened. |
| Draft-PR human check | `plan/response-cache-contract-migration/response-cache-contract-migration.draft-pr-human-check.json` | Human | Fresh, current-plan-SHA-bound gate created only after plan review approval. |
| Human merge | `plan/response-cache-contract-migration/response-cache-contract-migration.human-merge.json` | Human | Explicit pre-merge gate required before `pr-open` may become `merged`. |
| Code review | `plan/response-cache-contract-migration/response-cache-contract-migration.code-review.yaml` | Reviewer | Fresh bounded implementation quality/boundary verdict. |
| Draft-PR preflight | `plan/response-cache-contract-migration/response-cache-contract-migration.draft-pr-preflight.yaml` | Main Agent | Fresh preflight after approved code review; must preserve historical human-check bytes. |
| Compatibility factory | `src/async_model_gateway/response_cache/compat.py` | Implementer | Remove `create`, use predecessor `hasher`, require explicit namespace in `build`, and private-alias target imports. |
| Record/read facade | `src/async_model_gateway/response_cache/record.py`, `src/async_model_gateway/response_cache/cache.py` | Implementer | Define internal unsupported record and classify it as cleanup-then-miss. |
| Store boundaries | `src/async_model_gateway/response_cache/ports/store.py`, `src/async_model_gateway/response_cache/ports/__init__.py`, `src/async_model_gateway/response_cache/_in_memory_store.py` | Implementer | Declare read union, remove ports-root `CacheStore` re-export, and retain coherent token deletion. |
| Tests | `tests/response_cache/test_key_factory.py`, `tests/response_cache/test_canonical_feature_hasher.py`, `tests/response_cache/test_response_cache_contract_migration.py`, `tests/response_cache/test_cache.py`, `tests/response_cache/test_in_memory_store.py`, `tests/response_cache/test_response_cache_package_surface.py` | Implementer | Direct-import behavior, predecessor-hasher golden digests and pair-list ordering, fail-closed `Mapping[str, str]` type coverage, chained UTF-8 failure coverage, factory absence/build behavior, unsupported-schema race/miss, and negative export coverage. |

`README.md`, `VERSION`, `.github/copilot-instructions.md`, CI workflows, and every unlisted path
are explicit no-change paths for this revision. Any drift outside this table returns to planning
rework.

## Implementation Steps

After the required fresh plan review and Draft-PR human check pass, the Implementer performs only
these bounded steps:

1. In `src/async_model_gateway/response_cache/compat.py`, change the deprecated factory to
   `ResponseCacheKeyFactory(hasher)` and `build(*, namespace, model_payload_hash, features)`;
   delete `create`, remove namespace state, and use private aliases for every imported target
   collaborator so no forbidden target name is a `compat` attribute.
2. In `tests/response_cache/test_key_factory.py`,
   `tests/response_cache/test_canonical_feature_hasher.py`, and
   `tests/response_cache/test_response_cache_package_surface.py`, replace `create` coverage with
   explicit-namespace `build` coverage; retain direct predecessor-hasher golden digests and
   pair-list ordering, assert non-`Mapping[str, str]` pairs fail closed with `TypeError`, and
   assert an unencodable Unicode value raises `TypeError` chained from `UnicodeEncodeError`.
   Assert `create` and accidental `compat` / ports-root attributes are absent using ordinary
   imports only; do not use dynamic loading.
3. In `src/async_model_gateway/response_cache/record.py` and
   `src/async_model_gateway/response_cache/ports/store.py`, introduce non-exported
   `UnsupportedSchemaRecord(schema_version, version_token)` and widen only `CacheStore.get` to
   its declared read union. Preserve every `StoredCacheRecord` validation rule, especially exact
   schema version 1.
4. In `src/async_model_gateway/response_cache/cache.py` and
   `src/async_model_gateway/response_cache/_in_memory_store.py`, branch on the internal
   unsupported-schema read result before codec access and run existing atomic
   `delete_if_version` with its observed token. Return `CacheMiss` for deletion success, mismatch,
   or classified cleanup failure; do not change cancellation or defect propagation.
5. In `tests/response_cache/test_response_cache_contract_migration.py`, `test_cache.py`, and
   `test_in_memory_store.py`, add direct tests for the schema-1 invariant, unsupported-schema
   miss/no-decode behavior, token-guarded replacement race, cleanup operational failure, and
   unchanged cancellation. Do not use `importlib`, loaders, `exec`, `eval`, `runpy`, or
   `__import__`.
6. Run the declared focused and full validation, retain the resulting implementation evidence for
   review, and do not edit the historical human-check as part of validation or repair.

## Validation / Acceptance Checks

- Check reconciliation, technical spec, plan, and Python spec agree on all three PR #26 decisions
  and name no unregistered implementation path.
- Confirm `ResponseCacheKeyFactory` accepts only `hasher`, has no namespace field or `create`,
  and `build` returns `CacheKey` only after receiving explicit namespace.
- Confirm `tests/response_cache/test_canonical_feature_hasher.py` directly preserves predecessor
  golden digests and pair-list ordering, rejects non-`Mapping[str, str]` pairs with `TypeError`,
  and exposes strict UTF-8 failure as `TypeError` chained from `UnicodeEncodeError`; it uses only
  ordinary imports and no dynamic loading.
- Confirm `StoredCacheRecord(schema_version != 1)` still raises, whereas only internal
  `UnsupportedSchemaRecord(non_1_schema, observed_token)` may come from `CacheStore.get`.
- Confirm unsupported lookup invokes no codec decode, compare-deletes with the observed token,
  cannot remove a concurrent replacement, and always returns `CacheMiss` for expected cleanup
  outcomes; cancellation and defects propagate unchanged.
- Confirm `CacheStore` imports from `ports.store` but is absent from `ports.__all__` and package
  attributes; confirm `compat.__all__` is unchanged and all forbidden target attributes are absent.
- Confirm all new/changed tests use ordinary imports; no dynamic module loading is introduced.
- Confirm `human-check.json` remains byte-identical. Its historical status cannot satisfy the
  fresh plan review, Draft-PR human check, code review, preflight, or merge gate.
- Required commands after implementation, without selecting or mutating the historical
  human-check:

```text
uv run pytest tests/response_cache/test_key_factory.py tests/response_cache/test_canonical_feature_hasher.py tests/response_cache/test_response_cache_contract_migration.py tests/response_cache/test_cache.py tests/response_cache/test_in_memory_store.py tests/response_cache/test_response_cache_package_surface.py -v --no-cov
uv run pytest tests/response_cache -v --no-cov
uv run pytest
uv run ruff check src tests docs README.md analysis/response-cache-contract-migration plan/response-cache-contract-migration
uv run pyright
uv run pre-commit run --files $(git ls-files -co --exclude-standard | rg -v '^plan/response-cache-contract-migration/response-cache-contract-migration\.human-check\.json$')
```

## Reviewer Handoff

```json
{
  "verdict": "approved | needs-rework",
  "blocking_issues": [],
  "copilot_feedback_triage": {
    "ADDRESS": [],
    "DISCUSS": [],
    "SKIP": []
  }
}
```

## Post-merge / release actions

No release workflow required.

## Open Questions / Unresolved Items

None. The three PR #26 comment resolutions, exact source/test paths, ownership, and fresh-gate
order are frozen.

## Python implementation-planning supplement (13-section extension)

### Goal

Implement only the three reconciled PR #26 contract corrections without changing the established
async cache boundary or historical evidence.

### Non-goals

- No public `ResponseCache` API, `CacheKey` identity/hash, invalidator, context, or legacy-adapter
  placement change.
- No persistent backend, migration format, TTL-policy, timeout, retry, task, queue, or lifecycle
  feature.
- No source/test/CI/documentation change outside the exact Artifact Paths list, and no dynamic
  test import mechanism.

### Current Context

The base migration's implementation tracker and implementation-entry gates already exist as
historical evidence. This revision has a new plan SHA and therefore needs fresh planning and
Draft-PR gates. `StoredCacheRecord` currently rejects non-1 schemas even though lookup must
reclaim an unsupported stored schema safely; `compat` currently retains the obsolete factory
shortcut; and package-surface tests define the required negative exports.

### Requirements

1. Meet all three locked PR #26 decisions and no others.
2. Preserve `StoredCacheRecord.schema_version == 1`, atomic compare-delete, non-persistent
   context, and cancellation/defect propagation.
3. Produce direct test evidence for factory absence/build shape, unsupported-schema cleanup, and
   negative import surfaces.
4. Obtain fresh plan review, Human Draft-PR check, code review, and preflight in order while
   leaving historical human-check bytes untouched.

### Decisions

- Async-planning status: triggered — cite trigger evidence: the existing async `CacheStore.get`
  and `ResponseCache.lookup` cleanup boundary remains active; this revision freezes its
  unsupported-record cleanup, race, operational-failure, and cancellation behavior without
  changing the async baseline.
- Module/package placement: exact source/test paths are in the Artifact Paths table.
- New public API: no; `UnsupportedSchemaRecord` is non-exported internal and factory remains
  `compat`-only.
- Interface changes: yes, `CacheStore.get` submodule-port return annotation widens to its internal
  read union; ports-root exports narrow by removing `CacheStore`.
- Breaking changes allowed: yes, only removal of deprecated `compat.ResponseCacheKeyFactory.create`
  and its namespace-retaining constructor form; the explicit predecessor `build` bridge remains.
- New dependencies: no.
- Error-handling strategy: unsupported schema is a miss after token-guarded cleanup; known cleanup
  operational errors remain miss; cancellation and non-family defects propagate.
- Typing strategy: strict typed frozen/slotted records and explicit union narrowing; no `Any`, no
  dynamic imports, and no public export of the internal read marker.

### Async boundary decision

Only `CacheStore.get` and `delete_if_version` remain awaited. Record validation, factory hashing,
identity, union narrowing, and codec non-use for unsupported schema remain synchronous. No new
async boundary is introduced.

### Resource lifecycle decision

`ResponseCache` still owns no store lifecycle. No client, task, worker, clock owner, or cleanup
resource is created by this revision.

### Concurrency model

Lookup direct-awaits store get and, only for stale/unsupported input, one token-guarded delete.
There is no lock, fan-out, retry, background cleanup, or cross-key coordination. A replacement
with another token survives compare-delete.

### Failure model

`UnsupportedSchemaRecord` is normal read classification, not an exception. Cleanup members of the
existing operational-error family become `CacheMiss`; malformed internal marker construction and
all unexpected defects remain defects.

### Cancellation / timeout policy

The caller owns cancellation. No timeout, retry, shield, or catch-all exception translation is
added; `CancelledError` from either awaited store operation reaches the caller unchanged.

### Validation plan

Run the focused direct-import/factory/store/cache tests, response-cache suite, full suite, ruff,
pyright, and the historical-file-safe pre-commit selector. Validate the historical human-check
digest and terminal byte before and after preflight without including it in a mutating probe.

### Handoff notes for the implementer

Do not infer a broader schema migration: only the two-field internal marker is permitted. Stop for
planning rework if schema parsing needs more fields, a public export, a store API beyond `get`, or
any change to context/atomicity/cancellation. Do not alter the historical tracker or human check.

### Public Contract / API Changes

No new root-public API. The deprecated `compat` constructor/method surface narrows as locked;
`CacheStore.get` changes only on its dedicated submodule-public port, and its additional result is
internal.

### Affected Files / Modules

Likely affected files are exactly the six source paths and six test paths in Artifact Paths.
Candidate planning inputs are the three analysis/spec artifacts listed there. No other file is
authorized.

### Implementation Steps

Use the six canonical steps above in order after fresh gates; no tracker amendment is authorized
for this post-implementation comment revision.

### Test Plan

- Happy path: explicit-namespace factory build produces `CacheKey`; predecessor golden digests
  preserve canonical pair-list ordering; fresh supported record hits.
- Invalid input: non-`Mapping[str, str]` feature pairs, factory/record invalid values, and schema
  1 marker misuse raise defects.
- Edge case: unsupported schema skips decoding and cleanup token mismatch preserves replacement.
- Regression: known cleanup failure remains miss; cancellation remains caller-owned.
- Backward compatibility: deprecated factory still builds; an unencodable Unicode feature value
  raises `TypeError` chained from `UnicodeEncodeError`; `create`, ports-root `CacheStore`, and
  leaked `compat` target attributes are absent by ordinary direct import tests with no dynamic
  loading.

### Validation Commands

Use the commands in **Validation / Acceptance Checks** after fresh plan review and Human Draft-PR
check, and before fresh code review.

### Risks

- Permitting an invalid `StoredCacheRecord` instead of a narrow marker would weaken the schema-1
  invariant and make downstream decoding unsafe.
- An unconditional cleanup could delete a concurrent replacement.
- Accidental root or `compat` exports would turn internal collaborators into unsupported API.
- Reusing stale review/human evidence, or running a formatter against historical human-check, would
  invalidate required gate provenance.

### Rollback Plan

Revert only the exact planning artifacts for this revision before implementation. After a later
implementation failure, revert only the exact registered source/test paths; never edit the
historical human-check, historical step tracker, or other evidence to make a gate pass.

### Open Questions

None.
