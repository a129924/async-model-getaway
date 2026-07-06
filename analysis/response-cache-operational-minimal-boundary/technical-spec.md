# response-cache-operational-minimal-boundary Technical Specification

## Translation Status

- Source baseline: `analysis/response-cache-operational-minimal-boundary/requirements.md`
- Translation posture: pessimistic implementer
- Result: `ready-for-plan-authoring`

## Technical Summary

- 此 topic 最小且誠實的落地方式，是在既有 keyed `response_cache` package 上新增 operational owner `ResponseCache`、單欄位 value type `ResponseCacheEntry`，以及只允許經由 `async_model_gateway.response_cache.ports.store` 直接匯入的 submodule-public `ResponseCacheStore` port。
- `ResponseCache` 只負責透過既有 `ResponseCacheKey` 對 store 做 async `get` / `set` 委派；它不重新計算 hashes，也不擁有 backend、TTL、serialization 或 orchestrator integration semantics。
- package root 應擴張為 re-export `ResponseCache`、`ResponseCacheEntry`、既有 `ResponseCacheKey` 與既有 `ResponseCacheKeyFactory`，但不得 root re-export `ResponseCacheStore`。
- `ResponseCacheEntry` 的 contract 嚴格限於 `response: str`；任何 metadata、timestamps 或 provider annotations 都延後處理。

## Requirement-to-Technical Mapping

| Requirement | Technical realization | Planned artifacts | Dependency notes |
| --- | --- | --- | --- |
| `ResponseCache` 必須成為最小 operational owner，並消費既有 `ResponseCacheKey` | 新增 `cache.py`，實作只做 async store delegation 的 thin owner；既有 key/factory 維持為 upstream identity dependency | `src/async_model_gateway/response_cache/cache.py`, `tests/response_cache/test_cache.py`, `plan/response-cache-operational-minimal-boundary/response-cache-operational-minimal-boundary.spec.md` | 依賴既有 keyed boundary；不依賴 concrete backend |
| `ResponseCache` API 必須固定為 constructor + async `get` / `set` | `ResponseCache` constructor 持有 `ResponseCacheStore`；`get` / `set` 僅暴露 `ResponseCacheKey` 與 `ResponseCacheEntry` | `src/async_model_gateway/response_cache/cache.py`, `src/async_model_gateway/response_cache/ports/store.py`, `tests/response_cache/test_cache.py` | store port methods 需與 owner API 對齊 |
| `ResponseCacheEntry` 必須只有 `response: str` | 新增 frozen value type module `entry.py`，不加入 metadata | `src/async_model_gateway/response_cache/entry.py`, `tests/response_cache/test_entry.py`, `plan/response-cache-operational-minimal-boundary/response-cache-operational-minimal-boundary.spec.md` | 不允許未經新 topic 授權的欄位擴張 |
| `ResponseCacheStore` 必須維持 submodule-public | 在 `ports/store.py` 定義 abstract async store contract，並明確禁止 `response_cache/ports/__init__.py` 與 package root re-export 該型別 | `src/async_model_gateway/response_cache/ports/store.py`, `src/async_model_gateway/response_cache/ports/__init__.py`, `tests/response_cache/test_response_cache_package_surface.py` | 唯一允許的 public owner path 是 `async_model_gateway.response_cache.ports.store` |
| package root 必須 re-export `ResponseCache`、`ResponseCacheEntry`、既有 keyed surfaces | 更新既有 `response_cache/__init__.py`，擴張 root exports 但不破壞 keyed boundary compatibility | `src/async_model_gateway/response_cache/__init__.py`, `tests/response_cache/test_response_cache_package_surface.py` | 既有 `test_key.py` 與 `test_key_factory.py` 必須保持通過 |
| async-only baseline 必須被凍結 | plan 與 tests 明確把 operational boundary 限於 async `get` / `set` 的 direct await delegation | `plan/.../*.plan.md`, `plan/.../*.spec.md`, `tests/response_cache/test_cache.py` | 不新增 sync wrapper、timeout 或 fan-out policy |
| scope 只限指定 docs/source/tests/artifacts | topic plan 列出精確 path contract；technical spec 不宣告其他 source area | `plan/response-cache-operational-minimal-boundary/response-cache-operational-minimal-boundary.plan.md` | path drift 必須回到 `spec-and-plan-finalization` |
| concrete backend、policy 與 wiring 維持 out of scope | docs 只描述最小 operational boundary，不宣稱完整 runtime cache implementation | `docs/architecture.md`, `docs/specs/response-cache-boundary.md` | 若需要 backend details，必須另開 topic |

## Proposed Source And Test Surface

### Source

- `src/async_model_gateway/response_cache/__init__.py`
- `src/async_model_gateway/response_cache/cache.py`
- `src/async_model_gateway/response_cache/entry.py`
- `src/async_model_gateway/response_cache/ports/__init__.py`
- `src/async_model_gateway/response_cache/ports/store.py`

### Existing source surfaces to preserve

- `src/async_model_gateway/response_cache/key.py`
- `src/async_model_gateway/response_cache/key_factory.py`
- `src/async_model_gateway/response_cache/ports/feature_hasher.py`

### Tests

- `tests/response_cache/test_response_cache_package_surface.py`
- `tests/response_cache/test_cache.py`
- `tests/response_cache/test_entry.py`
- `tests/response_cache/test_key.py`
- `tests/response_cache/test_key_factory.py`

### Docs

- `docs/architecture.md`
- `docs/specs/response-cache-boundary.md`

## Technical Decisions

- Async-planning status: `triggered` — cite trigger evidence: 此 topic 新增 public async `ResponseCache.get(...)` / `set(...)` 與 async `ResponseCacheStore.get(...)` / `set(...)` boundary，必須在 implementation 前凍結 async boundary、resource ownership、failure propagation 與不引入 timeout / retry / sync mirror 的限制。
- `ResponseCache` 應是 thin async owner：它只持有 `ResponseCacheStore`，並將 `ResponseCacheKey` / `ResponseCacheEntry` 原樣傳遞給 store contract。
- `ResponseCacheEntry` 應是小型、不可變、完整型別化的 value surface，且只有 `response: str` 一個欄位。
- `ResponseCacheStore` 應凍結為最小 abstract collaborator，提供與 owner API 對齊的 async `get` / `set` contract；其抽象表達方式可由實作者在 `ports/store.py` 內選擇，但不得改變 public method surface，且唯一允許的 public owner path 是 `async_model_gateway.response_cache.ports.store`。
- package root 只應 re-export runtime owner 與 value/key surfaces：`ResponseCache`、`ResponseCacheEntry`、`ResponseCacheKey`、`ResponseCacheKeyFactory`。`ResponseCacheStore` 不得由 package root 或 `async_model_gateway.response_cache.ports` re-export，並維持僅能從 `async_model_gateway.response_cache.ports.store` 直接匯入。
- error handling 應維持 fail-closed 且不做翻譯：store failures 原樣傳播；`get` 回傳 `None` 只代表 store miss，不代表 swallowed exception。
- async baseline 已觸發，但 concurrency model 仍鎖為 direct await delegation，不加入 background ownership、batching、retry、timeout 或 sync compatibility orchestration。

### Async planning baseline

- Async boundary decision：只有 `ResponseCache` 與 `ResponseCacheStore` 的 public `get` / `set` contract 是 async；`ResponseCacheEntry`、既有 `ResponseCacheKey` 與既有 `ResponseCacheKeyFactory` 仍維持同步 value/helper surfaces。
- Resource lifecycle decision：`ResponseCache` 只持有呼叫端提供的 `ResponseCacheStore` reference，不建立、共享、關閉或重置 store-backed resources。
- Concurrency model：`ResponseCache.get(...)` 與 `set(...)` 都是單次 direct await delegation；不在此 topic 中加入 fan-out、batching、worker ownership、backpressure 或 queue semantics。
- Failure model：store-raised failures 原樣向外傳播；`None` 只表達 cache miss，不能被視為 error swallowing 或 fallback success。
- Cancellation / timeout policy：此 topic 不新增 timeout、retry 或 cancellation wrapper；任何底層 awaitable cancellation semantics 維持由 store 實作者與 caller runtime 擁有。
- Validation plan：planned tests 與 plan validation 必須證明 async owner/store signatures、direct delegation、miss-as-`None` semantics、store failure propagation，以及 `ResponseCacheStore` 不會從 package root 或 `async_model_gateway.response_cache.ports` re-export。
- Handoff note：implementer 只能在已宣告的 async boundary 內工作；若 implementation 需要額外 lifecycle ownership、timeout/retry policy 或 sync mirror API，必須回到 `spec-and-plan-finalization`。

## Feasibility And Cost

| Workstream | Complexity | Sequencing | Operational burden |
| --- | --- | --- | --- |
| Operational owner 與 entry/store source surfaces | Medium | 必須排在 RED tests 之後 | Low；不引入 concrete resources |
| Package-surface 與 behavior tests | Medium | implementation 的第一個子階段 | Low；isolated pytest coverage |
| Docs 對齊 | Low | 在 source contracts 凍結後進行 | Low；純 wording 變更 |

## Architecture Compliance Check

- 符合目前架構：`ResponseCache` 仍是由 `orchestrator` 消費的獨立 boundary，並繼續依賴既有 `ResponseCacheKey`。
- 符合 ownership rules：hash authority 不從 `ModelPayloadHasher` 或 `FeatureHasher` 移走；`ResponseCache` 只消費已建好的 key。
- 符合 repo stage：只補最小 operational boundary，不假設 backend、provider 或 orchestration flow 已存在。
- 不需要 stable-library metadata：此 topic 明確是 non-stable-library，且沒有 release timing。

## Conflict Notes And Rollback-to-Alignment Triggers

- workflow conflict：repo-level `plan/topic-plan-contract.md` 要求 canonical topic-plan section order，而 `python-plan-authoring` 則要求另一套 13-section `*.plan.md` 結構。
  Handling：此 topic 採最保守的 repo-compliant shape，讓 `response-cache-operational-minimal-boundary.plan.md` 優先遵守 canonical topic-plan contract，並把 Python 行為契約與 step tracking 分別落在 `*.spec.md` 與 `*.step.md`。
- 已避開的重大衝突：若把 `ResponseCacheStore` 由 package root 或 `async_model_gateway.response_cache.ports` re-export，package surface 會不必要地承諾 backend abstraction。
  Handling：store port 僅維持為 `async_model_gateway.response_cache.ports.store` 的 submodule-public surface。
- 出現下列任一情況時，必須回退到 alignment：
  - 引入 concrete store/backend/serialization path
  - 擴張 `ResponseCacheEntry` 超出 `response: str`
  - 改動 `ResponseCacheKey` / `ResponseCacheKeyFactory` contract
  - 將 async-only baseline 改成 sync mirror、timeout policy 或 broader concurrency feature
  - 將 human gate 或 review artifact 預填為已通過

## Open Technical Questions

- 無。
