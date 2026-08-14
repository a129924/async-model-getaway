# core abstractions boundary

## 摘要

這份文件是 core abstractions boundary 的索引入口。

它只負責總覽、共享詞彙、閱讀順序與依賴方向摘要，不承擔各邊界的細節正文。

## 閱讀順序

建議依照以下順序閱讀：

1. [canonical-input-boundary.md](canonical-input-boundary.md)
2. [prediction-workflow-boundary.md](prediction-workflow-boundary.md)
3. [model-side-boundary.md](model-side-boundary.md)
4. [orchestrator-boundary.md](orchestrator-boundary.md)
5. [response-cache-boundary.md](response-cache-boundary.md)

## 共享詞彙

這一組 spec 以以下詞彙作為正式共享語彙：

- `model_name`
- `model_source_kind`
- `model-payload`
- `model_artifact`
- `features`
- `prediction_input`
- `orchestrator`
- `PredictionOrchestrator`
- `Predictor`
- `ResultCodec`
- `ModelRegistry`
- `ModelPool`
- `ModelGateway`
- `ResponseCache`
- `runtime-model`
- `payload-hash`
- `model_identity_hash`
- `prediction_input_hash`

`ModelGateway` 是正式名詞；不使用 `ModelGetaway`。

## 依賴方向摘要

高層依賴方向固定為：

1. target `canonical input boundary` 定義 `model_name`、`model_source_kind`、`model-payload`、`features` 與 `prediction_input`
2. `PredictionOrchestrator` 在首次 await 前建立 prediction-input snapshot，並協調下游 authority
3. `ModelRegistry` 擁有 `payload-hash`、完整 model identity context、freshness authority，以及 target `model_identity_hash`
4. `Predictor` 投影 input identity 與 application result；專責 hashers、namespace deriver、key deriver 在 cache 外產生 target key
5. internal local composition 在 acquisition 前依 explicit `LoaderFamily` 解析配對的 Loader、Executor 與 concurrency policy
6. internal `ModelPool` 消費 composition 注入的 Loader，載入 raw provider runtime 並建立 concrete `LoadedRuntimeModel`
7. `ModelGateway` 擁有 remote `runtime-model` provider / access boundary
8. internal Executor 消費同一個 pre-resolved binding 的 `LoadedRuntimeModel`，在 gate 後處理單次 invocation lifecycle
9. `ResultCodec` 在 application layer 做 application result `↔` cache `str`；`ResponseCache` 只處理 cache `str` reuse
10. local runtime composition、pool、loader、executor 與 loaded model 均沒有 public package entrypoint

在目前階段：

- `model_source_kind` 只鎖 `local | remote`
- local runtime taxonomy 留在 `ModelPool` 內部
- local read contract 由 `model_artifact` 承擔，且目前已由
  `async_model_gateway.model_runtime.model_artifact` 提供最小 public shared read contract
- `async_model_gateway.model_runtime.model_artifact` 只公開 `ModelArtifact` 與 `LoaderFamily`
- `ModelArtifact` 只承載 `loader_family`、`artifact_path`、`loader_options`
- `LoaderFamily` starter vocabulary 只允許 `pickle`、`torch`、`onnx`
- closed binding resolver 對這三個 family 使用 explicit dispatch；ONNX loader/executor 在 resolver 內預先配對，PICKLE 與 TORCH fail closed
- 已落地的 local flow 是 `ModelArtifact → resolve binding → injected Loader → ModelPool → LoadedRuntimeModel → paired Executor → result`；同一 binding 必須通過 acquisition 與 execution，沒有 public local entrypoint
- `LoadedRuntimeModel` 是 concrete generic internal resource，保存 runtime、Semaphore 與 aware-UTC timestamps；它沒有 loader family、provider handoff、execute 或 lifecycle API
- Executor 在取得 gate 後更新使用時間、direct-await 單次 invocation，並原樣傳播一般例外與 cancellation；它不做 late family/type/provider dispatch
- 除 ONNX session acquisition 外的 artifact I/O、真實 provider invocation、provider framework、完整 orchestration/remote execution、lifecycle、timeout 與 retry 仍 deferred
- `async_model_gateway.model_registry.stores.InMemoryRegistryStore` 已作為
  process-local concrete store 提供，但不改變 `model_registry` root package
  的 re-export boundary
- `runtime-model` 維持統一 consumption surface
- provider acquisition 與 invocation semantics 維持分離 boundary
- capability 差異先收斂在 `features`

## Deferred Items

這一組文件明確不處理：

- provider-specific runtime implementation、invocation 與 framework（ONNX session acquisition 除外）
- `src` module layout
- `pydantic`
- `sqlalchemy`
- cache key algorithm 細節
- provider adapter contract
- 完整 runtime flow implementation
