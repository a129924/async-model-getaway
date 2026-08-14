# canonical input boundary

## 摘要

這份文件定義 core abstractions 的輸入邊界。

target workflow 的正式共享 canonical input 由以下五個欄位構成：

- `model_name`
- `model_source_kind`
- `model-payload`
- `features`
- `prediction_input`

producer 除了提供 identity material，也必須在 local path 提供一份獨立的 read contract。
目前已實作的 local request 仍以 `invocation` 表示受限輸入；它是 target
`prediction_input` 的 transition projection，不是已完成的通用 request shape。

## `model_name`

`model_name` 是 producer-controlled namespace key。

它的命名正確性由前面的 producer 管控，gateway 不負責替它命名、校正或做業務理解。

但它不是純 lookup 噪音，而是 canonical input 的正式欄位，會參與 identity context。

## `model_source_kind`

`model_source_kind` 是 model path 的最小分流訊號。

在目前階段，它的值域只固定為：

- `local`
- `remote`

它是 routing discriminator，但目前不擴張成 provider taxonomy 或 execution mode taxonomy。

local 的多樣性不升成 canonical input vocabulary，而是留在 `ModelPool` 內部消化。

## `model-payload`

`model-payload` 是嚴格字面的 model identity material。

原則是：開發者丟什麼，我就 hash 什麼。

只要開發者提供的 `model-payload` material 不同，就一律視為模型已更新。

它不應被解讀成一般 request payload，也不應被重寫成語意等價判斷的來源。

它只回答「這是不是同一個模型」，不負責告訴 loader 怎麼讀 artifact。

目前 repo 已有最小 implementation core：
`async_model_gateway.model_registry.ModelRegistry` 會消費
`model_name`、`model_source_kind` 與 `model-payload`，而
`async_model_gateway.model_registry.model_payload.ModelPayloadHasher`
仍是 `payload-hash` 的 public owner。

這個 public owner 的 method `hash_model_payload(...)` 會對
`model-payload` 做 recursive canonicalization，再產生 cross-process
stable 的 SHA-256 hex digest。nested dict 會 canonicalize，list 順序保留，
scalar 不做 normalization，unsupported type 直接 `TypeError` fail
closed。

## `features`

`features` 是 bounded capability vocabulary 所構成的 capability / usage-mode request。

它回答的是「這個模型這次要做什麼」，而不是「這是不是同一個模型」。

在 target workflow 中，`features` 不參與 model identity，也不被擴張成
provider contract 或 settings object。`Predictor` 是 capability / usage-mode
vocabulary 的 semantic owner：它驗證 feature snapshot，並投影 execution material
給 `ModelExecution`；`orchestrator` 不自行解讀 feature 語意。

這一輪不需要定出完整 capability 詞彙清單，但語意方向固定為受控能力詞彙，而不是任意 producer label。

## `prediction_input`

`prediction_input` 是會影響 application result 的實際 prediction material。
它和 `features` 不同：前者回答「這次要對什麼輸入產生結果」，後者回答「要使用
哪一種 bounded capability / usage mode」。

target workflow 要求它先被投影成 JSON-like identity material，並在第一次 await 前
建立深層 immutable snapshot。identity derivation 和 execution 必須消費同一 snapshot，
避免 caller mutation 使 cache key 和實際 execution input 分離。trace ID、request ID、
timestamp 等 observability-only material 不得進入 input identity。

`Predictor` 決定哪些 input differences 會影響結果；`PredictionInputHasher` 才負責
canonicalization 和 hash。兩者都是 target architecture vocabulary，尚未形成 Python
surface。

## Boundary

這一層負責：

- 固定 `model_name`、`model_source_kind`、`model-payload`、`features`、`prediction_input` 作為 target 共享輸入詞彙
- 聲明 external request shape 仍 deferred
- 固定它們是進入核心 orchestration boundary 前的 canonical input

這一層不負責：

- 產生 `payload-hash`
- 決定 cache identity 或自身 hash
- 決定 registry freshness
- 校正 `model_name`
- 擴張 `model_source_kind` 成 provider taxonomy
- 對 `model-payload` 做語意等價判斷
- 把 `features` 擴張成自由標籤集合
- 定義 Python class / protocol

## 依賴方向

`orchestrator` 消費這一層提供的完整 canonical input。

`ModelRegistry` 可以依賴 `model_name`、`model_source_kind` 與
`model-payload` 來產生 `payload-hash`，並以
`model_name + model_source_kind` 作為 store lookup identity；但 hashing
authority 不屬於這一層。

目前唯一已落地的 concrete store 是
`async_model_gateway.model_registry.stores.InMemoryRegistryStore`；它同樣只以
`model_name + model_source_kind` 做 lookup，不把 `payload-hash` 升格成
store key。

目前這個 authority 已先以 bounded callable 形式落地在
`async_model_gateway.model_registry.model_payload`；而最小 registry
freshness boundary 也已存在，但 cache identity wiring 與 orchestration
flow 仍不屬於這份 spec 的實作範圍。

`features` 在 target workflow 中只參與 feature identity，不參與 model identity authority。
`prediction_input` 則只參與 prediction-input identity；兩者不能互相取代。

## `model_artifact`

在 local path，producer 還必須提供一份獨立的 read contract，正式名詞固定為 `model_artifact`。

`model_artifact` 是 producer 與 local model side 之間的 read contract，不是 identity material。

目前 repo 已以 `async_model_gateway.model_runtime.model_artifact` 落地最小
public owner；`model_runtime` 是 umbrella root，而 `model_artifact` package
root 只 re-export `ModelArtifact` 與 `LoaderFamily`。

在這個最小 boundary 中：

- `LoaderFamily` 是 bounded enum，starter vocabulary 只允許 `pickle`、`torch`、`onnx`
- family 值必須由 producer 顯式提供，不得由副檔名、path fragment、artifact content 或 fallback heuristics 推導
- `ModelArtifact` 只承載 `loader_family`、`artifact_path` 與 `loader_options`
- `loader_options` 只承擔 JSON-like read-time metadata，不承擔 identity authority

`model_artifact` 不參與 `payload-hash` authority，也不應與 `model-payload` 混用。

repo 已落地最小 `ModelPool` acquisition slice：其 private `LocalModelLoader`
消費這個 shared read contract，僅依 explicit `LoaderFamily` 的 `pickle`、`torch`、
`onnx` 分支路由，並以 `assert_never(...)` 表示 closed enum 的不可達 fallback。
這不代表 artifact read、existence probing、concrete runtime-model contract、provider
abstraction、resource lifecycle 或其他 runtime behavior 已在 repo 中落地。
