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

目前 repo 已先落地一個最小實作：
`async_model_gateway.model_registry.model_payload.hash_model_payload`。

它只負責 `model-payload` 的 recursive canonicalization 與穩定
SHA-256 digest 產生；這不代表完整 `ModelRegistry`、freshness flow、
`orchestrator` 或 `ResponseCache` 已經實作完成。

## `orchestrator`

目前 `orchestrator` 的概念角色，是圍繞 canonical input 來協調 response generation。

高層預期 flow 如下：

1. Receive `model_name`, `model_source_kind`, `model-payload`, and `features`
2. Derive a payload-oriented identity from `model_name`, `model_source_kind`, and `model-payload`
3. Derive a response-cache identity from payload identity and `features`
4. Check response cache
5. Return cached response on hit
6. Request a `runtime-model` on miss
7. Use that `runtime-model` for response generation
8. Persist the generated response into response cache
9. Return the response

這裡描述的是高層概念 flow。除了 `model-payload` hashing core 已有最小實作外，
其餘 orchestration、freshness、cache 與 runtime acquisition flow 仍未在
repository 中落地。

## Responsibility Boundaries

### Gateway Side

目前 gateway side 被理解為負責：

- orchestration-oriented decisions
- response cache participation
- canonical input handling after normalization

### Model Side

目前 model side 被理解為負責：

- provision of a `runtime-model`
- local or remote model source selection
- model-side concerns behind the `runtime-model` boundary

local 與 remote 被視為 model-source concern，而不是不同的 gateway mode。

## Shared Vocabulary

以下詞彙是目前專案共享語彙的一部分：

- `model_name`
- `model_source_kind`
- `orchestrator`
- `model-payload`
- `features`
- response cache
- `runtime-model`
- local model source
- remote model source

這些詞彙大多仍維持在概念層，還不對應到最終定案的 Python class、protocol
或 API schema；目前唯一已落地的狹義實作，是
`model-payload` 的 canonical hashing core。

## Initialization 階段的 Out Of Scope

initialization 階段不包含：

- concrete API signatures
- cache-key algorithm details
- provider-specific contracts
- adapter schemas
- framework integration
- model pool implementation
- response cache implementation
- execution runtime behavior
- infrastructure selection

## 文件定位

`README.md` 應維持為專案的第一讀摘要文件。

這份文件則用來承接那些對 README 來說太深、但又足夠重要、必須在 initialization 階段保留下來的概念說明。

若需要進一步閱讀 core abstractions 的文件化邊界，請再讀 [docs/specs/core-abstractions-boundary.md](specs/core-abstractions-boundary.md)。
