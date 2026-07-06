Analysis-layer routing: strict mode. `analysis/response-cache-operational-minimal-boundary/technical-spec.md` is the execution-facing source of truth for this topic, and `analysis/response-cache-operational-minimal-boundary/requirements.md` remains the business guardrail. The chat contract is already aligned with these artifacts and does not override them.

# response-cache-operational-minimal-boundary

## Goal / Outcome

- 凍結一個 repo-visible、最小且 operational 的 response-cache boundary，使後續 Python implementation 能在既有 keyed boundary 上新增 `ResponseCache`、`ResponseCacheEntry` 與 `ResponseCacheStore`，而不必重新打開 backend、policy 或 orchestrator scope。
- 當此 topic 完成時，repository 會擁有完整的 analysis 與 planning artifacts，明確鎖定最小 async operational API、package-root export policy、submodule-public store port，以及 reviewer 與 human gate 的 repo-visible 路徑。

## Scope

- **In scope**:
  - `analysis/response-cache-operational-minimal-boundary/requirements.md` 與 `analysis/response-cache-operational-minimal-boundary/technical-spec.md` 的 analysis-layer baseline。
  - `plan/response-cache-operational-minimal-boundary/` 下的 topic plan、behavior spec、step tracking 與 review-support path contract。
  - `src/async_model_gateway/response_cache/__init__.py`、`cache.py`、`entry.py`、`ports/__init__.py`、`ports/store.py` 的最小 operational cache boundary 規劃。
  - `tests/response_cache/test_response_cache_package_surface.py`、`test_cache.py`、`test_entry.py` 的新 coverage 規劃，以及既有 `test_key.py`、`test_key_factory.py` 的 preserve-and-validate routing。
  - `docs/architecture.md` 與 `docs/specs/response-cache-boundary.md` 的 boundary wording 對齊。

- **Out of scope**:
  - 任何 concrete `ResponseCacheStore` implementation、backend adapter 或 persistence schema。
  - 任何 TTL、eviction、invalidation、serialization、metrics、tracing 或 freshness policy。
  - 任何 `orchestrator` wiring、response-generation flow、provider/model integration。
  - 任何重新設計 `ResponseCacheKey`、`ResponseCacheKeyFactory` 或 `FeatureHasher`。
  - 任何將 `ResponseCacheEntry` 擴張為 metadata-bearing payload 的工作。
  - 任何 stable-library、release、tag 或 versioning work。

## Locked Decisions

- Analysis-layer strict mode 已啟用：`analysis/response-cache-operational-minimal-boundary/technical-spec.md` 是 execution-facing source of truth，而 `analysis/response-cache-operational-minimal-boundary/requirements.md` 是 business guardrail。
- 此 topic 採 Python planning extension path，並要求 companion `*.spec.md`、`*.step.md`、review-support artifact paths 與後續 implementation-review evidence paths。
- D1 verdict: `non-trivial`。此 topic 會新增 public Python surfaces、async boundary decisions、新 tests 與 docs updates。
- `ResponseCache` 是此 topic 的 public owner；它消費既有 `ResponseCacheKey`，不重新計算 payload hash 或 feature hash。
- `ResponseCacheEntry` 是此 topic 的 public value type，且只允許 `response: str` 一個欄位。
- `ResponseCacheStore` 是此 topic 的 public store port，但必須維持 submodule-public 於 `async_model_gateway.response_cache.ports.store`；`async_model_gateway.response_cache` 與 `async_model_gateway.response_cache.ports` 都不得 re-export 它。
- package root 必須 re-export：
  - `ResponseCache`
  - `ResponseCacheEntry`
  - 既有 `ResponseCacheKey`
  - 既有 `ResponseCacheKeyFactory`
- public `ResponseCache` API 已凍結為：
  - `ResponseCache(store: ResponseCacheStore)`
  - `async def get(self, *, key: ResponseCacheKey) -> ResponseCacheEntry | None`
  - `async def set(self, *, key: ResponseCacheKey, entry: ResponseCacheEntry) -> None`
- Async-planning status: `triggered` — cite trigger evidence: 此 topic 新增 public async `ResponseCache.get(...)` / `set(...)` 與 async `ResponseCacheStore.get(...)` / `set(...)` boundary，必須在 implementation 前凍結 async boundary、resource ownership、direct-await concurrency、failure propagation，以及不引入 timeout / retry / sync mirror 的限制。
- async-only baseline 已鎖定：此 topic 必須用 async `get` / `set` owner contract 表達最小 operational boundary，不新增 sync mirror 或 broader concurrency/policy surface。
- workflow conflict 已凍結處理：repo canonical topic-plan order 與 `python-plan-authoring` 的 13-section `*.plan.md` 結構互相衝突；最保守做法是讓本 topic 的 `.plan.md` 優先遵守 repo-level canonical contract，而將 Python 行為契約與 step tracking 分別放在 `.spec.md` 與 `.step.md`。
- 此 topic 是 non-stable-library。`## Stable library metadata` 刻意省略，且不宣告 release workflow。

### Async boundary decision

- 只有 `ResponseCache` 與 `ResponseCacheStore` 的 public `get` / `set` contract 是 async；`ResponseCacheEntry`、既有 `ResponseCacheKey` 與既有 `ResponseCacheKeyFactory` 維持同步 value/helper surfaces。

### Resource lifecycle decision

- `ResponseCache` 只持有呼叫端提供的 `ResponseCacheStore` reference，不建立、共享、關閉、flush 或 reset 底層 store resources。

### Concurrency model

- `ResponseCache.get(...)` 與 `set(...)` 都只做單次 direct await delegation；此 topic 不加入 fan-out、batching、queue、worker ownership、backpressure 或 background task semantics。

### Failure model

- store-raised exceptions 原樣向外傳播；`ResponseCache.get(...) -> None` 僅代表 cache miss，不代表 swallowed failure，也不觸發 fallback behavior。

### Cancellation / timeout policy

- 此 topic 不新增 timeout、retry、circuit breaker 或 cancellation wrapper；任何 awaitable cancellation semantics 維持由 store 實作者與 caller runtime 擁有。

### Validation plan

- planned tests 與 reviewer checks 必須證明 async owner/store signatures、direct delegation、miss-as-`None` semantics、store failure propagation，以及 package root 與 `async_model_gateway.response_cache.ports` 都不 re-export `ResponseCacheStore`。

### Handoff notes for the implementer

- 若 implementation 需要額外 lifecycle ownership、timeout/retry policy、sync mirror API、multi-call concurrency，或想讓 `ResponseCacheStore` 被 package root / `async_model_gateway.response_cache.ports` re-export，必須停止並回到 `spec-and-plan-finalization`，不能在 `implement-plan` 內自行擴張。

## Boundaries / Exclusions

- Planning actor 只負責此 topic 的 analysis 與 planning artifacts，不實作 source code、不填 reviewer verdict，也不關閉 human gates。
- Implementer 只能修改 `## Artifact Paths` 中宣告的精確 docs/source/test/topic-artifact paths；任何超出這些路徑的 drift 都必須回到 `spec-and-plan-finalization`。
- Reviewer 提供獨立的 plan review 與後續 implementation-review evidence；reviewer 不替 implementer 完成步驟，也不代替 human gate。
- Human-owned 的 `human check` 與 `human merge` gates 仍然位於 creator-owned artifacts 之外，不能在此 topic 下預填為已通過。
- 既有 `tests/response_cache/test_key.py` 與 `tests/response_cache/test_key_factory.py` 在此 topic 中是 preserve-and-validate regression surface，不應被當作重新設計 keyed boundary 的入口。

## Status / Allowed Transitions

- **Current**: `review-ready`
- **Execution model**: follow `spec-and-plan-finalization -> implement-plan -> pr-comment -> pr-comment-review-pr-comments-and-fix`; stop at `merged`，因為此 topic 不使用條件式 `release` workflow。
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

- `approved` 需要 `plan/response-cache-operational-minimal-boundary/response-cache-operational-minimal-boundary.plan-review.json` 記錄 `approved` verdict，且需要獨立的 `plan/response-cache-operational-minimal-boundary/response-cache-operational-minimal-boundary.human-check.json` 明確通過 human check。
- 這次 repair 只修正 creator-owned validation contract，不改動 public API、artifact paths 或 source/test/docs scope；先前較窄 pytest subset 對 coverage gate 不誠實，因此更新後的 plan 必須重新經過 plan review，且 reviewer 接受後仍需新的 human check，才能把 repaired contract 視為已重新 cleared。
- 此 topic 使用 Python planning extension path；在 `implement-plan` 期間，RED test authoring 是 source edits 前的第一個必要 Python 子階段。
- `*.step.md`、`*.spec.md`、`*.red-tests.yaml` 與 `*.implementation-review.yaml` 都只是 workflow companion artifacts；在對應 gate actor 更新前，它們本身不代表 approval 或 implementation completion。
- 任何改動 public API、artifact paths、`ResponseCacheEntry` 欄位、store exposure policy 或 async baseline 的 rework，都必須讓 topic 回到 `spec-and-plan-finalization`。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Requirements baseline | `analysis/response-cache-operational-minimal-boundary/requirements.md` | Planning actor | operational cache boundary 的 frozen business-intent baseline |
| Technical specification | `analysis/response-cache-operational-minimal-boundary/technical-spec.md` | Planning actor | downstream planning 與 implementation 必須遵守的 execution-facing technical baseline |
| Topic plan | `plan/response-cache-operational-minimal-boundary/response-cache-operational-minimal-boundary.plan.md` | Planning actor | 此 topic 的 repo-visible execution contract |
| Topic behavior spec | `plan/response-cache-operational-minimal-boundary/response-cache-operational-minimal-boundary.spec.md` | Planning actor | non-trivial Python behavior contract，供 RED tests 與後續 review 使用 |
| Topic step tracking | `plan/response-cache-operational-minimal-boundary/response-cache-operational-minimal-boundary.step.md` | Implementer | repo-visible implementation-progress companion artifact |
| Plan review artifact | `plan/response-cache-operational-minimal-boundary/response-cache-operational-minimal-boundary.plan-review.json` | Reviewer | repo-visible planning gate verdict |
| RED test artifact | `plan/response-cache-operational-minimal-boundary/response-cache-operational-minimal-boundary.red-tests.yaml` | Implementer | `implement-plan` 期間產出的 repo-visible TDD gate evidence |
| Implementation review artifact | `plan/response-cache-operational-minimal-boundary/response-cache-operational-minimal-boundary.implementation-review.yaml` | Reviewer | repo-visible implementation-review gate evidence |
| Human check gate evidence | `plan/response-cache-operational-minimal-boundary/response-cache-operational-minimal-boundary.human-check.json` | Human | human-owned repo-visible gate evidence that clears the approved plan for `implement-plan` |
| Architecture summary | `docs/architecture.md` | Implementer | 對齊 minimal operational response-cache boundary 的高層 wording |
| Response-cache boundary spec | `docs/specs/response-cache-boundary.md` | Implementer | 對齊 keyed-plus-operational response-cache boundary wording |
| Response-cache package root | `src/async_model_gateway/response_cache/__init__.py` | Implementer | 擴張 root import surface，但維持 store port 非 root-public |
| Response-cache owner | `src/async_model_gateway/response_cache/cache.py` | Implementer | 最小 operational `ResponseCache` owner |
| Response-cache entry value type | `src/async_model_gateway/response_cache/entry.py` | Implementer | 單欄位 `ResponseCacheEntry` value surface |
| Response-cache ports package root | `src/async_model_gateway/response_cache/ports/__init__.py` | Implementer | 維持 ports package 邊界，但不得 re-export `ResponseCacheStore` |
| Response-cache store port | `src/async_model_gateway/response_cache/ports/store.py` | Implementer | submodule-public async store contract |
| Response-cache package-surface tests | `tests/response_cache/test_response_cache_package_surface.py` | Implementer | 驗證 root export policy 與 submodule-public store exposure |
| Response-cache owner tests | `tests/response_cache/test_cache.py` | Implementer | 驗證 `ResponseCache` async delegation、miss/hit semantics 與 failure propagation |
| Response-cache entry tests | `tests/response_cache/test_entry.py` | Implementer | 驗證 `ResponseCacheEntry` 只有 `response: str` 且保持 immutable contract |
| Existing keyed key tests | `tests/response_cache/test_key.py` | Implementer | preserve-and-validate regression coverage；不預期修改，除非 reviewer-approved rework 明確需要 |
| Existing keyed factory tests | `tests/response_cache/test_key_factory.py` | Implementer | preserve-and-validate regression coverage；不預期修改，除非 reviewer-approved rework 明確需要 |

Artifact path notes:

- 此 topic 不修改 `README.md`、`VERSION` 或 `.github/copilot-instructions.md`。
- listed paths 是 executable contract；若 implementation 需要新增 concrete backend、orchestrator 或 broader package-root paths，必須停止並回到 `spec-and-plan-finalization`。
- `tests/response_cache/test_key.py` 與 `tests/response_cache/test_key_factory.py` 被列入是為了 preserve-and-validate routing，不代表 keyed boundary 被重新打開。
- `response-cache-operational-minimal-boundary.plan-review.json` 與 `response-cache-operational-minimal-boundary.human-check.json` 是後續 gate actors 的 evidence paths；plan authoring 只宣告它們，不預填 verdict、cleared state 或 passed state。

## Implementation Steps

1. 在 `tests/response_cache/test_response_cache_package_surface.py`、`tests/response_cache/test_cache.py` 與 `tests/response_cache/test_entry.py` 補上 RED coverage，並記錄 `plan/response-cache-operational-minimal-boundary/response-cache-operational-minimal-boundary.red-tests.yaml`，使新的 operational boundary 先以 tests 鎖定；同時把 `tests/response_cache/test_key.py` 與 `tests/response_cache/test_key_factory.py` 納入 preserve-and-validate regression matrix。
2. 新增或更新 `src/async_model_gateway/response_cache/__init__.py`、`src/async_model_gateway/response_cache/cache.py`、`src/async_model_gateway/response_cache/entry.py`、`src/async_model_gateway/response_cache/ports/__init__.py` 與 `src/async_model_gateway/response_cache/ports/store.py`，使 package root re-export `ResponseCache`、`ResponseCacheEntry`、既有 `ResponseCacheKey` 與既有 `ResponseCacheKeyFactory`，並讓 `ResponseCacheStore` 只維持在 `async_model_gateway.response_cache.ports.store`，不由 package root 或 `async_model_gateway.response_cache.ports` re-export。
3. 更新 `docs/architecture.md` 與 `docs/specs/response-cache-boundary.md`，使 repo-visible wording 反映：既有 keyed boundary 已存在，而最小 operational `ResponseCache` 現在只透過 async store port 消費 `ResponseCacheKey` 與 `ResponseCacheEntry`。
4. 執行 repo-consistent 的 selected pytest suite：`uv run pytest tests/response_cache/test_response_cache_package_surface.py tests/response_cache/test_cache.py tests/response_cache/test_entry.py tests/response_cache/test_key.py tests/response_cache/test_key_factory.py tests/model_registry/model_payload/test_canonical_hash.py tests/model_registry/stores/test_in_memory.py tests/model_registry/stores/test_stores_package_surface.py tests/model_registry/test_freshness_policy.py tests/model_registry/test_registry.py tests/test_package_entrypoint.py tests/test_local_path_guard.py -v`，再執行 `uv run ruff check docs src tests plan/response-cache-operational-minimal-boundary` 與 `uv run pyright`，更新 `plan/response-cache-operational-minimal-boundary/response-cache-operational-minimal-boundary.step.md`，並把 reviewer-owned artifacts 留給後續角色填寫。

## Validation / Acceptance Checks

- Canonical topic-plan sections、status names、transitions 與 reviewer handoff shape 必須持續符合 `plan/topic-plan-contract.md` 與 `plan/agent-handoff-workflow.md`。
- analysis layer 必須完整：`requirements.md` 與 `technical-spec.md` 兩者都存在，且 plan 採 strict analysis routing。
- `response-cache-operational-minimal-boundary.spec.md` 必須存在，因為此 topic 被鎖為 `non-trivial`。
- `response-cache-operational-minimal-boundary.step.md` 必須 mirror 每個編號 implementation step，且除了 `plan-authoring` 之外不得預先完成後續 workflow stages 或 implementation steps。
- `response-cache-operational-minimal-boundary.human-check.json` 必須保持為 human-owned pending gate evidence path；在 human 明確清 gate 前，不得把 topic 視為可進入 `implement-plan`。
- pytest validation evidence 必須使用已宣告的 selected suite，並在 repository coverage gate 下通過；不得以未回寫到 creator-owned contract 的較窄 response-cache-only subset 或其他替代命令取代。
- selected suite 中追加的 `tests/model_registry/model_payload/test_canonical_hash.py`、`tests/model_registry/stores/test_in_memory.py`、`tests/model_registry/stores/test_stores_package_surface.py`、`tests/model_registry/test_freshness_policy.py`、`tests/model_registry/test_registry.py`、`tests/test_package_entrypoint.py` 與 `tests/test_local_path_guard.py` 只用於 repo-consistent validation，並不擴張此 topic 的 source、docs 或 behavior scope。
- package-surface validation 必須證明 package root re-export `ResponseCache`、`ResponseCacheEntry`、`ResponseCacheKey` 與 `ResponseCacheKeyFactory`，且 package root 與 `async_model_gateway.response_cache.ports` 都不 re-export `ResponseCacheStore`；唯一允許的 public owner path 是 `async_model_gateway.response_cache.ports.store`。
- behavior validation 必須證明 `ResponseCache.get(...)` / `set(...)` 只做 async store delegation、保留 literal key 與 entry surface、將 store miss 表達為 `None`，並讓 store failures 原樣傳播。
- async-baseline validation 必須證明 implementation 沒有偷偷加入 timeout、retry、sync mirror、background task 或 broader concurrency behavior。
- entry validation 必須證明 `ResponseCacheEntry` 只有 `response: str`，沒有 metadata、timestamps 或其他 fields。
- regression validation 必須保留 `tests/response_cache/test_key.py` 與 `tests/response_cache/test_key_factory.py` 的既有 keyed boundary guarantees。
- 不得有任何 artifact path、implementation step 或驗證要求引入 concrete backend、TTL、eviction、serialization、metrics、tracing 或 orchestrator wiring。

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

- No release workflow required.
- merge 後停止；不要在此 topic 下新增 version bump、release notes、tags 或 stable-library publication work。

## Open Questions / Unresolved Items

- None.
