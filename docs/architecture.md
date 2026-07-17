# async-model-gateway 架構說明

## 摘要

這份文件用來記錄專案在 initialization 階段的設計層理解。

它的目的，是把目前已對齊的術語與邊界固定下來，同時避免讓人誤以為 runtime behavior 已經完成實作。

## Canonical Input Boundary

目前的 canonical input boundary 是：

- `model_name`
- `model_source_kind`
- `model-payload`
- `features`

專案目前不定義原始 external request shape。未來任何外部 request，都預期先經過 normalization，再進入核心 orchestration boundary。

在目前階段，`model_source_kind` 只鎖 `local | remote`；local runtime 的多樣性留在 model side 內部消化。對外能力差異則先收斂在 `features`，不先拆成多方法名公開介面。

在 local path，除了 identity context 外，還需要一份獨立的 read contract 供 loader 使用；這條路徑不能把 `model-payload` 當成 loader 猜測依據。

目前 repo 已以 `async_model_gateway.model_runtime.model_artifact` 落地這份最小
shared read contract：`model_runtime` 是 umbrella root，而
`model_artifact` package root 只公開 `ModelArtifact` 與 `LoaderFamily`，其中
`ModelArtifact` 只承載 `loader_family`、`artifact_path` 與 `loader_options`，
而 `LoaderFamily` starter vocabulary 只允許 `pickle`、`torch`、`onnx`。

目前 repo 已落地一個最小的 model-registry boundary：
`async_model_gateway.model_registry.ModelRegistry` 會先以
`model_name + model_source_kind` 做 store lookup，再透過既有的
`async_model_gateway.model_registry.model_payload.ModelPayloadHasher`
產生 `payload-hash`，最後交付受限的 freshness decision。

其中 `ModelPayloadHasher.hash_model_payload(...)` 仍只負責
`model-payload` 的 recursive canonicalization 與穩定 SHA-256 digest
產生；這不代表完整 `orchestrator`、`ResponseCache` 或
`runtime-model` acquisition flow 已經實作完成。

## `orchestrator`

目前 `orchestrator` 的概念角色，是圍繞 canonical input 來協調 response generation。
它負責推進高層順序，但不直接 execute model。

高層預期 flow 如下：

1. Receive `model_name`, `model_source_kind`, `model-payload`, and `features`
2. Derive a payload-oriented identity from `model_name`, `model_source_kind`, and `model-payload`
3. Derive a `ResponseCacheKey` from payload identity and `features`
4. Check response cache
5. Return cached response on hit
6. Acquire a `runtime-model` from `ModelPool` or `ModelGateway` on miss
7. Delegate invocation of that `runtime-model` to `ModelExecution`
8. Persist the generated response into response cache
9. Return the response

這裡描述的是高層概念 flow。除了最小 `ModelRegistry` boundary、`model-payload`
hashing core、最小 keyed `response_cache` boundary，以及狹義的
`ModelExecution` invocation seam 已落地外，其餘 orchestration 與完整 runtime
acquisition/execution flow 仍未在 repository 中落地。

## Responsibility Boundaries

### Gateway Side

目前 gateway side 被理解為負責：

- orchestration-oriented decisions
- response cache participation
- canonical input handling after normalization
- coordination across provider, execution, and cache boundaries

在目前 repo 已落地的最小 cache boundary 中，gateway side 只先準備
`ResponseCacheKey`：它由 literal `namespace`、既有 `ModelPayloadHasher`
產生的 `model_payload_hash`，以及 `FeatureHasher` 產生的 `feature_hash`
組成。repo 現在另外落地最小 operational `ResponseCache` boundary：它只透過
async `ResponseCacheStore` port 消費這個 key 與 `ResponseCacheEntry`，而不是
自行計算 hashes 或擁有 backend/policy semantics。

但 gateway side 不直接擁有 model invocation semantics。

### Model Side

目前 model side 被理解為負責：

- `ModelPool` 作為 local `runtime-model` provider / lifecycle owner
- `ModelGateway` 作為 remote `runtime-model` provider / access boundary
- `ModelExecution` 作為 `runtime-model` invocation semantics owner
- `runtime-model` 作為 provider boundary 與 execution boundary 之間的 unified consumption surface

local 與 remote 被視為 model-source concern，而不是不同的 gateway mode。

在 local path，`ModelPool` 內部會消費獨立的 shared read contract
`async_model_gateway.model_runtime.model_artifact`；這個 boundary 只固定
explicit `LoaderFamily` 與最小 artifact metadata，不承擔 loader runtime、
artifact I/O 或 identity authority。

repo 已落地其中最小的 local acquisition slice：
`async_model_gateway.model_runtime.model_pool.ModelPool` 提供 async
`acquire(...)`，並保有私有 `LocalModelLoader`。loader 只消費 `ModelArtifact`，以
`LoaderFamily.PICKLE`、`LoaderFamily.TORCH`、`LoaderFamily.ONNX` 的 explicit
`match/case` 分支選擇對應 private handler；closed enum 的不可達 fallback 使用
`assert_never(...)`。`async_model_gateway.model_runtime.runtime_model` 已提供 abstract
`LoadedRuntimeModel` consumption contract；它只公開 readonly `loader_family`，並以
non-public `_provider_runtime()` 交給 `ModelExecution` 作 internal handoff。
provider runtime 只存在於同一 module 的 private local implementation，`ModelPool`
與 private loader 均以此 contract 作 return type。這個 slice 不讀取 artifact，亦不
實作 provider framework、cache、close/unload 或其他 lifecycle policy。

repo 目前也已在 `async_model_gateway.model_runtime.model_execution` 落地最小
generic `ModelExecution` boundary。它只接受 injected typed async callable，從
`LoadedRuntimeModel` 取得 provider runtime 後 direct-await 單次 invocation；一般
例外與 cancellation 原樣傳播。它不建立 provider framework，不負責 loader I/O、
orchestrator 或 remote execution wiring，也不管理 lifecycle、timeout 或 retry。

## Shared Vocabulary

以下詞彙是目前專案共享語彙的一部分：

- `model_name`
- `model_source_kind`
- `orchestrator`
- `model-payload`
- `model_artifact`
- `features`
- `ModelPool`
- `ModelGateway`
- `ModelExecution`
- response cache
- `runtime-model`
- local model source
- remote model source

這些詞彙大多仍維持在概念層，還不對應到完整的 Python API schema；目前已落地的
狹義實作，限於最小 `ModelRegistry` boundary、`model-payload` 的 canonical hashing
core、最小 `ModelPool` local acquisition slice、abstract `LoadedRuntimeModel`
consumption contract，以及最小 `ModelExecution` typed async invocation seam。

## Initialization 階段的 Out Of Scope

initialization 階段不包含：

- concrete API signatures
- cache-key algorithm details
- provider-specific contracts
- adapter schemas
- framework integration
- artifact I/O、provider framework 與完整 model pool lifecycle
- response cache implementation
- provider-specific execution runtime behavior 與完整 execution flow
- infrastructure selection

## 文件定位

`README.md` 應維持為專案的第一讀摘要文件。

這份文件則用來承接那些對 README 來說太深、但又足夠重要、必須在 initialization 階段保留下來的概念說明。

若需要進一步閱讀 core abstractions 的文件化邊界，請再讀 [docs/specs/core-abstractions-boundary.md](specs/core-abstractions-boundary.md)。
