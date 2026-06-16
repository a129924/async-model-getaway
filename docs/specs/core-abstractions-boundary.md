# core abstractions boundary

## 摘要

這份文件是 core abstractions boundary 的索引入口。

它只負責總覽、共享詞彙、閱讀順序與依賴方向摘要，不承擔各邊界的細節正文。

## 閱讀順序

建議依照以下順序閱讀：

1. [canonical-input-boundary.md](canonical-input-boundary.md)
2. [orchestrator-boundary.md](orchestrator-boundary.md)
3. [model-side-boundary.md](model-side-boundary.md)
4. [response-cache-boundary.md](response-cache-boundary.md)

## 共享詞彙

這一組 spec 以以下詞彙作為正式共享語彙：

- `model-payload`
- `features`
- `orchestrator`
- `ModelRegistry`
- `ModelPool`
- `ModelGateway`
- `ResponseCache`
- `runtime-model`
- `payload-hash`

`ModelGateway` 是正式名詞；不使用 `ModelGetaway`。

## 依賴方向摘要

高層依賴方向固定為：

1. `canonical input boundary` 只定義 `model-payload` 與 `features`
2. `orchestrator` 協調高層流程，但不擁有 hashing、lifecycle 或 cache identity authority
3. `ModelRegistry` 擁有 `payload-hash` 與 freshness authority
4. `ModelPool` 擁有 local model runtime and lifecycle
5. `ModelGateway` 擁有 remote model side boundary
6. `ResponseCache` 依賴 `payload-hash + features`

## Deferred Items

這一組文件明確不處理：

- Python class / protocol 最終型別
- `src` module layout
- `pydantic`
- `sqlalchemy`
- cache key algorithm 細節
- provider adapter contract
- runtime flow implementation
