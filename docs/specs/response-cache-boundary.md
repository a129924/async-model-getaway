# response cache boundary

## 摘要

`ResponseCache` 是 response reuse boundary。

它的角色是讓相同條件下的 response 可以被重用，但目前不處理實際 backend、schema 或 persistence implementation。

## Identity Dependency

`ResponseCache` 在這一輪固定依賴：

- `payload-hash`
- `features`

也就是說，目前的 cache identity 概念固定為 `payload-hash + features`。

`features` 參與 response reuse，但不參與 model identity。

`model_name` 與 `model_source_kind` 不直接成為 cache identity owner。

`features` 在這裡被視為 bounded capability vocabulary 的一部分，而不是任意 producer label。

## Owner Responsibility

`ResponseCache` 負責：

- 定義 response reuse 的責任歸屬
- 對 `orchestrator` 提供 hit / miss 概念邊界
- 與 canonical input 及 model side identity 維持清楚依賴方向

## 明確不做

這一輪不定義：

- cache key algorithm 細節
- TTL / eviction implementation
- persistence schema
- database / Redis / `SQLAlchemy`
- provider adapter

## Boundary Position

`ResponseCache` 不是 `ModelRegistry` 的附屬，也不是 `ModelPool` 的附屬。

它是由 `orchestrator` 消費、並依賴 `payload-hash + features` 的獨立業務邊界。
