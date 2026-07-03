# response-cache-keyed-minimal-boundary Requirements Baseline

## Freeze Status

- Status: `frozen`
- Topic: `response-cache-keyed-minimal-boundary`
- Intended downstream artifact: `analysis/response-cache-keyed-minimal-boundary/technical-spec.md`
- Alignment source: `spec-and-plan-finalization` 階段中明確提供的 topic contract

## Business Outcome

- repository 必須新增一個 repo-visible、最小且 keyed 的 response-cache boundary contract，將 cache key 建構責任與未來 `ResponseCache` 的 storage 行為分離。
- implementer 與 reviewer 必須能在不重開 broader cache architecture、backend 或 orchestrator scope 的前提下，執行下一個 Python workflow。

## Actors

- Repository maintainer：需要一個 bounded topic contract，使工作能通過 plan review 並在後續 implementation 中不必重新決定 cache-key authority。
- Implementer：需要最小 keyed boundary 的精確 source、test 與文件路徑，以及已凍結的決策。
- Reviewer：需要可量測的 acceptance signals，證明此 topic 沒有超出最小 keyed scope。

## In-scope Requirements

1. repository 必須定義一個最小 response-cache key contract，使未來任何 `ResponseCache` runtime surface 都消費已建好的 `ResponseCacheKey`，而不是自行計算 cache hash。
   Acceptance signal：planning artifacts 與 downstream technical spec 都必須明確寫出 hash authority 位於 `ResponseCache` 之外。
2. `ResponseCacheKey` 必須固定為三個欄位：`namespace: str`、`model_payload_hash: str`、`feature_hash: str`。
   Acceptance signal：technical spec 與 topic plan 都只描述這三個欄位，不得出現額外 key material。
3. `ResponseCacheKeyFactory` 必須在建構時持有 `FeatureHasher`，並暴露一個 `build(...)` 路徑，明確接收 `namespace`、`model_payload_hash: str` 與 `features: Mapping[str, str]`。
   Acceptance signal：technical spec 與 topic plan 都必須凍結這些輸入，並明確寫出 payload hashing 發生在 factory 外部的 upstream owner。
4. 此 topic 的 feature input 必須凍結為 `Mapping[str, str]`。
   Acceptance signal：所有 creator-owned artifacts 都必須使用這個精確型別，不得擴張成任意 mappings、settings objects 或 provider labels。
5. 此最小 keyed boundary 必須與 cache backend、persistence schema、TTL、eviction 與 orchestrator wiring 決策保持分離。
   Acceptance signal：任何 in-scope artifact path 或 implementation step 都不得包含 store、backend、schema、TTL、eviction 或 orchestrator 檔案。
6. topic 必須為下一個 workflow stage 產出完整的 creator-owned artifact set：`requirements.md`、`technical-spec.md`、`*.plan.md`、`*.spec.md`、`*.step.md`。
   Acceptance signal：每個命名 artifact 都存在於 topic plan 宣告的精確路徑。

## Non-goals

- 此 topic 不會把 `feature-hash` authority 擴張成 broader keyed boundary topic。
- 此 topic 不會引入 cache store、backend adapter、schema、TTL policy 或 eviction policy。
- 此 topic 不會將 `ResponseCache` 接到 `orchestrator` 或任何 runtime execution flow。
- 此 topic 不會重新定義 `ModelPayloadHasher` 的 ownership 或 hashing semantics。
- 此 topic 不會擴張成 stable-library 或 release-facing work。

## Assumptions

- topic contract 已由 maintainer 凍結，在 technical translation 前不需要再做 business negotiation。
- 既有 `ModelPayloadHasher` 行為仍是此 topic 中 payload-hash 的權威來源。
- 未來可以另開 topic 引入 operational `ResponseCache` storage behavior，但那份工作必須遵守這裡凍結的 keyed boundary。

## Contradictions Surfaced And Resolved

- 潛在矛盾：topic 名稱提到 `ResponseCache`，但同一份 contract 又禁止 store/backend/schema work。
  Resolution：此 topic 只凍結 keyed boundary authority 與準備 `ResponseCacheKey` 所需的最小 source surfaces；operational cache persistence 明確延後。
- 潛在矛盾：`features` 會影響 cache reuse，但 topic 又禁止 broader feature-hash authority work。
  Resolution：`features` 凍結為 `Mapping[str, str]`，且只透過 `ResponseCacheKeyFactory` 持有的 bounded `FeatureHasher` 進行 hashing。

## Extreme-boundary Checks

- 沒有 backend：topic 仍必須可完成，因為它只凍結 keyed boundary artifacts；backend work 不在範圍內。
- 錯誤 actor 想擴張 `features`：任何把 `Mapping[str, str]` 改成更寬型別的要求都屬於 out of scope，必須另開新 topic。
- 只有部分完成、缺少 `ResponseCacheKeyFactory`：不可接受，因為最小 boundary 會留下 hash-authority routing 不明確的問題。
- 最低量情境：單一 cache-key build 也必須遵守相同的顯式輸入 contract。
- 峰值量情境：此 topic 不做 throughput 承諾，因為沒有引入 runtime backend 或 orchestration path。
- workflow 中斷：若後續 implementation 需要 store 或 orchestrator 檔案，工作必須回到 `spec-and-plan-finalization`，不能在此 topic 內直接擴 scope。

## Acceptance Signals

- `analysis/response-cache-keyed-minimal-boundary/technical-spec.md` 將每一個 in-scope requirement 映射到 bounded technical work。
- `plan/response-cache-keyed-minimal-boundary/response-cache-keyed-minimal-boundary.plan.md` 列出精確 artifact paths 與 canonical workflow transitions。
- `plan/response-cache-keyed-minimal-boundary/response-cache-keyed-minimal-boundary.spec.md` 與 `.step.md` 作為 Python implementation workflow 的 companion artifacts 存在。
- 沒有任何 creator-owned artifact 宣稱 backend、TTL、eviction、schema 或 orchestrator work 屬於此 topic。

## Blockers

- 無。
