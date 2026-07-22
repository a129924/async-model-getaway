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
3. `ModelPool` 是 local `runtime-model` 的最小 public acquisition boundary；其 async `acquire(...)` 回傳 `LoadedRuntimeModel`
4. private `LocalModelLoader` 作為 `ModelPool` 內部的 local acquisition sub-boundary，只消費 `model_artifact` 並依 explicit `LoaderFamily` dispatch；ONNX route 在此 lazy 建立 provider session 並建立 loader-local private handle
5. `ModelGateway` 擁有 remote `runtime-model` provider / access boundary
6. `runtime-model` 是 provider boundary 交付給 `ModelExecution` 的 unified consumption surface；目前以 abstract opaque `LoadedRuntimeModel` 表達最小 typed contract
7. `ModelExecution` 擁有 `runtime-model` invocation semantics；它透過 internal handoff 將 provider runtime 交給 injected typed async callable，direct-await 單次 invocation 並回傳 result
8. `ResponseCache` 依賴 `payload-hash + features`
9. `orchestrator` 協調 registry、provider、execution 與 cache boundary，但不直接 execute model

在目前階段：

- `model_source_kind` 只鎖 `local | remote`
- local runtime taxonomy 留在 `ModelPool` 內部
- local read contract 由 `model_artifact` 承擔，且目前已由
  `async_model_gateway.model_runtime.model_artifact` 提供最小 public shared read contract
- `async_model_gateway.model_runtime.model_artifact` 只公開 `ModelArtifact` 與 `LoaderFamily`
- `ModelArtifact` 只承載 `loader_family`、`artifact_path`、`loader_options`
- `LoaderFamily` starter vocabulary 只允許 `pickle`、`torch`、`onnx`
- `LocalModelLoader` 對這三個 family 使用 explicit `match/case`；closed enum 的不可達 fallback 使用 `assert_never(...)`
- 已落地的 local flow 是 `ModelArtifact → LocalModelLoader → provider session → LoadedRuntimeModel → ModelExecution → result`；`ModelPool.acquire(...)` 是保有 private loader 的 public local entrypoint
- `LoadedRuntimeModel` 只公開 `loader_family`，不提供 public `execute(...)` 或 provider getter；provider runtime 留在 loader-local private implementation，並僅以 non-public internal handoff 交給最小 `ModelExecution`
- `async_model_gateway.model_runtime.model_execution` 只公開 generic `ModelExecution`，以 injected typed async callable direct-await 單次 invocation、回傳 result，並原樣傳播一般例外與 cancellation；它不依 `loader_family` 做 provider dispatch
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
