# model side boundary

## 摘要

這份文件定義 model side 的正式共享詞彙與責任邊界。

目前 model side 固定由四個業務名詞構成：

- `ModelRegistry`
- `ModelPool`
- `ModelGateway`
- `ModelExecution`

`runtime-model` 則是 provider boundary 與 execution boundary 之間的 unified consumption surface。

## `ModelRegistry`

`ModelRegistry` 是 identity context owner、`payload-hash` authority 與 freshness authority。

目前 repo 已落地這個 boundary 的最小 class-first 版本：
`async_model_gateway.model_registry.ModelRegistry`。

對應的 process-local concrete store 目前則以 submodule public surface 形式提供：
`async_model_gateway.model_registry.stores.InMemoryRegistryStore`。它維持
async-only `RegistryStore` contract、empty-only constructor，以及同一 instance
上的單一 in-memory state 與 serialized read/write policy。

它透過位於 `async_model_gateway.model_registry.ports.store` 的 async-only
`RegistryStore` 做 lookup 與條件式 persistence，並持續以既有的
`async_model_gateway.model_registry.model_payload.ModelPayloadHasher`
作為 `payload-hash` owner。

它負責：

- 消費以下 identity context：
  - `model_name`
  - `model_source_kind`
  - `model-payload`
- 以 `model_name + model_source_kind` 作為 store lookup identity
- 從上述 identity context 派生穩定的 `payload-hash`
- 交付受限的 freshness decision：`first-seen`、`unchanged`、`changed`
- 在 freshness 不是 `unchanged` 時更新 registry state
- 提供與 payload identity 相關的決策資訊給 `orchestrator`

它不負責：

- model 下架
- local model lifecycle
- remote model execution
- response cache persistence

gateway / registry 不做語意等價判斷；只要 `model-payload` material 不同，就一律視為模型已更新。

目前已落地的 hashing core 也遵守這個原則：dict key order 會被 canonicalize，
但 list order 仍屬 identity material，`1` 與 `1.0` 也不會被視為同一份 payload。

目前這個最小 boundary 仍不擴張到 cache wiring、runtime-model acquisition、
`ModelPool`、`ModelGateway` 或更寬的 model-side orchestration。

## `ModelPool`

`ModelPool` 是 local 路徑的最小 public acquisition boundary。

目前 repo 已在 `async_model_gateway.model_runtime.model_pool` package root
公開 `ModelPool`，其唯一 public acquisition method 是 async
`acquire(self, artifact: ModelArtifact) -> LoadedRuntimeModel`。一個 pool instance
在建立時保有一個 private `LocalModelLoader`，並直接 await 其 typed load 結果。

這個實作 slice 只負責將有效 `ModelArtifact` 交給 retained private loader；它不宣稱
local model availability、cache/reuse、上下載、close/unload 或其他 lifecycle policy
已完成。它以 `LoadedRuntimeModel` 作 abstract opaque acquisition-handle contract；provider
runtime 不穿透 public boundary。private `LocalModelLoader` 在 acquisition 完成後建立
loader-local private handle，保存 local provider runtime 與 explicit `LoaderFamily`
provenance，並以 non-public internal handoff 交給最小 `ModelExecution` boundary。

它不負責：

- execution policy 或 invocation semantics
- `payload-hash` authority
- registry freshness authority
- remote model side boundary
- 把 local runtime taxonomy 提前暴露成 canonical input 欄位

## `LocalModelLoader`

`LocalModelLoader` 是 `ModelPool` 內部的 private local acquisition sub-boundary，
不是 top-level public owner。

它的輸入是 `model_artifact`，而不是 `model-payload`。

目前 repo 已先落地這個 shared read contract 的最小 public owner：
`async_model_gateway.model_runtime.model_artifact`。`model_runtime` 是 umbrella
root，而 `model_artifact` package root 只公開 `ModelArtifact` 與
`LoaderFamily`。

其中：

- `ModelArtifact` 只承載 `loader_family`、`artifact_path`、`loader_options`
- `LoaderFamily` 是 bounded enum，starter vocabulary 只允許 `pickle`、`torch`、`onnx`
- loader family 必須由 producer 顯式提供，不得由 path、副檔名、artifact content 或 fallback heuristics 推導

目前實作只根據 `artifact.loader_family` 作 explicit dispatch：

- `LoaderFamily.PICKLE` 直接 await private `_load_pickle(...)`
- `LoaderFamily.TORCH` 直接 await private `_load_torch(...)`
- `LoaderFamily.ONNX` 直接 await private `_load_onnx(...)`
- closed enum 的不可達 fallback 使用 `assert_never(...)`

目前 `PICKLE` 與 `TORCH` handler 都是 no-I/O placeholder，維持
`NotImplementedError`。`ONNX` handler 則透過 private helper 建立 CPU-only
`onnxruntime.InferenceSession`，再直接建構 loader-local private opaque handle；它只做
acquisition，不執行 inference。session 只在 `LocalModelLoader.load(...)` 選定 ONNX
route 時 lazy 建立，而非 application startup 預先建立。已落地的 local flow 是：

`ModelArtifact → LocalModelLoader → provider session → LoadedRuntimeModel → ModelExecution → result`。

其中 result 僅指 injected typed invoker 的回傳值，不建立 ONNX result schema 或 adapter。
所有 route 都不根據 `artifact_path`、副檔名或內容推導 family。

它不負責：

- 依賴 `model-payload` 猜 loader
- 擁有 identity authority
- 對外暴露 top-level business owner 身分
- 除 ONNX session acquisition 外的 artifact I/O、provider framework 或 lifecycle policy

## Fail-Closed 原則

已知 family 的目前 no-I/O handler 會以 `NotImplementedError` fail closed。未知
enum fallback 是 static unreachable path，而非新的 runtime invalid-family policy。

猜副檔名、猜 pickle、猜 object shape 不能作為正式主路徑。因此，即使
`artifact_path` 看起來像既有格式，shared read contract 仍不得省略 explicit
`LoaderFamily`，也不得把 `loader_options` 升格成 identity material。

## `ModelGateway`

`ModelGateway` 是 remote `runtime-model` provider / access boundary。

它只屬於 `remote` 路徑。

它負責：

- remote model source 路徑
- remote `runtime-model` provider / access
- 對上層邊界交付可消費的 remote `runtime-model`

remote 目前只有單一實際需求，不需要先做更細 provider 分類。

它與 `ModelPool` 並列，而不是被 `ModelPool` 吞進去。

它不負責：

- execution policy 或 invocation semantics
- local model runtime lifecycle
- `payload-hash` authority

## `ModelExecution`

`ModelExecution` 是 model side 的 invocation semantics owner。

它與 `ModelPool` / `ModelGateway` 並列，是 sibling boundary，不是 provider
boundary 的 child concern。

目前 repo 已在 `async_model_gateway.model_runtime.model_execution` package root
公開 generic `ModelExecution`。constructor 只接收 injected typed async callable；
`execute(...)` 從 `LoadedRuntimeModel` 的 non-public handoff 取得 provider runtime，
再 direct-await 單次 invocation。runtime、invocation 與 result 不經轉換，一般例外與
cancellation 原樣傳播。它是唯一的 production handoff consumer，且不依
`loader_family` 做 provider-specific `match/case` dispatch。

它負責：

- 消費統一的 `runtime-model` surface
- 擁有 model invocation semantics
- 作為 `orchestrator` 委派 execution 的正式 boundary
- 在 execution 階段承接 local / remote provider 之後的統一消費責任

它不負責：

- local `runtime-model` provider / lifecycle
- remote `runtime-model` provider / access
- `payload-hash` authority 或 registry freshness authority
- response cache identity authority
- 把 `features` 升格成 provider-specific execution contract
- 建立 provider framework 或執行 loader I/O
- orchestrator wiring 或 remote execution wiring
- cache/reuse、close/unload、timeout、retry 或 task lifecycle

## `runtime-model`

`runtime-model` 是 `ModelPool` / `ModelGateway` 與 `ModelExecution` 之間的
unified consumption surface。

它不是 system-level execution owner。

目前 `async_model_gateway.model_runtime.runtime_model` 已公開 abstract nominal
`LoadedRuntimeModel`。它唯一的 public semantic 是 readonly `loader_family`；
`_provider_runtime()` 是非 public 的 model-side internal handoff，只由目前的最小
`ModelExecution` boundary 消費。concrete `_LocalLoadedRuntimeModel` 的 construction
ownership 位於 private `LocalModelLoader`，而非 public runtime-model contract module；
它不從 package root export，因此 provider-specific object 不會成為 package consumer
contract；application / orchestrator 不可把它當成 provider session getter。這不建立
executable runtime model、provider adapter、ONNX invoker、除 ONNX session acquisition
外的 artifact I/O、remote execution wiring 或 lifecycle policy。

對外能力邊界在目前階段採統一入口；能力差異先收斂在 `features`，不先拆成多方法名公開 surface。
