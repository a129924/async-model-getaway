# response-cache-contract-migration

## Goal / Outcome

在不擴張 response-cache migration 範圍下，將 PR #26 的三則 actionable review comments
reconcile 到 strict analysis、Python specification 與可執行 plan：deprecated factory 保留唯一
可驗證的 predecessor 形狀；unsupported schema 可安全回收而不破壞 record invariant；target
submodule 的 import surface 不外洩。完成後，本 revision 必須重新取得 fresh plan-review 與
current-file-SHA-256 Human clearance，才可進行唯一的 CI-only implementation。最後必須由新的完整
aggregate reviewer evidence 綁定 base/head/scope/digest，再進入 fresh preflight；既有
historical human check 不得變更。

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
- **In scope（delivery governance）**：freeze immutable historical human-check anchor、final
  aggregate reviewer evidence 的 base/head/scope/digest contract，並在 fresh gates 後僅授權
  `.github/workflows/ci.yml` 加入先掃 historical path、再對其餘檔案套用既有 exact selector
  的兩段 CI sequence。
- **Out of scope**：Planning actor 不修改 Python source、tests、CI、documentation、reviewer、
  human 或 preflight evidence，亦不修改任何 historical artifact。後續 Implementer 不得修改
  source、tests 或 evidence；其唯一新 implementation path 是 declared CI workflow。不得重新規劃
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
- historical human-check 的 immutable anchor 固定為 SHA-256
  `f6ec59dbf3f5df4ba42359b9978c31bebd4bbf30b1645146ba1a4841508d417b`、terminal byte `0x7d`、
  no final LF。後續 CI 必須先以 local-path guard 唯讀掃描這個 exact path，再以目前的
  exact-selector pre-commit command 掃描其餘檔案；selector 的 command text 不得改動，
  historical file 不得傳給可能改寫它的 hook。
- 既有
  `plan/response-cache-contract-migration/response-cache-contract-migration.human-check.json`
  是 immutable historical evidence，Planning actor、Implementer、Reviewer、Main Agent 均不得改寫。
  既有 fresh-human-check、forward-preflight、step tracker 和 implementation review 是先前的
  implementation-entry evidence，不能替代這次 revision 的 fresh plan review 或 Draft-PR gates。
- 本 plan 的唯一 SHA authority 是 topic plan 檔案內容的 SHA-256，不是 Git blob SHA、tree SHA
  或 commit SHA。Planning actor 完成所有 planning-artifact 修改後，必須以
  `shasum -a 256 plan/response-cache-contract-migration/response-cache-contract-migration.plan.md`
  重新計算此檔案的 digest。fresh `plan-review.json` 的 `reviewed_plan_sha256` 與 Human
  Draft-PR check 的 `reviewed_plan_sha256` 都必須等於該命令在各自寫入前重新計算的相同
  64-hex digest；任何 plan-byte drift 都使兩個 gate 失效並要求重新 review、再重新計算後
  取得 Human binding。
- 本 plan 檔案內容改變後，現有 `plan-review.json`、`draft-pr-human-check.json`、`code-review.yaml`
  與 `draft-pr-preflight.yaml` 都不能核准本 revision。順序固定為：fresh independent
  plan-review → Human 建立 current-file-SHA-256-bound Draft-PR human check → bounded CI-only
  implementation → fresh final aggregate code review → Main Agent fresh Draft-PR preflight →
  `pr-open`。Planning actor 不得預填任何 evidence。
- 最終 aggregate reviewer artifact 必須固定 base revision
  `dbba2efb6ab4a8b802dfdb122e561ad576fdea53`，在 reviewer 寫入時固定 exact committed head、
  ordered closed scope 與 `git diff --binary <base> <head> -- <scope>` 的 SHA-256。其自身與所有
  gate artifacts 不得位於 scope，避免 self-reference；任何 scoped drift 均使 evidence 失效。

## Boundaries / Exclusions

- Planning actor 僅可修改本 plan 及本 revision 在 Artifact Paths 列出的 analysis/spec artifacts；
  不實作、不建立 reviewer/human/preflight artifacts，也不改 step tracker。
- Implementer 僅在 fresh plan review 與 Human Draft-PR check 已通過後修改
  `.github/workflows/ci.yml`；不得回寫 planning、source、tests、historical human check 或任何
  existing evidence。
- Reviewer 只產生 fresh `plan-review.json` 與 final aggregate code-review verdict；Human 只產生 explicit
  Draft-PR human check 與 human merge；Main Agent 只在 fresh code review approved 後建立
  preflight。
- 不得以新 public export、dynamic module loading、unconditional stale delete、schema-1
  `UnsupportedSchemaRecord`、context observation 或 namespace-retaining factory 解決 comment。
- 既有 `response-cache-contract-migration.step.md` 已完整記錄 Cache BC implementation。這個
  governance revision 不重新開啟 source/test implementation 或改寫 tracker；其 bounded CI-only
  execution 與 fresh review / human / aggregate code-review / preflight gates 另行記錄。

## Status / Allowed Transitions

- **Current**：`review-ready`。本 plan、analysis 與 Python spec 都改變，下一個有效動作是
  Reviewer 在 declared path 寫入 fresh JSON-only plan review。舊 review 或任一 historical
  human-check 不具本 revision 的 authority。
- **Required route**：`review-ready` → `reviewer-in-progress`。fresh `plan-review.json` 可以先記錄
  `approved` verdict，但 topic 必須維持 `reviewer-in-progress`，直到 Human 在
  `plan/response-cache-contract-migration/response-cache-contract-migration.draft-pr-human-check.json`
  建立 current-file-SHA-256-bound Draft-PR human check；兩個 fresh gates 都成立後，才可
  `reviewer-in-progress` → `approved` → `publish-in-progress`。完成 bounded CI-only implementation
  後，Reviewer 的 fresh `final-aggregate-review.yaml` 必須為 approved，Main Agent 才能建立 preflight；
  preflight passed 才可 `publish-in-progress` → `pr-open`。
- **Rework route**：plan review 的 `needs-rework` 依 canonical status route
  `reviewer-in-progress` → `needs-rework` → `creator-in-progress` 處理。pre-PR final aggregate
  review 的 `needs-rework` 是 `implement-plan` 的未通過 gate verdict，不是 topic status：在
  `publish-in-progress` 保持未完成、不得轉為 `pr-open`、不得進入 `pr-comment` 或
  `pr-comment-review-pr-comments-and-fix`。Main Agent 將 closed CI-only repair 交回
  `implement-plan`，Implementer 只修復 `.github/workflows/ci.yml`，重新執行所有 validation
  及 immutable-anchor pre/post checks，並交付新的 committed candidate；Reviewer 必須對新 head
  取代式地重做 final aggregate review。只有新的 aggregate `approved` 才能由 Main Agent 建立
  新的 Draft-PR preflight；preflight 不通過同樣回到這個 `implement-plan` → aggregate →
  preflight loop。此 loop 在 PR 開啟前不使用 PR-comment phase。若 repair 需要 scope、artifact
  paths、public contract、async baseline 或 historical human-check bytes 改變，停止 loop 並回到
  `spec-and-plan-finalization`，以 canonical planning rework 重新取得 gates。
- **Merge route**：`pr-open` → `merged` 仍需要 Human 在
  `plan/response-cache-contract-migration/response-cache-contract-migration.human-merge.json`
  明確通過 pre-merge gate。無 release workflow。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Business baseline | `analysis/response-cache-contract-migration/requirements.md` | Existing analysis authority | Strict business guardrail; not modified by this revision. |
| Reconciliation baseline | `analysis/response-cache-contract-migration/canonical-reconciliation.md` | Planning actor | Preserve the three PR #26 mappings and add the delivery-governance reconciliation. |
| Technical baseline | `analysis/response-cache-contract-migration/technical-spec.md` | Planning actor | Preserve the Cache BC technical contract and add exact CI/evidence governance. |
| Topic plan | `plan/response-cache-contract-migration/response-cache-contract-migration.plan.md` | Planning actor | Current execution, aggregate-evidence, and fresh-gate contract. |
| Python specification | `plan/response-cache-contract-migration/response-cache-contract-migration.spec.md` | Planning actor | Non-trivial Cache BC contract plus CI/evidence acceptance scenarios. |
| Plan review | `plan/response-cache-contract-migration/response-cache-contract-migration.plan-review.json` | Reviewer | Replace stale verdict with a fresh JSON-only review bound to the recomputed SHA-256 of this plan file's bytes. |
| Historical human check | `plan/response-cache-contract-migration/response-cache-contract-migration.human-check.json` | Human | Immutable historical evidence; never modify or use as this revision's approval. |
| Historical implementation tracker | `plan/response-cache-contract-migration/response-cache-contract-migration.step.md` | Implementer (historical) | Completed base-migration record; intentionally not modified or reopened. |
| Draft-PR human check | `plan/response-cache-contract-migration/response-cache-contract-migration.draft-pr-human-check.json` | Human | Fresh gate created only after plan review approval and bound to the then-recomputed SHA-256 of this plan file's bytes. |
| Human merge | `plan/response-cache-contract-migration/response-cache-contract-migration.human-merge.json` | Human | Explicit pre-merge gate required before `pr-open` may become `merged`. |
| Historical code review | `plan/response-cache-contract-migration/response-cache-contract-migration.code-review.yaml` | Reviewer (historical) | Stale prior evidence; preserve without editing and do not use as this revision's final gate. |
| Final aggregate code review | `plan/response-cache-contract-migration/response-cache-contract-migration.final-aggregate-review.yaml` | Reviewer | New final evidence with fixed base/head/scope/digest after CI-only implementation. |
| Draft-PR preflight | `plan/response-cache-contract-migration/response-cache-contract-migration.draft-pr-preflight.yaml` | Main Agent | Fresh preflight only after approved final aggregate review; must preserve historical human-check bytes. |
| CI workflow | `.github/workflows/ci.yml` | Implementer | Add the read-only local-path-guard invocation for the exact historical path before the existing byte-identical exact-selector pre-commit command. |
| Historical Cache BC source | `src/async_model_gateway/response_cache/compat.py`, `src/async_model_gateway/response_cache/record.py`, `src/async_model_gateway/response_cache/cache.py`, `src/async_model_gateway/response_cache/_in_memory_store.py`, `src/async_model_gateway/response_cache/ports/store.py`, `src/async_model_gateway/response_cache/ports/__init__.py` | Existing implementation | Locked aggregate-review scope only; no further change is authorized. |
| Historical Cache BC tests | `tests/response_cache/test_key_factory.py`, `tests/response_cache/test_canonical_feature_hasher.py`, `tests/response_cache/test_response_cache_contract_migration.py`, `tests/response_cache/test_cache.py`, `tests/response_cache/test_in_memory_store.py`, `tests/response_cache/test_response_cache_package_surface.py` | Existing implementation | Locked aggregate-review scope only; no further change is authorized. |

`README.md`, `VERSION`, `.github/copilot-instructions.md`, all source/test paths, every existing
reviewer/human/preflight artifact, and every unlisted path are explicit no-change paths for this
revision. `.github/workflows/ci.yml` is the sole later implementation exception. Any drift outside
this table returns to planning rework.

The final aggregate review must use this ordered closed scope in its literal diff command:

1. `.github/workflows/ci.yml`
2. `analysis/response-cache-contract-migration/canonical-reconciliation.md`
3. `analysis/response-cache-contract-migration/technical-spec.md`
4. `plan/response-cache-contract-migration/response-cache-contract-migration.plan.md`
5. `plan/response-cache-contract-migration/response-cache-contract-migration.spec.md`
6. `src/async_model_gateway/response_cache/compat.py`
7. `src/async_model_gateway/response_cache/record.py`
8. `src/async_model_gateway/response_cache/cache.py`
9. `src/async_model_gateway/response_cache/_in_memory_store.py`
10. `src/async_model_gateway/response_cache/ports/store.py`
11. `src/async_model_gateway/response_cache/ports/__init__.py`
12. `tests/response_cache/test_key_factory.py`
13. `tests/response_cache/test_canonical_feature_hasher.py`
14. `tests/response_cache/test_response_cache_contract_migration.py`
15. `tests/response_cache/test_cache.py`
16. `tests/response_cache/test_in_memory_store.py`
17. `tests/response_cache/test_response_cache_package_surface.py`

## Implementation Steps

After the required fresh plan review and current-file-SHA-256 Draft-PR human check pass, the
Implementer performs only these bounded steps:

1. In `.github/workflows/ci.yml`, add one named step immediately before the existing
   `Run pre-commit` step. Its command is exactly
   `uv run python -m async_model_gateway._repo_hooks.local_path_guard plan/response-cache-contract-migration/response-cache-contract-migration.human-check.json`.
   The step is read-only and applies only to that historical path.
2. In the same file, retain the existing `Run pre-commit` command byte-for-byte:
   `uv run pre-commit run --files $(git ls-files -co --exclude-standard | rg -v '^plan/response-cache-contract-migration/response-cache-contract-migration\.human-check\.json$')`.
   It remains the second phase, selects every other file, and does not gain a skip, hook override,
   broad exclusion, or alternate selector.
3. Before and after the CI validation sequence, run the declared immutable-anchor commands without
   writing, formatting, staging, restoring, or passing the historical file to any hook. Record
   both command-result sets for Reviewer together with the final committed candidate. Do not
   change source, tests, planning artifacts, reviewer/human/preflight artifacts, or the historical
   implementation tracker.

## Validation / Acceptance Checks

- Confirm reconciliation, technical spec, plan, and Python spec preserve the locked Cache BC
  contract while agreeing on the exact CI/evidence revision and no unregistered implementation path.
- Confirm CI invokes the exact historical-path local-path guard before the unchanged exact-selector
  pre-commit command; no skip, override, broad exclusion, or alternate selector is present.
- Confirm the historical human-check remains SHA-256
  `f6ec59dbf3f5df4ba42359b9978c31bebd4bbf30b1645146ba1a4841508d417b`, terminal byte `0x7d`, and
  without a final LF both before and after the CI sequence, using the exact non-writing commands
  below. `git diff --exit-code -- <historical-path>` must also succeed in both result sets. Its
  status cannot satisfy the fresh plan review, current-file-SHA-256 Human check, final aggregate
  review, preflight, or merge gate.
- Confirm every locked source/test contract remains unchanged by this revision, including direct
  imports only, no dynamic loading, schema-1 invariant, token-guarded cleanup, and narrow
  compatibility/export surfaces.
- Confirm the final aggregate reviewer artifact has base
  `dbba2efb6ab4a8b802dfdb122e561ad576fdea53`, one exact committed head, all 17 ordered scope paths,
  the literal scoped binary-diff command, its SHA-256 digest, and proof of no post-head scoped
  drift. It must not treat itself or any gate artifact as part of that digest.
- Required commands after implementation. Run the first three commands as an immutable-anchor
  **pre** set before CI validation and again as an immutable-anchor **post** set after it. They
  are read-only checks; do not substitute a formatter, restore, stage, or any mutating command for
  them, and never pass the historical path to pre-commit:

```text
shasum -a 256 plan/response-cache-contract-migration/response-cache-contract-migration.human-check.json
test "$(tail -c 1 plan/response-cache-contract-migration/response-cache-contract-migration.human-check.json | od -An -t x1 | tr -d '[:space:]')" = "7d" && test "$(tail -c 1 plan/response-cache-contract-migration/response-cache-contract-migration.human-check.json | od -An -t x1 | tr -d '[:space:]')" != "0a"
git diff --exit-code -- plan/response-cache-contract-migration/response-cache-contract-migration.human-check.json
uv run python -m async_model_gateway._repo_hooks.local_path_guard plan/response-cache-contract-migration/response-cache-contract-migration.human-check.json
uv run pre-commit run --files $(git ls-files -co --exclude-standard | rg -v '^plan/response-cache-contract-migration/response-cache-contract-migration\.human-check\.json$')
uv run pytest
uv run ruff check src tests docs README.md analysis/response-cache-contract-migration plan/response-cache-contract-migration
uv run pyright
```

### Final aggregate reviewer evidence contract

Only Reviewer creates
`plan/response-cache-contract-migration/response-cache-contract-migration.final-aggregate-review.yaml`,
and only after the CI-only change is committed. The artifact must be a complete aggregate verdict,
not a pointer to prior review artifacts, and must contain all of the following:

- `review: final-aggregate-implementation-conformance-and-python-code-review`, `topic`,
  `reviewer`, `verdict`, and `review_status`;
- `reviewed_change.base_revision` exactly
  `dbba2efb6ab4a8b802dfdb122e561ad576fdea53`;
- `reviewed_change.head_revision` equal to the exact committed candidate reviewed, together with
  `head_is_immutable_for_review: true`;
- `reviewed_change.scope_paths` equal, in the declared order, to all 17 paths in Artifact Paths;
- `reviewed_change.scope_command`, the literal `git diff --binary <base> <head> -- <scope>`
  command using those concrete revisions and paths, and `reviewed_change.diff_sha256` calculated
  from its byte stream;
- `reviewed_change.changed_scope_paths`, a checked subset of `scope_paths`, plus a proof that
  `git diff --name-only <head> HEAD -- <scope>` is empty when preflight begins;
- `immutable_historical_anchor.pre` and `immutable_historical_anchor.post`, each recording the
  `shasum -a 256` output/digest, `terminal_byte_hex: "0x7d"`,
  `final_lf_present: false`, and `git_diff_exit_code: 0` from the exact non-writing commands
  above, together with `pre_equals_post: true`; and
- full implementation conformance, Cache BC boundary, test/validation, CI-sequence, scope-creep,
  and governance verdicts. Existing review artifacts may be cited only as historical provenance,
  never as a substitute for this aggregate verdict.

## Reviewer Handoff

```json
{
  "verdict": "approved | needs-rework",
  "reviewed_plan_sha256": "SHA-256 of the current topic plan file bytes, recomputed immediately before reviewer write; not a Git object SHA",
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

Preserve the locked Cache BC implementation and add only the two-stage CI verification plus
reproducible final aggregate review contract, without changing runtime behavior or historical
evidence.

### Non-goals

- No public `ResponseCache` API, `CacheKey` identity/hash, invalidator, context, or legacy-adapter
  placement change.
- No persistent backend, migration format, TTL-policy, timeout, retry, task, queue, or lifecycle
  feature.
- No source, test, documentation, reviewer, human, or preflight artifact change; CI may change
  only at `.github/workflows/ci.yml` as the two exact declared commands require.

### Current Context

The Cache BC source and direct-import tests are already locked historical implementation scope.
This plan revision changes its file SHA-256 and therefore requires fresh plan review followed by
Human clearance bound to the recomputed current file digest, never a Git object SHA. The historical human-check has a deliberately non-normalized
EOF, so CI must check it read-only before the existing selector runs hooks on every other file.

### Requirements

1. Preserve every locked Cache BC decision without modifying source or tests.
2. Run local-path guard on only the exact historical human-check path before the unchanged
   exact-selector pre-commit command checks every other file.
3. Keep the historical anchor SHA-256, terminal byte, no-final-LF state, and clean Git diff
   unchanged in non-writing pre/post checks.
4. Obtain fresh plan review, current-file-SHA-256 Human Draft-PR clearance, final aggregate review,
   and fresh preflight in order.

### Decisions

- Async-planning status: exempt — cite exemption evidence: this revision changes only CI command
  ordering and evidence provenance; it introduces no async boundary, lifecycle, concurrency,
  failure translation, cancellation, or timeout behavior.
- Module/package placement: only `.github/workflows/ci.yml` may receive implementation edits;
  the exact planning and historical aggregate scope paths are in Artifact Paths.
- New public API: no.
- Interface changes: yes, CI gains one read-only validation step before its existing pre-commit
  step; no Python interface changes.
- Breaking changes allowed: no; the existing selector is retained byte-for-byte and all Cache BC
  contracts remain unchanged.
- New dependencies: no.
- Error-handling strategy: local-path findings, historical-anchor mismatch, nonzero historical
  Git diff, hook failure, selector drift, or post-review scoped drift fail their gate; none permits
  rewriting historical evidence.
- Typing strategy: no Python production or test code changes; existing strict typing baseline is
  validated unchanged.

### Public Contract / API Changes

No public API changes. The locked compatibility factory, internal record marker, store union, and
negative exports are historical aggregate-review scope only.

### Affected Files / Modules

Likely implementation file: `.github/workflows/ci.yml` only. Candidate planning inputs are the
three analysis/spec artifacts listed in Artifact Paths; historical source/test paths are reviewed
but cannot be edited. No other file is authorized.

### Implementation Steps

Use the three canonical CI-only steps above in order after fresh gates; no tracker amendment is
authorized for this governance revision.

### Test Plan

Test file: `tests/test_local_path_guard.py` is existing read-only regression coverage; this revision
adds no test file because the CI command order, immutable anchor, and selector are validated by the
declared workflow commands and final aggregate review.

- Happy path: CI local-path guard accepts the anchored historical file, then the unchanged selector
  runs hooks on all other selected files.
- Invalid input: an introduced local path or altered anchor makes the applicable validation gate fail.
- Edge case: the historical no-final-LF file is never supplied to a hook that would normalize it.
- Regression: full pytest and pyright preserve all Cache BC behavior and strict types without source
  or test edits.
- Backward compatibility: the final aggregate review confirms the locked factory, schema, race,
  and ordinary-import contracts are unchanged.

### Validation Commands

Use the commands in **Validation / Acceptance Checks** after fresh plan review and current-file-SHA-256
Human Draft-PR clearance, and before final aggregate code review.

### Risks

- Modifying the selector while adding the separate guard could leave paths unchecked or hand the
  historical file to a mutating hook.
- A self-referential or partial review digest could claim coverage without binding the final change.
- Reusing stale review/human evidence, or running a formatter against historical human-check, would
  invalidate required gate provenance.

### Rollback Plan

Revert only the four planning artifacts before implementation. After a later CI failure, revert
only `.github/workflows/ci.yml`; never edit the historical human-check, source/tests, tracker, or
reviewer/human/preflight evidence to make a gate pass.

### Open Questions

None.
