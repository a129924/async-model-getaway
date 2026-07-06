# response-cache-operational-minimal-boundary Requirements Baseline

## Freeze Status

- Status: `frozen`
- Topic: `response-cache-operational-minimal-boundary`
- Intended downstream artifact: `analysis/response-cache-operational-minimal-boundary/technical-spec.md`
- Alignment source: `spec-and-plan-finalization` 階段中已同意的 implementation contract

## Business Outcome

- repository 必須新增一個 repo-visible、最小且 operational 的 `ResponseCache` boundary，讓既有 `ResponseCacheKey` 可以被實際的 cache owner 消費，但不把 topic 擴張成 backend、TTL 或 orchestrator work。
- implementer 與 reviewer 必須能在不重開 broader response-cache architecture 的前提下，落地 `ResponseCache`、`ResponseCacheEntry` 與 `ResponseCacheStore` 的最小 Python contract。

## Actors

- Repository maintainer：需要一個 bounded operational cache contract，讓 keyed boundary 可以被最小 runtime owner 消費，而不再停留在 draft-only topic。
- Implementer：需要精確的 source、tests、docs 與 workflow artifact paths，以及已凍結的 async 與 package-surface 決策。
- Reviewer：需要可量測的 acceptance signals，證明此 topic 只新增最小 operational boundary，沒有偷帶 backend、policy 或 metadata 擴張。

## In-scope Requirements

1. repository 必須新增 `ResponseCache` 作為最小 operational owner，並讓它依賴既有 `ResponseCacheKey`，而不是自行重新計算 cache identity。
   Acceptance signal：所有 creator-owned artifacts 都明確寫出 `ResponseCache` 消費 `ResponseCacheKey`，且不重新打開 payload-hash 或 feature-hash authority。
2. `ResponseCache` public API 必須凍結為：
   - `ResponseCache(store: ResponseCacheStore)`
   - `async def get(self, *, key: ResponseCacheKey) -> ResponseCacheEntry | None`
   - `async def set(self, *, key: ResponseCacheKey, entry: ResponseCacheEntry) -> None`
   Acceptance signal：technical spec、topic plan 與 behavior spec 都只描述這三個 public elements，不得擴張額外 public methods。
3. `ResponseCacheEntry` 必須凍結為單欄位 value type：`response: str`。
   Acceptance signal：creator-owned artifacts、planned tests 與 docs 都不得引入 metadata、TTL、timestamps 或 provider details。
4. `ResponseCacheStore` 必須維持 submodule-public，位於 `response_cache.ports.store`，且 package root 不得 re-export 它。
   Acceptance signal：plan 與 spec 必須同時鎖定 root export policy 與 submodule-public policy。
5. package root 必須 re-export `ResponseCache`、`ResponseCacheEntry`、既有 `ResponseCacheKey` 與既有 `ResponseCacheKeyFactory`。
   Acceptance signal：planned package-surface coverage 必須同時驗證新增 re-exports 與既有 keyed re-exports 沒有退化。
6. 此 topic 必須以 repo-visible planning evidence 凍結 async baseline，並依真實 trigger evidence 將 async-planning status 明寫為 `triggered`；不得把 async applicability 留給 implementer 猜測。
   Acceptance signal：creator-owned artifacts 都明確記錄新的 public async `ResponseCache.get(...)` / `set(...)` 與 async `ResponseCacheStore.get(...)` / `set(...)` 是 trigger evidence，並凍結 boundary、resource ownership、direct-await concurrency、failure propagation，以及不引入 timeout / retry / sync mirror 的限制。
7. implementation scope 必須限於指定 source、tests、docs 與 topic workflow artifacts，並且保留與驗證既有 keyed tests。
   Acceptance signal：topic plan 的 artifact table 必須列出精確路徑，validation commands 必須包含新的 operational tests 與既有 keyed regression tests。
8. 此 topic 不得引入 concrete store implementation、backend adapter、serialization、TTL、eviction、metrics、tracing、orchestrator wiring 或 response-generation flow。
   Acceptance signal：任何 creator-owned artifact 都不得把上述項目列為 implementation step、behavior contract 或 acceptance signal。
9. topic 必須為下一個 workflow stage 產出完整的 creator-owned artifact set：`requirements.md`、`technical-spec.md`、`*.plan.md`、`*.spec.md`、`*.step.md`。
   Acceptance signal：每個命名 artifact 都存在於 topic plan 宣告的精確路徑，且 topic 狀態停在 `review-ready`。

## Non-goals

- 此 topic 不會新增 concrete `ResponseCacheStore` backend。
- 此 topic 不會加入 Redis、database、file、memory cache backend selection。
- 此 topic 不會加入 TTL、eviction、invalidation 或 freshness policy。
- 此 topic 不會重新設計 `ResponseCacheKey` 或 `ResponseCacheKeyFactory`。
- 此 topic 不會把 `ResponseCacheEntry` 擴張為 metadata-bearing payload。
- 此 topic 不會將 `ResponseCache` 接到 `orchestrator`、provider 或 response-generation flow。
- 此 topic 不會宣告 stable-library、release 或 versioning work。

## Assumptions

- 既有 keyed response-cache boundary 已存在，且 `ResponseCacheKey` 與 `ResponseCacheKeyFactory` 行為在此 topic 中視為既有依賴，而不是重新設計對象。
- 最小 operational boundary 可以只透過 abstract `ResponseCacheStore` port 成立，不需要 concrete backend 才能凍結 owner responsibility。
- `ResponseCacheStore` 的 async contract 會與 `ResponseCache.get(...)` / `set(...)` 的 key 與 entry surface 對齊。

## Contradictions Surfaced And Resolved

- 潛在矛盾：topic 名稱包含 `operational`，但 frozen scope 又禁止 concrete store/backend。
  Resolution：此 topic 的 `operational` 指的是 `ResponseCache` 真的成為 runtime owner 並消費 `ResponseCacheKey` 與 `ResponseCacheEntry`；concrete persistence 仍延後到別的 topic。
- 潛在矛盾：package root 要新增 `ResponseCache` 與 `ResponseCacheEntry`，但 `ResponseCacheStore` 又不得 root re-export。
  Resolution：對外 root surface 只公開 runtime owner 與 value types；store port 維持 submodule-public，避免把 backend abstraction 升成 package-root promise。
- 潛在矛盾：topic 鎖 async-only baseline，但又不允許 concurrency/policy 擴張。
  Resolution：最小 async baseline 仍需以 repo-visible trigger evidence 明寫，但只凍結 `await`-driven `get` / `set` boundary、store lifecycle ownership 與 failure propagation；不延伸到 fan-out、timeouts、retries 或 cancellation orchestration features。

## Extreme-boundary Checks

- 沒有 concrete store：topic 仍必須可完成，因為 `ResponseCacheStore` 只是 abstract port，最小 owner contract 仍可被規劃與驗證。
- caller 只需要 cache hit/miss boundary：topic 仍必須要求 `ResponseCacheEntry` 存在，避免 `ResponseCache` 直接退化成裸 `str` owner。
- implementer 想把 store port root re-export：屬於 scope violation，因為 package-root promise 會不必要地變寬。
- implementer 想在 `ResponseCacheEntry` 補 metadata：屬於 out of scope，必須另開 topic。
- reviewer 想以 human gate 或 implementation completion 取代 plan review：不可接受，因為 workflow contract 要求明確 repo-visible gate paths。

## Acceptance Signals

- `analysis/response-cache-operational-minimal-boundary/technical-spec.md` 會把每個 in-scope requirement 映射到 bounded technical work 與精確 artifact paths。
- `plan/response-cache-operational-minimal-boundary/response-cache-operational-minimal-boundary.plan.md` 會列出 canonical workflow transitions、exact artifact paths 與 review-support gate paths。
- `plan/response-cache-operational-minimal-boundary/response-cache-operational-minimal-boundary.plan.md` 會明寫 async-planning status 與其 trigger evidence，避免後續 reviewer 只能從 `async def` 表面語法推論。
- `plan/response-cache-operational-minimal-boundary/response-cache-operational-minimal-boundary.spec.md` 會凍結 `ResponseCache`、`ResponseCacheEntry` 與 package-surface 的行為契約。
- `plan/response-cache-operational-minimal-boundary/response-cache-operational-minimal-boundary.step.md` 會 mirror implementation steps，且不預填 implementation completion。
- 沒有任何 creator-owned artifact 宣稱 concrete backend、TTL、eviction、serialization、metrics、tracing 或 orchestrator wiring 屬於此 topic。

## Blockers

- 無。
