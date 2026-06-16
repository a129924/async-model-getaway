# orchestrator boundary

## 摘要

`orchestrator` 是這個系統的高層協調者。

它負責圍繞 canonical input 協調 response generation，但不擁有 hashing、model lifecycle 或 response cache identity 的 authority。

## Owner Responsibility

`orchestrator` 主要負責：

- 接收 `model-payload` 與 `features`
- 協調高層決策順序
- 根據下游 authority 的結果推進 response generation

## 依賴的 Authority

`orchestrator` 依賴：

- `ModelRegistry` 提供 `payload-hash` 與 freshness result
- `ModelPool` 提供 local `runtime-model`
- `ModelGateway` 提供 remote model side 路徑
- `ResponseCache` 提供 response reuse boundary

## 明確不擁有的責任

`orchestrator` 不負責：

- 產生 `payload-hash`
- 擁有 registry freshness authority
- 擁有 local model runtime lifecycle
- 擁有 remote model side boundary
- 擁有 cache identity authority
- 擁有 persistence schema

## Boundary Position

`orchestrator` 是高層 owner，但不是 owner 混合體。

它的價值在於協調各邊界，而不是把所有業務責任集中在自己身上。
