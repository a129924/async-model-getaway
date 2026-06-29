# core abstractions boundary

## 摘要

這份文件是 core abstractions boundary 的索引入口。

它只負責總覽、共享詞彙、閱讀順序與依賴方向摘要，不承擔各邊界的細節正文。

## 閱讀順序

建議依照以下順序閱讀：

1. [canonical-input-boundary.md](canonical-input-boundary.md)
2. [model-side-boundary.md](model-side-boundary.md)
3. [orchestrator-boundary.md](orchestrator-boundary.md)
4. [response-cache-boundary.md](response-cache-boundary.md)

## 共享詞彙

這一組 spec 以以下詞彙作為正式共享語彙：

- `model_name`
- `model_source_kind`
- `model-payload`
- `model_artifact`
- `features`
- `orchestrator`
- `ModelRegistry`
- `ModelPool`
- `ModelGateway`
- `ModelExecution`
- `ResponseCache`
- `runtime-model`
- `payload-hash`

`ModelGateway` 是正式名詞；不使用 `ModelGetaway`。

## 依賴方向摘要

高層依賴方向固定為：

1. `canonical input boundary` 定義 `model_name`、`model_source_kind`、`model-payload`、`features`
2. `ModelRegistry` 擁有 `payload-hash`、identity context 與 freshness authority
3. `ModelPool` 擁有 local `runtime-model` provider / lifecycle
4. `LocalModelLoader` 作為 `ModelPool` 內部的 local acquisition sub-boundary，只消費 `model_artifact`
5. `ModelGateway` 擁有 remote `runtime-model` provider / access boundary
6. `runtime-model` 是 provider boundary 交付給 `ModelExecution` 的 unified consumption surface
7. `ModelExecution` 擁有 `runtime-model` invocation semantics
8. `ResponseCache` 依賴 `payload-hash + features`
9. `orchestrator` 協調 registry、provider、execution 與 cache boundary，但不直接 execute model

在目前階段：

- `model_source_kind` 只鎖 `local | remote`
- local runtime taxonomy 留在 `ModelPool` 內部
- local read contract 由 `model_artifact` 承擔
- `runtime-model` 維持統一 consumption surface
- provider acquisition 與 invocation semantics 維持分離 boundary
- capability 差異先收斂在 `features`

## Deferred Items

這一組文件明確不處理：

- Python class / protocol 最終型別
- `src` module layout
- `pydantic`
- `sqlalchemy`
- cache key algorithm 細節
- provider adapter contract
- runtime flow implementation
