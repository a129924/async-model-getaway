> Semantic warning: 在 authoring 當下找不到
> `analysis/model-registry-in-memory-store/requirements.md` 與
> `analysis/model-registry-in-memory-store/technical-spec.md`。此 plan
> 依據 repo exploration、workflow contract 與已鎖定的人為決策撰寫；analysis
> layer 目前屬缺件狀態，不可視為已補齊。

# model-registry-in-memory-store

## Goal / Outcome

- 以 repo-visible planning artifacts 凍結 `InMemoryRegistryStore` 的 bounded
  implementation contract，讓 repository 在既有最小 `ModelRegistry` boundary
  上新增一個 async-only、process-local 的 concrete `RegistryStore`
  implementation。
- 當此 topic 完成時，`async_model_gateway.model_registry.stores.in_memory`
  會提供 `InMemoryRegistryStore`，其 public surface 維持 submodule public、
  不做 `async_model_gateway.model_registry` root re-export，並以最小必要 docs
  更新與 patch bump 反映 stable-library / release-facing 影響。

## Scope

- **In scope**:
  - 在 `plan/model-registry-in-memory-store/` 下建立本 topic 的 repo-visible
    planning artifacts。
  - 新增 `InMemoryRegistryStore` 作為 `RegistryStore` 的 concrete subclass。
  - 規劃 async-only `get_entry()` / `upsert_entry()` implementation，並要求使用
    `typing_extensions.override`。
  - 規劃 empty-only `__init__()` 與單一 `asyncio.Lock` 的 same-instance
    serialized read/write policy。
  - 維持 store lookup identity 為 `model_name + model_source_kind`。
  - 規劃 store tests、store package-surface tests，與 model-registry package
    surface tests 的必要更新。
  - 規劃使用 `ModelRegistry(store=InMemoryRegistryStore())` 的端對端 regression
    test，並沿用既有 `tests/model_registry/test_registry.py` 測試面。
  - 規劃 `README.md`、`docs/specs/model-side-boundary.md`、
    `docs/specs/canonical-input-boundary.md`、
    `docs/specs/core-abstractions-boundary.md` 的最小必要更新。
  - 將 `src/async_model_gateway/__version__.py` 與 `pyproject.toml` 納入
    release-facing artifact paths，並鎖定 patch bump。
  - 將 `uv.lock` 納入 release-facing artifact paths，確保 editable package
    version 會隨 patch bump 同步。

- **Out of scope**:
  - 任何 sync API 或 dual sync/async surface。
  - 任何 delete / clear / list / seeded constructor behavior。
  - 任何 persistence backend、disk state、database wiring 或 broader
    persistence abstraction。
  - 任何 broader model-side topics、registry owner redesign、freshness-policy
    redesign 或 payload-hasher contract 變更。
  - `async_model_gateway.model_registry` root package 對此 store 的 re-export。

## Locked Decisions

- topic slug 固定為 `model-registry-in-memory-store`；此 topic 不延續
  `model-execution-boundary`。
- 此 topic 採用 Python planning extension path，並保留 companion
  `*.step.md` 與 `*.spec.md` artifacts。
- D1 verdict: `non-trivial`。此 topic 會新增 concrete async store surface、
  擴張 package layout、tests、docs 與 release-facing metadata paths，因此需要
  spec / step / review companions。
- `InMemoryRegistryStore` 是唯一允許新增的 concrete store class name。
- `InMemoryRegistryStore` 必須具體繼承
  `async_model_gateway.model_registry.ports.RegistryStore`。
- `get_entry()` 與 `upsert_entry()` 必須使用 `typing_extensions.override`。
- constructor 鎖為 empty-only `__init__()`；不得要求 seed data、外部 mapping、
  lock injection 或 other runtime collaborator。
- concurrency policy 固定為單一 `asyncio.Lock` 序列化同一 instance 的讀寫；
  不得改成 reader-writer lock、per-key lock、global singleton lock 或 lock-free
  contract。
- `InMemoryRegistryStore` 是 submodule public surface；允許透過
  `async_model_gateway.model_registry.stores` package surface 暴露，但不得從
  `async_model_gateway.model_registry` root re-export。
- lookup key 維持 `model_name + model_source_kind`；不得把 `payload_hash`
  升格為 store lookup identity。
- 此 topic 是 stable-library / release-facing topic，versioning policy 鎖定為
  `patch bump`。
- `README.md`、`docs/specs/model-side-boundary.md`、
  `docs/specs/canonical-input-boundary.md`、
  `docs/specs/core-abstractions-boundary.md`、
  `src/async_model_gateway/__version__.py`、`pyproject.toml`、`uv.lock`
  都必須列入 implement lifecycle artifact paths。
- stores package-surface test artifact path 固定為
  `tests/model_registry/stores/test_stores_package_surface.py`，以避免在既有
  pytest import contract 下與 `tests/model_registry/test_model_registry_package_surface.py`
  發生 basename collision；此 topic 不調整 repo-wide pytest import mode。
- 端對端 registry/store regression test artifact path 固定為
  `tests/model_registry/test_registry.py`；此 topic 只在既有 registry 測試面補上
  `ModelRegistry(store=InMemoryRegistryStore())` coverage，不擴張成新的測試矩陣。
- Non-goal 固定為：不得把本 topic 擴張成 persistence abstraction、broader
  architecture、full docs sweep 或 major release work。

## Boundaries / Exclusions

- Planning actor 只負責 author 本 topic 的 planning artifacts，不實作 source、
  tests、docs 或 version metadata。
- Implementer 之後只能修改 `## Artifact Paths` 中明確列出的 paths；若需要額外
  source/test/doc/release path，必須回到 `spec-and-plan-finalization`。
- Reviewer 只負責獨立 plan verdict 與後續 implementation-review verdict；
  reviewer 不實作 creator work，也不關閉 `human check` / `human merge`。
- Human gate artifacts 可以被本 plan 宣告 exact path，但此輪不建立、不預填、
  不代替 human pass。
- 此 topic 不得藉由 in-memory store 擴張到 broader model-side architecture、
  persistence policy、cache wiring、registry API widening 或 release automation。

## Status / Allowed Transitions

- **Current**: `review-ready`
- **Execution model**: follow
  `spec-and-plan-finalization -> implement-plan -> pr-comment -> pr-comment-review-pr-comments-and-fix -> release`；
  由於此 topic 明確宣告 stable-library / release-facing timing，因此 `release`
  workflow 條件成立。
- **Allowed transitions**:
  - `planned` -> `creator-in-progress`
  - `creator-in-progress` -> `review-ready`
  - `review-ready` -> `reviewer-in-progress`
  - `reviewer-in-progress` -> `approved`
  - `reviewer-in-progress` -> `needs-rework`
  - `needs-rework` -> `creator-in-progress`
  - `approved` -> `creator-in-progress`
  - `approved` -> `publish-in-progress`
  - `publish-in-progress` -> `pr-open`
  - `publish-in-progress` -> `merged`
  - `pr-open` -> `needs-rework`
  - `pr-open` -> `merged`
  - `merged` -> `released`

Routing notes:

- `approved` 依 repo contract 必須同時具備 repo-visible plan-review artifact
  的 `approved` verdict 與 explicit repo-visible `human check` gate pass。
- 此 topic 採用 Python extension path；`implement-plan` 內第一個 mandatory
  Python subphase 仍是 RED test authoring。
- 此 topic 會宣告 `*.red-tests.yaml` 與
  `*.implementation-review.yaml` companion paths 供後續 workflow 使用；宣告
  path 不代表 artifact 已存在或 gate 已通過。
- 此次 planning repair 已變更 executable artifact paths；既有
  `model-registry-in-memory-store.plan-review.json` 與
  `model-registry-in-memory-store.human-check.json` 僅能視為 repair 前的歷史
  gate evidence，後續必須依更新後的 plan 重新經過 reviewer verdict 與
  explicit human check，才能再次進入 `implement-plan`。
- 任何對 class name、constructor shape、override policy、single-lock
  concurrency、public surface、artifact paths、README/VERSION timing 或 bump
  direction 的變更，都必須回到 `spec-and-plan-finalization`。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/model-registry-in-memory-store/model-registry-in-memory-store.plan.md` | Planning actor | 本 topic 的 repo-visible execution contract |
| Topic step tracking | `plan/model-registry-in-memory-store/model-registry-in-memory-store.step.md` | Implementer | repo-visible implementation-progress companion artifact maintained by the executor during `implement-plan` |
| Topic behavior spec | `plan/model-registry-in-memory-store/model-registry-in-memory-store.spec.md` | Planning actor | non-trivial Python behavior contract for TDD and later review |
| Plan review artifact | `plan/model-registry-in-memory-store/model-registry-in-memory-store.plan-review.json` | Reviewer | repo-visible planning gate verdict |
| Human check gate artifact | `plan/model-registry-in-memory-store/model-registry-in-memory-store.human-check.json` | Human | explicit repo-visible gate that clears the approved plan for `implement-plan` |
| RED test artifact | `plan/model-registry-in-memory-store/model-registry-in-memory-store.red-tests.yaml` | Implementer | repo-visible TDD gate evidence produced during `implement-plan` |
| Implementation review artifact | `plan/model-registry-in-memory-store/model-registry-in-memory-store.implementation-review.yaml` | Reviewer | repo-visible implementation-review gate evidence before PR routing |
| Stores package surface | `src/async_model_gateway/model_registry/stores/__init__.py` | Implementer | submodule-level public surface for concrete store exposure |
| In-memory store implementation | `src/async_model_gateway/model_registry/stores/in_memory.py` | Implementer | concrete async in-memory `RegistryStore` implementation |
| Store behavior tests | `tests/model_registry/stores/test_in_memory.py` | Implementer | async behavior coverage for lookup, upsert, concurrency, and identity rules |
| Stores package-surface tests | `tests/model_registry/stores/test_stores_package_surface.py` | Implementer | verifies submodule public exposure without root re-export while keeping a unique pytest basename |
| Model-registry package-surface tests | `tests/model_registry/test_model_registry_package_surface.py` | Implementer | guards root package non-re-export contract against store leakage |
| Model-registry end-to-end regression tests | `tests/model_registry/test_registry.py` | Implementer | verifies `ModelRegistry(store=InMemoryRegistryStore())` against the bounded registry/store integration path |
| Project summary | `README.md` | Implementer | minimal first-read update for new in-memory store availability |
| Model side boundary spec | `docs/specs/model-side-boundary.md` | Implementer | aligns model-side wording with concrete in-memory registry store availability |
| Canonical input boundary spec | `docs/specs/canonical-input-boundary.md` | Implementer | preserves `model_name + model_source_kind` lookup identity wording |
| Core abstractions boundary spec | `docs/specs/core-abstractions-boundary.md` | Implementer | keeps boundary index and cross-reference wording consistent |
| Package version source | `src/async_model_gateway/__version__.py` | Implementer | repo-visible package version bump source for patch release |
| Packaging metadata | `pyproject.toml` | Implementer | package version metadata bump aligned to patch release |
| Lockfile metadata | `uv.lock` | Implementer | lockfile sync required so editable package version matches the declared patch bump |

Artifact path notes:

- 本 topic 不修改 `src/async_model_gateway/model_registry/__init__.py`，因為 root
  re-export for the store 明確屬 out-of-scope。
- 若 implementer 發現必須修改其他 source/test/doc paths 才能完成此 topic，
  這是 plan alignment 問題，不得靜默擴張。
- 本 topic 明確宣告 review / human / release companion artifact paths，但此輪
  plan authoring 不建立 reviewer artifact 或 human gate artifact。

## Stable library metadata

- `README row`: 更新 `README.md` 中對已落地 model-registry boundary 的摘要，
  以最小必要文字補上 in-memory store availability 與 submodule public
  surface；不做 full docs sweep。
- `VERSION bump`: `patch bump`。
- `timing`: `release`。
- `rationale`: 此 topic 雖然只新增一個 bounded concrete store，但它會影響
  package surface、使用者可見文件與版本 metadata，因此必須以 stable-library /
  release-facing contract 明確宣告。
- `release note expectation`: release workflow 應記錄新增
  `InMemoryRegistryStore`、其 async-only / in-memory 性質、以及 root package
  不 re-export 此 store。

## Implementation Steps

1. 在 `tests/model_registry/stores/test_in_memory.py` 撰寫 RED coverage，鎖定
   `InMemoryRegistryStore` 的 empty-only constructor、`model_name +
   model_source_kind` lookup identity、first upsert / overwrite behavior、
   missing-entry return path，以及相同 instance 上以單一 `asyncio.Lock`
   序列化讀寫的 contract。
2. 在 `tests/model_registry/stores/test_stores_package_surface.py`、
   `tests/model_registry/test_model_registry_package_surface.py` 與
   `tests/model_registry/test_registry.py` 撰寫或更新 bounded coverage，分別鎖定
   store submodule public surface、root package 非 re-export contract，以及
   `ModelRegistry(store=InMemoryRegistryStore())` 的端對端 regression path。
3. 新增 `src/async_model_gateway/model_registry/stores/in_memory.py` 與
   `src/async_model_gateway/model_registry/stores/__init__.py`，讓
   `InMemoryRegistryStore` 成為 `RegistryStore` concrete subclass，維持
   empty-only `__init__()`、單一 `asyncio.Lock`、以及
   `typing_extensions.override` 標註的 async `get_entry()` /
   `upsert_entry()`。
4. 更新 `README.md`、`docs/specs/model-side-boundary.md`、
   `docs/specs/canonical-input-boundary.md` 與
   `docs/specs/core-abstractions-boundary.md`，以最小必要 wording 反映新的
   in-memory store、submodule public surface、以及未變更的 lookup identity
   boundary。
5. 在 `src/async_model_gateway/__version__.py`、`pyproject.toml` 與 `uv.lock`
   規劃並實作 patch bump sync，讓 release-facing metadata 與 editable package
   version 對齊；不得擴張成 major/minor release work。
6. 執行本 topic 的 bounded validation，更新
   `plan/model-registry-in-memory-store/model-registry-in-memory-store.step.md`，
   並在後續 workflow 需要時產出 implementer-owned 的
   `model-registry-in-memory-store.red-tests.yaml` 與其他 implementer-owned
   bounded evidence，確認本 topic 的 repo-visible validation evidence 已完成並可
   供後續 gate 檢查。

## Validation / Acceptance Checks

- Canonical plan sections、status names、allowed transitions 與 reviewer
  handoff shape 必須持續符合 repo workflow contracts。
- `model-registry-in-memory-store.spec.md` 必須存在，因為此 topic 已鎖定為
  `non-trivial`。
- `model-registry-in-memory-store.step.md` 必須鏡像所有編號的 implementation
  steps，且目前僅 `plan-authoring` 完成；不得預填 implementation 或 review
  completion。
- Validation 必須證明 `InMemoryRegistryStore` 是
  `RegistryStore` concrete subclass，且 `get_entry()` / `upsert_entry()`
  使用 `typing_extensions.override`。
- Validation 必須證明 constructor 維持 empty-only `__init__()`，沒有 seed /
  collaborator injection / sync helper surface。
- Validation 必須證明相同 instance 的讀寫以單一 `asyncio.Lock`
  序列化，不引入 broader concurrency policy。
- Validation 必須證明 store lookup identity 仍只使用
  `model_name + model_source_kind`，而非 `payload_hash`。
- Validation 必須證明 `InMemoryRegistryStore` 可由
  `async_model_gateway.model_registry.stores` 取得，但不會從
  `async_model_gateway.model_registry` root package 洩漏。
- Validation 必須證明 `tests/model_registry/test_registry.py` 內存在
  `ModelRegistry(store=InMemoryRegistryStore())` 的 bounded regression
  coverage，且不額外擴張新的 registry 測試矩陣。
- Validation 必須證明 stores package-surface test path 維持 unique basename，
  不與 `tests/model_registry/test_model_registry_package_surface.py` 在既有 pytest import
  contract 下產生 collision。
- Validation 必須證明 `README.md`、docs/specs、`__version__.py`、
  `pyproject.toml` 與 `uv.lock` 的 release-facing changes 與 patch bump 一致，
  且 `uv lock --check` 不因 editable package version 落後而失敗，同時不擴張成
  full docs sweep 或 major release work。

## Reviewer Handoff

```json
{
  "verdict": "approved|needs-rework",
  "blocking_issues": [],
  "copilot_feedback_triage": {
    "ADDRESS": [],
    "DISCUSS": [],
    "SKIP": []
  }
}
```

## Post-merge / release actions

- Merge 後進入條件式 `release` workflow。
- `release` 階段需執行 patch bump publication work，並確認 release-facing
  metadata 與 docs wording 已與 merged implementation 對齊。

## Open Questions / Unresolved Items

- None. 目前沒有 blocking open questions；若後續需要新增 artifact path、調整
  public surface、或改變 release-facing intent，必須回到
  `spec-and-plan-finalization` 重新對齊 contract。

## Non-goals

- 本 topic 不新增 sync wrapper、sync facade 或 test-only sync helper。
- 本 topic 不新增 delete / clear / list / seed constructor APIs。
- 本 topic 不引入 persistence backend、pluggable storage abstraction 或 broader
  registry architecture rewrite。
- 本 topic 不把 `InMemoryRegistryStore` root re-export 到
  `async_model_gateway.model_registry`。
- 本 topic 不做 full docs sweep、minor/major version bump 或 release automation
  overhaul。

## Current Context

- repository 已有最小 `ModelRegistry` boundary、`RegistryStore` abstract port、
  與對應 package-surface / behavior tests，但目前尚未存在 concrete
  `model_registry.stores` package。
- `src/async_model_gateway/model_registry/ports/store.py` 已定義 async-only
  `RegistryStore.get_entry(...)` 與 `upsert_entry(...)` contract，lookup identity
  維持 `model_name + model_source_kind`。
- `tests/model_registry/test_model_registry_package_surface.py` 已保護 root package 只 re-export
  `ModelRegistry`，因此新 store 不能從 root package 洩漏；新增 stores
  package-surface coverage 時必須避開相同 basename。
- `README.md` 與 docs/specs 目前描述的是最小 registry boundary；新增 concrete
  store 後需要最小必要 wording 更新。
- package version baseline 目前為 `0.4.1`；此 topic 已鎖定為 patch bump。

## Requirements

1. Repository 必須新增一個名為 `InMemoryRegistryStore` 的 concrete
   `RegistryStore` implementation，且 class name 不得改名。
2. `InMemoryRegistryStore` 必須維持 async-only `get_entry()` /
   `upsert_entry()` contract，並在兩個 override methods 上使用
   `typing_extensions.override`。
3. `InMemoryRegistryStore.__init__()` 必須是 empty-only constructor，且同一
   instance 的讀寫必須由單一 `asyncio.Lock` 序列化。
4. Store lookup identity 必須維持 `model_name + model_source_kind`，不得把
   `payload_hash` 升格為 key。
5. `InMemoryRegistryStore` 只能作為 `model_registry.stores` submodule public
   surface；`async_model_gateway.model_registry` root package 不得 re-export 它。
6. Implementation lifecycle 必須涵蓋 store tests、package-surface tests、
   `README.md`、相關 specs、`src/async_model_gateway/__version__.py` 與
   `pyproject.toml`。
7. 此 topic 作為 stable-library / release-facing topic，必須以 patch bump
   完成版本 metadata 更新，且 release workflow 必須被明確宣告。

## Decisions

- Async-planning status: triggered — cite trigger evidence: 新增 async-only
  `RegistryStore` concrete implementation，並明確鎖定單一 `asyncio.Lock`
  的 same-instance concurrency policy，屬於 planning-stage async boundary /
  lifecycle / concurrency decision。
- Module/package placement: 新增 source 在
  `src/async_model_gateway/model_registry/stores/` 下；不修改 root package
  re-export surface。
- New public API: yes — 新增 submodule-level public class
  `async_model_gateway.model_registry.stores.InMemoryRegistryStore`。
- Interface changes: yes — `model_registry.stores` package 成為新的 concrete
  store exposure point，
  `tests/model_registry/test_model_registry_package_surface.py` 需同步防止 root package surface
  漂移，而 stores-side coverage 必須使用不衝突的 test basename。
- Breaking changes allowed: no — 既有 `ModelRegistry` root package contract、
  lookup identity 與 async port contract 都維持不變。
- New dependencies: no — 只使用標準庫 `asyncio` 與既有 `typing_extensions`。
- Error handling strategy: `get_entry()` 對缺失 key 回傳 `None`；`upsert_entry()`
  以最後寫入值覆蓋同 lookup identity 舊 entry；topic 不新增 custom exceptions。
- Typing strategy: fully typed；沿用既有 strict typing baseline，僅在 override
  上使用 `typing_extensions.override`。

### Async boundary decision

- `InMemoryRegistryStore` 對外維持 async-only methods，以符合既有
  `RegistryStore` port；不新增 sync mirror API。
- 內部資料結構可為同步 in-memory mapping，但所有對外讀寫都必須經過 async
  method boundary 與 lock-protected critical section。

### Resource lifecycle decision

- `InMemoryRegistryStore` 自己擁有其 in-memory state 與單一 `asyncio.Lock`。
- empty-only `__init__()` 建立初始空 state 與 lock；topic 不允許外部注入 state、
  lock 或 seed data。
- 此 store 無外部 I/O resource、無 close/shutdown lifecycle。

### Concurrency model

- 同一 instance 的 `get_entry()` 與 `upsert_entry()` 一律以單一
  `asyncio.Lock` 序列化。
- 不做 per-key lock、optimistic read、reader/writer split 或 background task
  ownership。
- 不嘗試為跨 instance 提供一致性；concurrency contract 僅限 same-instance。

### Failure model

- topic 不引入新的 checked/custom exception hierarchy。
- 缺失 key 視為正常讀取結果並回傳 `None`。
- 寫入以覆蓋 semantics 處理同 identity 舊值；不額外提供 conflict error。
- 若未來實作出現 unexpected internal failure，應直接 propagate，而不是在此
  topic invent translation layer。

### Cancellation / timeout policy

- 本 store 不宣告額外 timeout、retry 或 cancellation translation。
- 若 coroutine 在等待或持有 lock 時被取消，實作必須依 `asyncio.Lock`
  正常釋放 / cleanup semantics 運作；topic 不新增 custom cancellation API。
- 因為無外部 I/O，此 topic 不需要額外 timeout budget。

### Validation plan

- 以 async pytest coverage 驗證 empty-only constructor、missing-entry read、
  overwrite behavior、lookup identity、same-instance serialization 與 public
  surface boundaries。
- 以 package-surface tests 驗證 submodule exposure 與 root non-re-export。
- 以 docs/version metadata checks 驗證 README/specs/patch bump 對齊。

### Handoff notes for the implementer

- 不要把 in-memory convenience 擴張成 sync helper；所有 public methods 仍維持
  async-only。
- 不要把 lock policy 改寫成更寬的 concurrency design；single-lock
  same-instance serialization 是 frozen decision。
- 不要修改 `src/async_model_gateway/model_registry/__init__.py` 去 re-export
  store。
- patch bump 僅限此 topic 所需的 version metadata 變更，不做 broader release
  automation。

## Public Contract / API Changes

- New public class:
  - `async_model_gateway.model_registry.stores.InMemoryRegistryStore`
- Planned constructor:
  - `def __init__(self) -> None`
- Planned methods:
  - `async def get_entry(*, model_name: str, model_source_kind: ModelSourceKind) -> RegistryEntry | None`
  - `async def upsert_entry(entry: RegistryEntry) -> None`
- Backward compatibility:
  - 既有 `ModelRegistry` root import surface 不變。
  - `RegistryStore` abstract port signature 不變。
  - `payload_hash` 不參與 lookup identity。
- Exceptions:
  - 本 topic 不新增 public custom exceptions；缺失 key 以 `None` 表示。

## Affected Files / Modules

Likely affected files:
- `src/async_model_gateway/model_registry/stores/__init__.py`
- `src/async_model_gateway/model_registry/stores/in_memory.py`
- `tests/model_registry/stores/test_in_memory.py`
- `tests/model_registry/stores/test_stores_package_surface.py`
- `tests/model_registry/test_model_registry_package_surface.py`
- `README.md`
- `docs/specs/model-side-boundary.md`
- `docs/specs/canonical-input-boundary.md`
- `docs/specs/core-abstractions-boundary.md`
- `src/async_model_gateway/__version__.py`
- `pyproject.toml`

Candidate files to inspect:
- `src/async_model_gateway/model_registry/ports/store.py`
- `src/async_model_gateway/model_registry/entry.py`
- `src/async_model_gateway/model_registry/__init__.py`
- `tests/model_registry/test_registry.py`

## Test Plan

- Happy path:
  - `tests/model_registry/stores/test_in_memory.py` 驗證 first upsert 後可用
    `model_name + model_source_kind` 讀回相同 `RegistryEntry`。
- Invalid input:
  - `tests/model_registry/stores/test_stores_package_surface.py` 與
    `tests/model_registry/test_model_registry_package_surface.py` 驗證 package surface 不會把
    store root re-export；任何 root import assumption 都應 fail。
- Edge case:
  - `tests/model_registry/stores/test_in_memory.py` 驗證 missing key 讀取回傳
    `None`，以及相同 `model_name` 但不同 `model_source_kind` 不互相覆蓋。
- Regression:
  - `tests/model_registry/test_model_registry_package_surface.py` 繼續保護
    `async_model_gateway.model_registry.__all__ == ["ModelRegistry"]`，
    避免新增 store 造成 root package surface 漂移。
- Backward compatibility:
  - 驗證 `RegistryStore` abstract contract 未改簽名、`payload_hash` 未出現在
    lookup method signature、且 docs/version updates 不暗示 root import 改變。
- Async-specific:
  - 使用 async tests 驗證同一 instance 的並發 `get_entry()` / `upsert_entry()`
    不會繞過單一 `asyncio.Lock` 的序列化決策。

## Validation Commands

- `uv run pytest tests/model_registry/stores/test_in_memory.py tests/model_registry/stores/test_stores_package_surface.py tests/model_registry/test_model_registry_package_surface.py -v`
- `uv run ruff check src tests README.md docs/specs plan/model-registry-in-memory-store`
- `uv run pyright`

## Risks

- 由於這是第一個 concrete store，package-surface wording 很容易漂移成 root
  re-export 或 broader architecture claim。
- single `asyncio.Lock` 雖然簡單，但若測試沒有明確覆蓋，實作者可能誤改成未鎖或
  multi-lock 行為。
- patch bump 與 docs update 若不同步，會造成 stable-library / release-facing
  evidence 不一致。

## Rollback Plan

- 以 git revert 回退本 topic 實際變更的 bounded paths：
  `src/async_model_gateway/model_registry/stores/__init__.py`,
  `src/async_model_gateway/model_registry/stores/in_memory.py`,
  `tests/model_registry/stores/test_in_memory.py`,
  `tests/model_registry/stores/test_stores_package_surface.py`,
  `tests/model_registry/test_model_registry_package_surface.py`,
  `README.md`,
  `docs/specs/model-side-boundary.md`,
  `docs/specs/canonical-input-boundary.md`,
  `docs/specs/core-abstractions-boundary.md`,
  `src/async_model_gateway/__version__.py`,
  `pyproject.toml`。
- 若 release metadata 已更新但 implementation 被回退，必須同時回退 patch
  bump 與 related docs wording，避免留下錯誤 release-facing state。
