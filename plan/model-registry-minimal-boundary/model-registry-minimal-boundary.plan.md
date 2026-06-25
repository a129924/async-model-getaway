> Semantic warning: 在 authoring 當下找不到
> `analysis/model-registry-minimal-boundary/requirements.md` 與
> `analysis/model-registry-minimal-boundary/technical-spec.md`。此 plan
> 僅依據 repo exploration 與明確的 topic-repair 要求撰寫。

# model-registry-minimal-boundary

## Goal / Outcome

- 以 canonical 的 `model-registry-minimal-boundary` topic plan、step
  tracker 與 behavior spec，取代已漂移的
  `model-registry-class-first-boundary` topic contract。
- 當此 topic 完成時，repository 可以實作一個最小、async-only、
  class-first 的 `ModelRegistry` boundary；其 root re-export 只有
  `ModelRegistry`，唯一 abstract collaborator 是位於 `ports/` 下的
  `RegistryStore`，而 freshness flow 會受限於已宣告的 artifact paths，
  不會重新打開既有的 `ModelPayloadHasher` contract。

## Scope

- **In scope**:
  - 在 `plan/model-registry-minimal-boundary/` 下新增 canonical topic
    artifacts。
  - 規劃最小 `ModelRegistry` boundary 所需且受限的 implementation、tests
    與 repo-visible 文件更新；範圍限於
    `src/async_model_gateway/model_registry/`、
    `tests/model_registry/`、`README.md`、`docs/architecture.md`、
    `docs/specs/canonical-input-boundary.md`、
    `docs/specs/model-side-boundary.md` 與 `uv.lock`。
  - 將 `model-registry-class-first-boundary` 退役，不再作為 canonical
    topic contract。

- **Out of scope**:
  - 此次 planning repair 中的任何 product-source implementation。
  - 任何 `ResponseCache`、`orchestrator`、`ModelPool`、`ModelGateway`、
    local loader 或 runtime-model 相關工作。
  - 任何重新打開
    `ModelPayloadHasher.hash_model_payload(model_payload: dict[str, JSONLike]) -> str`
    的行為。
  - 任何額外的 abstract collaborator、service/repository layering、
    sync-compatible registry surface，或 multi-concept registry blob
    file。

## Locked Decisions

- `model-registry-minimal-boundary` 是此工作唯一的 canonical topic slug。
  已退役的 `model-registry-class-first-boundary` artifacts 不得再用於
  review、approval、publish 或 implementation routing。
- 此 topic 明確採用 Python planning extension path，並保留 companion
  `*.step.md` 與 `*.spec.md` artifacts。
- D1 verdict: `non-trivial`。此 topic 在 implementation 開始前凍結新的
  async public boundary、精確的 source/test/doc paths，以及跨檔案的
  package split。
- 此 topic 保持 repository 的 async-only 方向。`ModelRegistry` 與
  `RegistryStore` 都維持 async-only；不允許 sync alias、sync fallback
  或 dual API。
- Boundary 維持 class-first。`ModelRegistry` 是 concrete boundary owner；
  此 topic 不採用 function-first registry API，也不採用
  service-plus-repository layering。
- `RegistryStore` 是此 topic 唯一的 abstract collaborator。
- 所有 abstract surfaces 都必須位於
  `src/async_model_gateway/model_registry/ports/*.py`。在此 topic 中，這代表
  `RegistryStore` 必須放在 `ports/` 下，且不得引入其他 ABC / abstract
  type。
- 一旦某個 source file 開始混雜多個 registry concepts，就必須比照
  `model_payload/` 拆成單一概念模組；不得保留肥大的單檔 registry
  implementation。
- Package root `src/async_model_gateway/model_registry/__init__.py`
  只能 re-export `ModelRegistry`。
- `RegistryFreshnessResult` 固定為
  `decision + entry + previous_payload_hash`。
- `RegistryStore` 的 lookup identity 固定為
  `model_name + model_source_kind`。`payload_hash` 在 store lookup 之後才作為
  freshness material 參與判斷，而不是 store lookup key。
- `ModelPayloadHasher.hash_model_payload(...) -> str` 的 signature、owner 與
  hashing semantics 都保持不變。
- Human decision `A` 已鎖定：`uv.lock` 是此 topic 的合法 repo-visible artifact
  path；僅允許承載此 topic implementation 所需的最小 lockfile 變更，不得藉此
  擴張成額外 dependency topic。
- 此 topic 會影響 repo-visible first-read 文字，因此 stable-library
  metadata 於下方宣告。此 topic 不需要 release workflow，也不需要
  VERSION bump。

## Boundaries / Exclusions

- Planning actor 只編輯此 topic repair 的 planning artifacts。
- Implementer 只能修改 `## Artifact Paths` 中明確列出的 implementation、
  test 與 document paths。
- Reviewer 負責獨立的 plan verdict 與後續 implementation review；
  reviewer 不負責撰寫 creator steps，也不負責關閉 human gates。
- Main Agent 在 review 之後負責 routing；routing decisions 不屬於 creator
  的 `Implementation Steps`。
- 此 topic 不會重寫 repo workflow names、status names 或 gate semantics。
- 如果後續工作需要額外 abstract collaborators、cache wiring、
  runtime-model acquisition 或更寬的 model-side architecture，則必須另開
  topic，並回到 `spec-and-plan-finalization`。

## Status / Allowed Transitions

- **Current**: `reviewer-in-progress`
- **Execution model**: follow
  `spec-and-plan-finalization -> implement-plan -> pr-comment -> pr-comment-review-pr-comments-and-fix`；
  由於此 topic 不使用條件式 `release` workflow，因此在 `merged` 停止。
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

Routing notes:

- 獨立 reviewer 工作已完成，且 repo-visible plan-review artifact 已記錄
  `approved` verdict。
- 依 repo contract，`approved` 必須同時具備 repo-visible plan-review
  artifact 的 `approved` verdict 與明確的 repo-visible `human check`。
- 目前 repo-visible `human check` 尚未通過，因此此 topic 尚未進入
  `approved`，且 `spec-and-plan-finalization` 仍未完成。
- 在 `human check` 明確通過之前，不得進入 `implement-plan`、
  `publish-in-progress` 或任何 implementation progress。
- RED test authoring 是 `implement-plan` 內第一個 Python subphase，但此刻尚未開始。
- 任何對 async-only contract、root re-export policy、abstract
  collaborator count、result shape、lookup key 或 artifact paths 的 scope
  變更，都必須回到 `spec-and-plan-finalization`。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/model-registry-minimal-boundary/model-registry-minimal-boundary.plan.md` | Planning actor | 此 topic 的 repo-visible execution contract |
| Topic step tracking | `plan/model-registry-minimal-boundary/model-registry-minimal-boundary.step.md` | Implementer | repo-visible implementer-progress companion artifact |
| Topic behavior spec | `plan/model-registry-minimal-boundary/model-registry-minimal-boundary.spec.md` | Planning actor | 供 TDD 與後續 review 使用的 non-trivial Python behavior contract |
| Plan review artifact | `plan/model-registry-minimal-boundary/model-registry-minimal-boundary.plan-review.json` | Reviewer | repo-visible planning gate verdict |
| RED test artifact | `plan/model-registry-minimal-boundary/model-registry-minimal-boundary.red-tests.yaml` | Implementer | 在 `implement-plan` 期間產出的 repo-visible TDD gate evidence |
| Implementation review artifact | `plan/model-registry-minimal-boundary/model-registry-minimal-boundary.implementation-review.yaml` | Reviewer | repo-visible implementation-review gate evidence |
| Project summary | `README.md` | Implementer | 實作落地後，first-read 文件必須不再把最小 registry boundary 描述成完全不存在 |
| Architecture summary | `docs/architecture.md` | Implementer | 與最小 async-only registry boundary 對齊的 architecture summary |
| Canonical input boundary spec | `docs/specs/canonical-input-boundary.md` | Implementer | 必須描述 `ModelRegistry` 消費 `model_name`、`model_source_kind` 與 `model-payload`，同時維持 hasher ownership 不變的 spec |
| Model side boundary spec | `docs/specs/model-side-boundary.md` | Implementer | 必須準確描述最小 class-first registry owner、async store boundary 與受限 freshness decision 的 spec |
| Dependency lockfile | `uv.lock` | Implementer | 合法的 repo-visible lockfile artifact path；僅允許承載此 topic implementation 所需的最小 dependency resolution 變更 |
| Model registry package root | `src/async_model_gateway/model_registry/__init__.py` | Implementer | 只能 re-export `ModelRegistry` 的 root import surface |
| Model registry boundary owner | `src/async_model_gateway/model_registry/registry.py` | Implementer | 負責 lookup、hashing、decision 與條件式 persistence orchestration 的 async `ModelRegistry` owner |
| Registry entry value object | `src/async_model_gateway/model_registry/entry.py` | Implementer | 單一概念的 concrete registry entry surface |
| Registry freshness policy | `src/async_model_gateway/model_registry/freshness_policy.py` | Implementer | 單一概念的 concrete freshness decision logic |
| Registry freshness result | `src/async_model_gateway/model_registry/freshness_result.py` | Implementer | 固定為 `decision + entry + previous_payload_hash` 的單一概念 result surface |
| Registry ports package root | `src/async_model_gateway/model_registry/ports/__init__.py` | Implementer | 放置 `ports/` 下 abstract collaborators 的 topic-local package surface |
| Registry store port | `src/async_model_gateway/model_registry/ports/store.py` | Implementer | 唯一 abstract collaborator，負責 async store lookup 與 upsert behavior |
| Registry package-surface tests | `tests/model_registry/test_package_surface.py` | Implementer | 驗證 root re-export 與 `ports/` placement boundary 的 pytest coverage |
| Registry boundary tests | `tests/model_registry/test_registry.py` | Implementer | 驗證 lookup、hashing、decision 與條件式 persistence flow 的 async pytest coverage |
| Registry freshness-policy tests | `tests/model_registry/test_freshness_policy.py` | Implementer | 驗證 result shape、key semantics 與 freshness classification behavior 的 pytest coverage |

Artifact path notes:

- `README.md` 與 `uv.lock` 屬於此 topic 範圍；`VERSION` 與
  `.github/copilot-instructions.md` 不在 scope 內。
- `src/async_model_gateway/model_registry/model_payload/__init__.py` 與
  `src/async_model_gateway/model_registry/model_payload/canonical_hash.py`
  可以被檢視，但刻意不列入可修改清單，因為 hasher contract 是 locked，不是
  reopened。
- 請將上述列出的 paths 視為可執行合約。
- 若後續工作偏離這些精確 paths，必須停止並回到
  `spec-and-plan-finalization`。

## Stable library metadata

- `README row`: implementation 落地後，更新 `README.md` 的 repo first-read
  敘述，使最小 registry boundary 不再被描述成完全缺席；此 repo 沒有 package-index
  table row 需要調整。
- `VERSION bump`: no bump。
- `timing`: `publish-in-progress`。
- `rationale`: `README.md` 是 repo 的 first-read surface，實作後必須與已落地
  boundary 一致，但此 topic 不引入 release work。

## Implementation Steps

1. 在 `tests/model_registry/test_package_surface.py`、
   `tests/model_registry/test_registry.py` 與
   `tests/model_registry/test_freshness_policy.py` 新增 async RED coverage，
   並記錄
   `plan/model-registry-minimal-boundary/model-registry-minimal-boundary.red-tests.yaml`，
   讓測試鎖定 async-only boundary、root re-export policy、僅限 `ports/`
   的 abstract surface、`model_name + model_source_kind` lookup identity、
   未變更的 hasher contract，以及固定的
   `RegistryFreshnessResult` shape。
2. 新增 `src/async_model_gateway/model_registry/registry.py`、
   `src/async_model_gateway/model_registry/entry.py`、
   `src/async_model_gateway/model_registry/freshness_policy.py`、
   `src/async_model_gateway/model_registry/freshness_result.py`、
   `src/async_model_gateway/model_registry/ports/__init__.py`、
   `src/async_model_gateway/model_registry/ports/store.py`，並更新
   `src/async_model_gateway/model_registry/__init__.py`，使 source layout
   維持一檔一概念、`RegistryStore` 仍是唯一 abstract collaborator、
   `ModelRegistry` 仍是唯一 root re-export，且 `ModelPayloadHasher`
   以原樣被使用。
3. 更新 `README.md`、`docs/architecture.md`、
   `docs/specs/canonical-input-boundary.md` 與
   `docs/specs/model-side-boundary.md`，使 repo-visible wording 正確反映最小
   async-only `ModelRegistry` boundary、`ports/` store contract，以及受限的
   freshness flow，且不擴張到 cache、gateway、pool 或 orchestrator
   implementation work。
4. 執行
   `uv run pytest tests/model_registry/test_package_surface.py tests/model_registry/test_registry.py tests/model_registry/test_freshness_policy.py tests/model_registry/model_payload/test_canonical_hash.py tests/test_package_entrypoint.py tests/test_local_path_guard.py -v`、
   `uv run ruff check README.md docs src tests plan/model-registry-minimal-boundary`
   與 `uv run pyright`，然後再更新
   `plan/model-registry-minimal-boundary/model-registry-minimal-boundary.step.md`
   以反映 implementer 擁有的工作已完成，之後才交給 reviewer 檢查。

## Validation / Acceptance Checks

- Canonical topic-plan sections、status names、transitions 與 reviewer
  handoff shape 仍需與 repo workflow contracts 相容。
- `model-registry-minimal-boundary.spec.md` 必須存在，因為此 topic 已鎖定為
  `non-trivial`。
- `model-registry-minimal-boundary.step.md` 必須鏡像所有編號的 implementation
  steps，且在目前階段只允許 `plan-authoring` 與 `plan-review` 標記完成；其餘
  workflow stages 必須維持未完成，直到 `human check` 與 implementation
  work 真正發生。
- 此 topic artifact set 不得預填 reviewer verdict 以外的 `approved` 狀態、
  不得預填 `human check`，也不得預填 `implement-plan` completion。
- Validation 必須證明 `ModelRegistry` 與 `RegistryStore` 為 async-only，
  同時 `RegistryEntry`、`RegistryFreshnessPolicy`、
  `RegistryFreshnessResult` 與 `ModelPayloadHasher` 仍是同步的 value 或
  policy surfaces。
- Validation 必須證明 package root 只 re-export `ModelRegistry`，所有
  abstract surfaces 都位於 `ports/*.py`，且沒有引入 multi-concept
  registry blob。
- Validation 必須證明 `RegistryFreshnessResult` 只包含
  `decision`、`entry` 與 `previous_payload_hash`。
- Validation 必須證明 `RegistryStore` lookup 只使用
  `model_name + model_source_kind`，而 `payload_hash` 是在 lookup 之後，透過
  未變更的 `ModelPayloadHasher.hash_model_payload(...) -> str` contract
  導出。
- Repo-visible docs 必須與新的最小 boundary 對齊，且不得聲稱 release
  work、VERSION 變更或更廣泛的 model-side implementation 已完成。

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

- No release workflow required.
- Merge 後即停止；不得在此 topic 下變更 `VERSION`、tags 或 release state。

## Open Questions / Unresolved Items

- None.

## Current Context

- `src/async_model_gateway/model_registry/` 目前只包含既有的
  `model_payload` hashing subpackage 與空的 package root；尚無 concrete
  `ModelRegistry`、store port 或 freshness decision surface。
- `ModelPayloadHasher` 已存在於
  `async_model_gateway.model_registry.model_payload`，並持有已鎖定的
  `hash_model_payload(...) -> str` contract。
- `README.md`、`docs/architecture.md` 與
  `docs/specs/model-side-boundary.md` 仍將最小 registry boundary 描述為尚未實作。
- 已退役的 `model-registry-class-first-boundary` topic artifacts 在 slug、
  sync/async assumptions、root re-exports 與 file-splitting decisions 上都已漂移，
  因此此 topic 取代它們，而不是延伸它們。

## Requirements

1. `ModelRegistry` 必須公開一個 async-only public operation，接受
   `model_name`、`model_source_kind` 與 `model_payload`，透過既有
   `ModelPayloadHasher` 導出 payload hash，並回傳
   `RegistryFreshnessResult`。
2. `RegistryStore` 必須是唯一 abstract collaborator，且必須提供以
   `model_name + model_source_kind` 為 key 的 async lookup 與 async upsert
   operations。
3. `RegistryFreshnessResult` 必須只包含 `decision`、`entry` 與
   `previous_payload_hash`。
4. Source layout 必須維持每個 registry concept 一個檔案，且所有 abstract
   types 都必須位於 `ports/*.py`。
5. `src/async_model_gateway/model_registry/__init__.py` 只能 re-export
   `ModelRegistry`。
6. 不合法的 `model_payload` 內容必須持續透過既有 hasher contract raise
   `TypeError`，且此 topic 不得改動
   `ModelPayloadHasher.hash_model_payload(...) -> str`。
7. Implementation 必須受限於此 plan 所列的精確 artifact paths。

## Decisions

- Async-planning status: triggered。trigger evidence 為：此 topic 已鎖定為
  async-only `ModelRegistry` boundary，且 `RegistryStore` lookup 與 upsert
  operations 為 async，同時 cancellation 與 failure behavior 也必須在實作前凍結。
- Module/package placement：在
  `src/async_model_gateway/model_registry/` 下新增 `registry.py`、
  `entry.py`、`freshness_policy.py`、`freshness_result.py` 與
  `ports/store.py`；`ModelPayloadHasher` 則保留在既有的
  `model_payload` subpackage。
- New public API: yes。新增
  `class ModelRegistry` 作為唯一的 root re-export，其 public method 為
  `async def resolve_freshness(self, *, model_name: str, model_source_kind: Literal["local", "remote"], model_payload: dict[str, JSONLike]) -> RegistryFreshnessResult`。
- Interface changes: yes。`async_model_gateway.model_registry` 會成為只對
  `ModelRegistry` 開放的真實 root public surface，而 `RegistryStore`、
  `RegistryEntry`、`RegistryFreshnessPolicy` 與
  `RegistryFreshnessResult` 仍只從各自定義的 submodules 對外公開。
- Breaking changes allowed: no。此 topic 只新增新的 registry boundary 與
  doc updates，不會重新打開既有 hasher contract。
- New dependencies: no。沿用 `pyproject.toml` 已宣告的
  `pytest-asyncio`、`ruff` 與 `pyright` toolchain。
- Error handling strategy：傳播來自
  `ModelPayloadHasher.hash_model_payload(...)` 的 `TypeError`；store lookup /
  upsert failures 也以原樣向外傳播；不得吞掉 `asyncio.CancelledError`；
  第一版不得創造新的 exception taxonomy。
- Typing strategy：在 repository strict baseline 下維持完整 typing；
  重用 `JSONLike`；對 `model_source_kind` 使用
  `Literal["local", "remote"]`；讓 `RegistryStore` 維持為具有明確 async
  methods 的 abstract surface；避免 `Any`。

### Async boundary decision

- `ModelRegistry.resolve_freshness(...)` 是 async-only。
- `RegistryStore` methods 是 async-only。
- `RegistryEntry`、`RegistryFreshnessPolicy`、
  `RegistryFreshnessResult` 與 `ModelPayloadHasher` 仍是用於 async flow
  內部的同步 value 或 policy surfaces。
- 此 topic 不會新增 background tasks、workers 或 sync-compatible
  wrappers。

### Resource lifecycle decision

- `ModelRegistry` 接收一個 ready-to-use 的 `RegistryStore` collaborator，
  自身不建立、不擁有、也不關閉 store-backed resources。
- `ModelRegistry` 可以接受選用的 injected concrete
  `RegistryFreshnessPolicy` 與 `ModelPayloadHasher` helpers，但這些 helpers
  在此 topic 內仍是同步且不可關閉的。
- `ModelRegistry` 不會凍結 connection pool、session lifecycle 或
  context-manager policy；這些仍屬於 store implementation 的責任。

### Concurrency model

- 每次 `resolve_freshness(...)` 呼叫只進行一次 async lookup，接著做同步的
  hash 與 decision work，最後最多進行一次 async upsert。
- 每次呼叫的 flow 都是循序的。此 topic 不會新增 fan-out、`gather`、
  batching、streaming 或 speculative writes。
- 因為此 topic 不引入內部 concurrency，所以不存在 grouped-failure
  surface。

### Failure model

- 不合法的 payload data 必須在任何 store write 開始前，透過既有 hasher path
  以 `TypeError` fail closed。
- Store lookup 與 store upsert failures 都必須以原樣向 caller 傳播。
- 如果 cancellation 發生在 awaited store I/O 期間，則 cancellation 必須以
  原樣傳播，`ModelRegistry` 不得把它轉譯成 domain-specific error。
- 由於沒有內部 concurrency，此 topic 不定義 aggregate-error handling。

### Cancellation / timeout policy

- Timeout ownership 屬於 caller 或外層 orchestration layer；
  `ModelRegistry` 不引入內部 timeout 或 retry loop。
- Cancellation 由 caller 擁有，且必須以原樣傳播。
- 若 cancellation 發生在條件式 upsert 開始之前，`ModelRegistry`
  不得做 best-effort write。
- 若 cancellation 中斷 awaited upsert，`ModelRegistry` 仍必須以原樣傳播
  cancellation；backend atomicity 與 partial-write semantics 仍屬於 store
  implementation 的責任。

### Validation plan

- Async pytest coverage 必須驗證 awaited lookup 與條件式 awaited upsert
  behavior，包括 `unchanged` 時的 no-write path。
- Package-surface tests 必須驗證 root package 只 re-export `ModelRegistry`，
  且 `RegistryStore` 維持位於 `ports/`。
- Freshness-policy tests 必須獨立於任何 backend implementation，驗證固定的
  result shape 與 `model_name + model_source_kind` lookup-key decision。
- Validation commands 維持為 `uv run pytest ...`、`uv run ruff check ...`
  與 `uv run pyright`。

### Handoff notes for the implementer

- 不得把既有 `ModelPayloadHasher` 轉成 async。
- 不得從 `model_registry/__init__.py` re-export `RegistryStore`、
  `RegistryEntry`、`RegistryFreshnessPolicy` 或
  `RegistryFreshnessResult`。
- 如果某個 module 開始混雜 registry owner、abstract port、value object
  與 result concerns，必須立即拆分，而不是保留方便但肥大的 blob file。
- Store lookup 必須只以 `model_name + model_source_kind` 為 key；只有在
  lookup 回來之後才能比較 hashed payload。

## Public Contract / API Changes

- `async_model_gateway.model_registry.ModelRegistry`
  - Constructor:
    `def __init__(self, store: RegistryStore, *, freshness_policy: RegistryFreshnessPolicy | None = None, payload_hasher: ModelPayloadHasher | None = None) -> None`
  - Public method:
    `async def resolve_freshness(self, *, model_name: str, model_source_kind: Literal["local", "remote"], model_payload: dict[str, JSONLike]) -> RegistryFreshnessResult`
  - Behavior contract:
    先以 `model_name + model_source_kind` await store lookup，再透過既有
    `ModelPayloadHasher` 對 candidate payload 做 hash，建立 candidate
    `RegistryEntry`，評估 freshness，只在 `first-seen` 或 `changed` 時 await
    store upsert，最後回傳 `RegistryFreshnessResult`。
- `async_model_gateway.model_registry.ports.store.RegistryStore`
  - Abstract methods:
    `async def get_entry(self, *, model_name: str, model_source_kind: Literal["local", "remote"]) -> RegistryEntry | None`
    and
    `async def upsert_entry(self, entry: RegistryEntry) -> None`
  - Contract:
    唯一的 abstract collaborator；此 topic 不定義任何 backend、session 或
    transaction policy。
- `async_model_gateway.model_registry.entry.RegistryEntry`
  - Concrete value surface，包含
    `model_name: str`、`model_source_kind: Literal["local", "remote"]` 與
    `payload_hash: str`。
- `async_model_gateway.model_registry.freshness_policy.RegistryFreshnessPolicy`
  - Public method:
    `def evaluate(self, *, candidate_entry: RegistryEntry, stored_entry: RegistryEntry | None) -> RegistryFreshnessResult`
  - Contract:
    當 stored entry 缺席時回傳 `decision="first-seen"`；
    當 payload hash 相同時回傳 `decision="unchanged"`；否則回傳
    `decision="changed"`。
- `async_model_gateway.model_registry.freshness_result.RegistryFreshnessResult`
  - Concrete result surface 固定為
    `decision: Literal["first-seen", "unchanged", "changed"]`、
    `entry: RegistryEntry` 與 `previous_payload_hash: str | None`。
- Backward compatibility:
  此 topic 會新增 registry boundary，但不會變更既有的
  `ModelPayloadHasher.hash_model_payload(...) -> str` contract。

## Affected Files / Modules

Likely affected files:
- `README.md`
- `docs/architecture.md`
- `docs/specs/canonical-input-boundary.md`
- `docs/specs/model-side-boundary.md`
- `src/async_model_gateway/model_registry/__init__.py`
- `src/async_model_gateway/model_registry/registry.py`
- `src/async_model_gateway/model_registry/entry.py`
- `src/async_model_gateway/model_registry/freshness_policy.py`
- `src/async_model_gateway/model_registry/freshness_result.py`
- `src/async_model_gateway/model_registry/ports/__init__.py`
- `src/async_model_gateway/model_registry/ports/store.py`
- `tests/model_registry/test_package_surface.py`
- `tests/model_registry/test_registry.py`
- `tests/model_registry/test_freshness_policy.py`

Candidate files to inspect:
- `src/async_model_gateway/model_registry/model_payload/__init__.py`
- `src/async_model_gateway/model_registry/model_payload/canonical_hash.py`
- `pyproject.toml`

## Test Plan

Test files:
- `tests/model_registry/test_package_surface.py`
- `tests/model_registry/test_registry.py`
- `tests/model_registry/test_freshness_policy.py`

Test cases:
- Happy path:
  `tests/model_registry/test_registry.py` 驗證 async lookup miss 會得到
  `decision="first-seen"`、await 一次 upsert，且回傳結果的
  `previous_payload_hash = None`。
- Invalid input:
  `tests/model_registry/test_registry.py` 驗證不合法的 `model_payload` 內容
  仍會透過未變更的 hasher path raise `TypeError`，且不會進行 awaited
  upsert。
- Edge case:
  `tests/model_registry/test_freshness_policy.py` 驗證相同 payload hash 仍為
  `unchanged`、不同 payload hash 變成 `changed`，且結果始終只包含
  `decision`、`entry` 與 `previous_payload_hash`。
- Regression:
  `tests/model_registry/test_package_surface.py` 驗證
  `model_registry/__init__.py` 只 re-export `ModelRegistry`，且
  `RegistryStore` 仍位於 `ports/`。
- Backward compatibility:
  `tests/model_registry/test_registry.py` 驗證 lookup identity 只由
  `model_name + model_source_kind` 構成，而 payload hash 仍來自未變更的
  `ModelPayloadHasher.hash_model_payload(...) -> str` contract。

## Validation Commands

```text
uv run pytest tests/model_registry/test_package_surface.py tests/model_registry/test_registry.py tests/model_registry/test_freshness_policy.py tests/model_registry/model_payload/test_canonical_hash.py tests/test_package_entrypoint.py tests/test_local_path_guard.py -v
uv run ruff check README.md docs src tests plan/model-registry-minimal-boundary
uv run pyright
```

## Risks

- Async-only 決策可能在 implementation 期間漂移，如果 implementer 為了方便在
  async boundary 旁邊保留 sync helpers。
- 檔案拆分規則可能回退，如果 `RegistryFreshnessPolicy` 與
  `RegistryFreshnessResult` 又被收攏成單一 multi-concept module。
- README / 文件更新可能偏離已鎖定的 implementation boundary，並意外誇大更廣的
  model-side 完成度。

## Rollback Plan

- 只回滾此 topic 所宣告 artifact paths 內的 implementation changes：
  `README.md`、`docs/architecture.md`、
  `docs/specs/canonical-input-boundary.md`、
  `docs/specs/model-side-boundary.md`、
  `src/async_model_gateway/model_registry/__init__.py`、
  `src/async_model_gateway/model_registry/registry.py`、
  `src/async_model_gateway/model_registry/entry.py`、
  `src/async_model_gateway/model_registry/freshness_policy.py`、
  `src/async_model_gateway/model_registry/freshness_result.py`、
  `src/async_model_gateway/model_registry/ports/__init__.py`、
  `src/async_model_gateway/model_registry/ports/store.py`、
  `tests/model_registry/test_package_surface.py`、
  `tests/model_registry/test_registry.py` 與
  `tests/model_registry/test_freshness_policy.py`。
- 即使 implementation 被回滾，也要保留
  `plan/model-registry-minimal-boundary/` 作為此 topic 的 planning history；
  不得恢復已退役的 `model-registry-class-first-boundary` topic 作為 canonical。
