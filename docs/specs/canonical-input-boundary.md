# canonical input boundary

## 摘要

這份文件定義 core abstractions 的輸入邊界。

在目前階段，正式共享的 canonical input 由以下四個欄位構成：

- `model_name`
- `model_source_kind`
- `model-payload`
- `features`

producer 除了提供 identity material，也必須在 local path 提供一份獨立的 read contract。

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
`async_model_gateway.model_registry.model_payload.hash_model_payload`。

這個 callable 會對 `model-payload` 做 recursive canonicalization，再產生
cross-process stable 的 SHA-256 hex digest。nested dict 會 canonicalize，
list 順序保留，scalar 不做 normalization，unsupported type 直接
`TypeError` fail closed。

## `features`

`features` 是 bounded capability vocabulary 所構成的 capability / usage-mode request。

它回答的是「這個模型這次要做什麼」，而不是「這是不是同一個模型」。

在目前階段，`features` 只影響 cache，不參與 model identity，也不被擴張成 provider contract、settings object 或 execution contract。

這一輪不需要定出完整 capability 詞彙清單，但語意方向固定為受控能力詞彙，而不是任意 producer label。

## Boundary

這一層負責：

這一層負責：

- 固定 `model_name`、`model_source_kind`、`model-payload`、`features` 作為正式共享輸入詞彙
- 聲明 external request shape 仍 deferred
- 固定它們是進入核心 orchestration boundary 前的 canonical input

這一層不負責：

- 產生 `payload-hash`
- 決定 cache identity
- 決定 registry freshness
- 校正 `model_name`
- 擴張 `model_source_kind` 成 provider taxonomy
- 對 `model-payload` 做語意等價判斷
- 把 `features` 擴張成自由標籤集合
- 定義 Python class / protocol

## 依賴方向

`orchestrator` 消費這一層提供的完整 canonical input。

`ModelRegistry` 可以依賴 `model_name`、`model_source_kind` 與 `model-payload` 來產生 `payload-hash`，但 hashing authority 不屬於這一層。

目前這個 authority 已先以 bounded callable 形式落地在
`async_model_gateway.model_registry.model_payload`；但 registry freshness、
cache identity wiring 與 orchestration flow 仍不屬於這份 spec 的實作範圍。

`features` 在目前階段只參與 cache 邊界，不參與 model identity authority。

## `model_artifact`

在 local path，producer 還必須提供一份獨立的 read contract，正式名詞固定為 `model_artifact`。

`model_artifact` 是 producer 與 local model side 之間的 read contract，不是 identity material。

它至少必須能表達：

- 怎麼選 loader family
- 要讀哪個 artifact
- 讀取時需要的額外資訊
- 讀完後要交付什麼邊界

`model_artifact` 不參與 `payload-hash` authority，也不應與 `model-payload` 混用。
