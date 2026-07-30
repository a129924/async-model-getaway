# response cache boundary

## 摘要

`ResponseCache` 是 response reuse boundary。

它的角色是讓相同條件下的 response 可以被重用。repo 目前已落地既有 keyed boundary、
最小 operational boundary，以及 internal process-local storage 的有限 freshness slice；
它仍不處理 persistence backend、schema 或 broader cache architecture。

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
- `ResponseCacheKeyFactory` 顯式接收 `model_payload_hash`
- payload hashing 仍由既有 `ModelPayloadHasher` 擁有，但發生在 factory 外部
- feature hashing 仍由 `response_cache.ports.FeatureHasher` 擁有
- factory 只負責協調上述 inputs 並回傳 `ResponseCacheKey`

## Operational Boundary

目前新增的最小 operational boundary 只包含：

- package root re-export `ResponseCache`、`ResponseCacheEntry`、`ResponseCacheKey` 與 `ResponseCacheKeyFactory`
- `ResponseCacheEntry` 只保留 `response: str`
- `ResponseCache` 只透過 async `get(...)` / `set(...)` 消費既有 `ResponseCacheKey`
- `ResponseCacheStore` 只維持在 `response_cache.ports.store` 的 submodule-public path
- internal `InMemoryResponseCacheStore` 接受 developer-injected 的正 TTL freshness policy，
  在成功寫入記錄 aware-UTC 時間，讀取不續期，並將到期既有 record 視為 `None` miss

在這個 boundary 中：

- `ResponseCache` 只持有 caller 提供的 `ResponseCacheStore`
- `ResponseCache.get(...)` / `set(...)` 只做 direct await delegation
- store miss 以 `None` 表達
- store failures 原樣向外傳播
- `ResponseCache` 不建立、關閉或重置 store resources
- internal policy 與 concrete store 不會 re-export 至 package root 或 `ports`

## Owner Responsibility

`ResponseCache` 負責：

- 定義 response reuse 的責任歸屬
- 對 `orchestrator` 提供 hit / miss 概念邊界
- 與 canonical input 及 model side identity 維持清楚依賴方向
- 透過既有 `ResponseCacheKey` 與最小 `ResponseCacheStore` port 協調 operational read/write owner

未來任何 operational `ResponseCache` surface 都應消費 `ResponseCacheKey`，而不是在自身內部重新計算 payload 或 feature hashes。

## 明確不做

這一輪不定義：

- public concrete-store 或 policy API
- settings/env TTL surface、TTL renewal、capacity、admission、eviction、invalidation 或 deletion
- persistence schema
- database / Redis / `SQLAlchemy`
- provider adapter

## Boundary Position

`ResponseCache` 不是 `ModelRegistry` 的附屬，也不是 `ModelPool` 的附屬。

它是由 `orchestrator` 消費、並依賴 `ResponseCacheKey` 的獨立業務邊界。
