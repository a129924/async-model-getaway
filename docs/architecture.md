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
3. Derive a `CacheKey` from already-derived payload identity and feature hash
4. Check response cache
5. Return cached response on hit
6. Use the relevant model-side provider path on miss
7. Delegate any provider invocation through its model-side boundary
8. Persist the generated response into response cache
9. Return the response

這裡描述的是高層概念 flow。除了最小 `ModelRegistry` boundary、`model-payload`
hashing core、最小 keyed/operational `response_cache` boundary，以及 internal local runtime slice
已落地外，其餘 orchestration 與完整 runtime acquisition/execution flow 仍未在
repository 中落地。

## Responsibility Boundaries

### Gateway Side

目前 gateway side 被理解為負責：

- orchestration-oriented decisions
- response cache participation
- canonical input handling after normalization
- coordination across provider, execution, and cache boundaries

在目前 repo 已落地的受限 cache boundary 中，gateway side 只先準備
`CacheKey`：它由 literal `namespace`、既有 `ModelPayloadHasher` 產生的
`model_payload_hash` 與已導出的 `feature_hash` 組成，cache 不再自行計算 hashes。
`ResponseCache` 只透過 async `CacheStore` 消費這個 key，並以 codec、token factory、
write-time expiry policy 與 injected UTC clock 建立完整 record。lookup 不會更新 expiry；
過期或不支援 record 的 cleanup 使用觀測到的 version token compare-delete，以免刪除較新的
replacement。invalidation 由獨立 `CacheInvalidator` 擁有；temporary deprecated legacy bridge
只在 `response_cache.compat`，不會穿透 package root。
policy 與 concrete store 都不穿透 package root 或 `ports` surface，且不擁有
persistence、eviction 或 orchestration semantics。

但 gateway side 不直接擁有 model invocation semantics。

### Model Side

目前 model side 被理解為負責：

- internal local runtime composition 作為 local binding owner
- `ModelPool` 作為 internal local runtime acquisition resource
- `ModelGateway` 作為 remote `runtime-model` provider / access boundary
- internal executor 作為 loaded runtime invocation lifecycle owner

local 與 remote 被視為 model-source concern，而不是不同的 gateway mode。

在 local path，`ModelPool` 內部會消費獨立的 shared read contract
`async_model_gateway.model_runtime.model_artifact`；這個 boundary 只固定
explicit `LoaderFamily` 與最小 artifact metadata，不承擔 loader runtime、
artifact I/O 或 identity authority。

repo 已落地其中最小的 internal local runtime slice。private composition 先依
`artifact.loader_family` 解析一組配對的 Loader、Executor 與 `max_concurrency`，再把
同一個 Loader 注入 `ModelPool` acquisition，並把同一個 Executor 用於 execution；
pool 不保有 resolver、executor、cache 或 retained loader state。它建立 concrete generic
`LoadedRuntimeModel`，只保存 provider runtime、`asyncio.Semaphore`、loaded timestamp
與 last-used timestamp。Executor 在成功取得 gate 後更新 last-used timestamp，再
direct-await provider invocation；一般例外與 cancellation 原樣傳播，且不做 late
type/family dispatch。

ONNX Loader 在 acquisition 時 lazy 建立 CPU-only provider session，而不是 application
startup 時預先建立；PICKLE 與 TORCH 仍在 loading 前 fail closed。local flow 是：

`ModelArtifact → resolve binding → injected Loader → ModelPool → LoadedRuntimeModel → paired Executor → result`。

所有 runtime composition、pool、loader、executor 與 loaded model surface 都是 internal；
沒有 public package export 或 compatibility adapter，provider session 也不會穿透
application / orchestrator boundary。此 slice 不實作真實 provider invocation、provider
framework、cache、close/unload、完整 lifecycle、timeout 或 retry。

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
- response cache
- `runtime-model`
- local model source
- remote model source

這些詞彙大多仍維持在概念層，還不對應到完整的 Python API schema；目前已落地的
狹義實作，限於最小 `ModelRegistry` boundary、`model-payload` 的 canonical hashing
core、internal local runtime binding/acquisition/execution slice；它不提供 public
runtime-model consumption API。

## Initialization 階段的 Out Of Scope

initialization 階段不包含：

- concrete API signatures
- cache-key algorithm details
- provider-specific contracts
- adapter schemas
- framework integration
- 除 ONNX session acquisition 外的 artifact I/O、provider framework 與完整 model pool lifecycle
- broader response cache implementation，例如 persistence、settings、eviction 與 orchestration wiring
- provider-specific execution runtime behavior 與完整 execution flow
- infrastructure selection

## 文件定位

`README.md` 應維持為專案的第一讀摘要文件。

這份文件則用來承接那些對 README 來說太深、但又足夠重要、必須在 initialization 階段保留下來的概念說明。

若需要進一步閱讀 core abstractions 的文件化邊界，請再讀 [docs/specs/core-abstractions-boundary.md](specs/core-abstractions-boundary.md)。
