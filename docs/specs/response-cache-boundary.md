# response cache boundary

## 摘要

`ResponseCache` 是 response reuse boundary。

它的角色是讓相同條件下的 response 可以被重用，但目前只落地最小 keyed boundary，不處理實際 backend、schema 或 persistence implementation。

## Identity Dependency

`ResponseCache` 在這一輪固定依賴：

- `ResponseCacheKey.namespace`
- `ResponseCacheKey.model_payload_hash`
- `ResponseCacheKey.feature_hash`

也就是說，目前的 cache identity 會先被準備成 `ResponseCacheKey`，而不是讓未來 cache runtime owner 直接自行組合 `payload-hash + features`。

`features` 參與 response reuse，但不參與 model identity。

`model_name` 與 `model_source_kind` 不直接成為 cache identity owner。

`features` 在這裡被視為 bounded capability vocabulary 的一部分，而不是任意 producer label。

在這個最小 boundary 中：

- `ResponseCacheKeyFactory` 顯式接收 `namespace`
- payload hashing 仍由既有 `ModelPayloadHasher` 擁有
- feature hashing 仍由 `response_cache.ports.FeatureHasher` 擁有
- factory 只負責協調上述 inputs 並回傳 `ResponseCacheKey`

## Owner Responsibility

`ResponseCache` 負責：

- 定義 response reuse 的責任歸屬
- 對 `orchestrator` 提供 hit / miss 概念邊界
- 與 canonical input 及 model side identity 維持清楚依賴方向

未來任何 operational `ResponseCache` surface 都應消費 `ResponseCacheKey`，而不是在自身內部重新計算 payload 或 feature hashes。

## 明確不做

這一輪不定義：

- operational cache storage API
- TTL / eviction implementation
- persistence schema
- database / Redis / `SQLAlchemy`
- provider adapter

## Boundary Position

`ResponseCache` 不是 `ModelRegistry` 的附屬，也不是 `ModelPool` 的附屬。

它是由 `orchestrator` 消費、並依賴 `ResponseCacheKey` 的獨立業務邊界。
