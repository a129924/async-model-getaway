# orchestrator boundary

## 摘要

`orchestrator` 是這個系統的高層協調者。

它負責圍繞 canonical input 協調 response generation，但不擁有 hashing、model lifecycle、execution policy 或 response cache identity 的 authority。target
workflow 將這個角色正式稱為 `PredictionOrchestrator`；名稱本身尚未新增 Python surface。

## Owner Responsibility

`orchestrator` 主要負責：

- 接收完整 canonical input：
  - `model_name`
  - `model_source_kind`
  - `model-payload`
  - `features`
  - `prediction_input`
- 在第一次 await 前建立並保有 prediction-input deep immutable snapshot，將同一
  snapshot handoff 給 identity derivation 與 execution
- 協調高層決策順序
- 根據下游 authority 的結果推進 response generation
- 委派 `ModelExecution` 發生 model invocation，而不是自己直接 execute model

## 依賴的 Authority

`orchestrator` 依賴：

- `ModelRegistry` 提供 `payload-hash` 與 freshness result
- target `ModelRegistry` result 提供 `model_identity_hash`
- `Predictor` 提供 input identity projection 與 application-result projection
- `FeatureIdentityHasher`、`PredictionInputHasher`、`CacheNamespaceDeriver` 與
  `CacheKeyDeriver` 在 cache 外完成 target key material
- `ResultCodec` 在 application result 與 cache `str` 間轉換
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
- 自行解讀 `features` 或 `prediction_input` 的語意
- 將 application result、Mapping 或 pandas value 下推到 `ResponseCache`、
  `CacheCodec` 或 `CacheStore`
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

在 target cache hit path，orchestrator 取得 `ResponseCache` 的 `str` value 後，
只委派 `ResultCodec.decode` 形成 application result；decode failure 原樣傳播，
不靜默轉成 miss。miss path 的 application result 經 `ResultCodec.encode` 形成 cache
`str` 後才可 remember；encode failure 同樣原樣傳播且不寫入。
