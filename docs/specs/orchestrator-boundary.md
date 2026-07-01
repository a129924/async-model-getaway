# orchestrator boundary

## 摘要

`orchestrator` 是這個系統的高層協調者。

它負責圍繞 canonical input 協調 response generation，但不擁有 hashing、model lifecycle、execution policy 或 response cache identity 的 authority。

## Owner Responsibility

`orchestrator` 主要負責：

- 接收完整 canonical input：
  - `model_name`
  - `model_source_kind`
  - `model-payload`
  - `features`
- 協調高層決策順序
- 根據下游 authority 的結果推進 response generation
- 委派 `ModelExecution` 發生 model invocation，而不是自己直接 execute model

## 依賴的 Authority

`orchestrator` 依賴：

- `ModelRegistry` 提供 `payload-hash` 與 freshness result
- `ModelPool` 提供 local `runtime-model` provider / lifecycle boundary
- `ModelGateway` 提供 remote `runtime-model` provider / access boundary
- `ModelExecution` 提供 `runtime-model` invocation boundary
- `ResponseCache` 提供 response reuse boundary

## 明確不擁有的責任

`orchestrator` 不負責：

- 產生 `payload-hash`
- 擁有 registry freshness authority
- 擁有 local model runtime lifecycle
- 擁有 remote model side boundary
- 直接 execute model
- 擁有 execution policy 或 invocation semantics
- 擁有 cache identity authority
- 擁有 persistence schema
- 校正 `model_name`
- 擴張 `model_source_kind`
- 把 `features` 解讀成 provider contract 或 execution contract
- 把能力差異外露成 `predict()` / `generate()` / `explain()` 等公開 method surface

## Boundary Position

`orchestrator` 是高層 owner，但不是 owner 混合體。

它的價值在於協調各邊界，而不是把所有業務責任集中在自己身上。

在目前階段，`orchestrator` 不負責判斷 `local | remote` 的 authority；分流訊號來自 canonical input 中的 `model_source_kind`。

能力差異目前由 `features` 表達，但 `orchestrator` 不因此承擔 provider-specific capability contract。
實際 model invocation 必須委派給 `ModelExecution`，而不是讓 `orchestrator`
自己成為 execution owner。
