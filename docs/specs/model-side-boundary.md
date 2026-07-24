# model side boundary

## 摘要

這份文件定義 model side 的正式共享詞彙與責任邊界。

目前 model side 固定由三個業務名詞構成：

- `ModelRegistry`
- `ModelPool`
- `ModelGateway`

local runtime binding 與 execution 是 internal implementation concern，不是業務層或
package-consumer 的 surface。

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

`ModelPool` 是 local 路徑的 internal acquisition resource，不是 public package
boundary。internal composition 在 pool acquisition 前解析一組 Loader、Executor 與
concurrency policy；pool 只接收該 Loader，載入 raw provider runtime，並建立 concrete
generic `LoadedRuntimeModel`。pool 不保有 resolver、executor、cache 或 retained loader
state，也不選擇 executor。

這個實作 slice 不宣稱 local model availability、cache/reuse、上下載、close/unload 或
其他 lifecycle policy 已完成。runtime 不穿透 public boundary，且 `ModelPool` 沒有
package root re-export 或 public caller。

它不負責：

- execution policy 或 invocation semantics
- `payload-hash` authority
- registry freshness authority
- remote model side boundary
- 把 local runtime taxonomy 提前暴露成 canonical input 欄位

## Internal Loader 與 Runtime Binding

generic `ModelLoader` 與 concrete ONNX Loader 是 internal local acquisition
sub-boundary，不是 top-level public owner。Loader 的輸入是 `model_artifact`，而不是
`model-payload`，並直接回傳 provider-native runtime；它不建立 `LoadedRuntimeModel`、
不管理 execution gate，也不選擇 Executor。

目前 repo 已先落地這個 shared read contract 的最小 public owner：
`async_model_gateway.model_runtime.model_artifact`。`model_runtime` 是 umbrella
root，而 `model_artifact` package root 只公開 `ModelArtifact` 與
`LoaderFamily`。

其中：

- `ModelArtifact` 只承載 `loader_family`、`artifact_path`、`loader_options`
- `LoaderFamily` 是 bounded enum，starter vocabulary 只允許 `pickle`、`torch`、`onnx`
- loader family 必須由 producer 顯式提供，不得由 path、副檔名、artifact content 或 fallback heuristics 推導

private resolver 只根據 `artifact.loader_family` 作 explicit dispatch，並在 acquisition
前建立 Loader / Executor pairing：

- `LoaderFamily.ONNX` 配對 ONNX Loader、ONNX Executor 與 `max_concurrency=1`
- `LoaderFamily.PICKLE` 與 `LoaderFamily.TORCH` 在 loading 前以 `NotImplementedError` fail closed
- closed enum 的不可達 fallback 使用 `assert_never(...)`

ONNX Loader 透過 private helper lazy 建立 CPU-only `onnxruntime.InferenceSession`；它只
做 acquisition，不執行 inference。session 不在 application startup 建立，也不經由
public surface 交付。所有 route 都不根據 `artifact_path`、副檔名或內容推導 family。

它不負責：

- 依賴 `model-payload` 猜 loader
- 擁有 identity authority
- 對外暴露 top-level business owner 身分或 public package entrypoint
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

## Internal Executor 與 Loaded Runtime Resource

internal generic Executor 擁有 loaded runtime 的單次 invocation lifecycle。它接收
同一個 pre-resolved binding 所建立的 `LoadedRuntimeModel`，在成功取得其 Semaphore
後更新 `last_used_at`，再 direct-await concrete invocation；一般例外與 cancellation
原樣傳播。Executor 不載入模型、不管理 pool、不長期持有 runtime，也不根據 runtime
type、metadata 或 loader family 做 late dispatch。

`LoadedRuntimeModel` 是 concrete generic internal resource，而不是 abstract opaque
public contract。它只保存 provider runtime、execution gate、`loaded_at` 與
`last_used_at`；不提供 `execute`、`invoke`、`load`、provider handoff 或 lifecycle API。
它由 `ModelPool` 建立，不保存 Loader、Executor、family 或 registry。這不建立 public
executable runtime model、provider adapter、ONNX invoker、除 ONNX session acquisition
外的 artifact I/O、remote execution wiring 或 lifecycle policy。

對外能力邊界在目前階段沒有 local runtime entrypoint；能力差異仍先收斂在 `features`，
不先拆成多方法名公開 surface。
