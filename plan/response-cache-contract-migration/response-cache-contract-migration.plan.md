# response-cache-contract-migration

## Goal / Outcome

將本 topic 的六份 dev-only planning 來源完整遷移為 feature worktree 的唯一權威
planning surface，並在新的權威位置重新建立後續 gate 順序。完成時，strict analysis、
topic plan、Python spec 與 fresh plan review 都只從 feature worktree 的已登錄相對路徑
讀取；既有 feature 歷史證據仍保持原位且不可變更。

## Scope

- **In scope**：下列六份 dev-only planning artifacts 的 SHA-256-preserving move protocol、
  feature-authoritative target paths、fresh independent plan review 重新定址，以及後續
  fresh human check、forward preflight、step tracker 與 implementation review 的 gate
  重建順序；以及不改寫 immutable historical `human-check.json` 下的 Draft PR
  pre-commit 相容 gate；以及本 PR 全部五個已列明 review threads 的唯一修正集合：
  `tests/response_cache/test_entry.py`、`tests/response_cache/test_key_factory.py`、
  `tests/response_cache/test_canonical_feature_hasher.py`、
  `tests/response_cache/test_in_memory_store.py` 的 expected-failure import hygiene，及
  `.github/workflows/ci.yml` 的唯一 Run pre-commit selector。目標 response-cache contract 的
  行為仍由 strict analysis 與 Python spec 凍結。
- **Out of scope**：此 planning rework 不搬移檔案、不修改 source、README、architecture docs
  或既有 feature evidence；除上述四個精確測試檔的五個 PR-comment hygiene 修正與已登錄的
  `.github/workflows/ci.yml` Run pre-commit invocation 外，不修改其他 tests、CI workflow、
  hook configuration 或 validation 設定；不執行 RED、其他實作、PR、merge 或 release；不新建
  orchestrator、persistence、settings、backend selection、timeout、retry、background task、queue、
  worker、batching 或 fan-out。
- **Analysis routing**：strict mode。`analysis/response-cache-contract-migration/technical-spec.md`
  是 execution-facing source of truth；`analysis/response-cache-contract-migration/requirements.md`
  是 business guardrail；`analysis/response-cache-contract-migration/canonical-reconciliation.md`
  是唯一 current/target/migration/compatibility row authority。無 human override。

## Locked Decisions

- 本題為 D1 `non-trivial` Python retrofit；本計畫的 Python supplement 與
  `response-cache-contract-migration.spec.md` 共同凍結實作契約，但本次只修訂 planning
  artifact。
- **遷移集合恰為六份**：requirements、technical-spec、canonical-reconciliation、topic plan、
  Python spec、plan-review。每一份都必須從 dev 的同名 repo-relative source 移到下方表列的
  feature target；完成後 dev 不得留有該 topic 的任何一份 planning source。
- **逐檔 SHA-preservation / move protocol**：Worktree-manager migration lane 在任何
  feature target 寫入前，對六個 final dev source bytes 逐一計算 SHA-256；寫入相同相對路徑
  的 feature target 後，逐一重算並要求 digest 相同；確認六對均相同、六個 feature targets
  均可讀，才以可復原且逐一確認的移除操作清除六個 dev sources。lane 的交接紀錄必須逐檔列出
  source relative path、target relative path、source digest、target digest、match 與
  source-removal result。任何缺檔、digest 不符、target 已有不同內容或 source-removal
  失敗都停止，保持原狀或回復尚未完成的單檔操作，並回到 planning rework；不得以 copy、
  sync、glob、目錄級猜測或 chat 聲明取代此 protocol。
- 現有 dev `plan-review.json` 也屬於六份必搬來源：先以相同 bytes 交付 feature target
  並完成 digest check，隨即標為 superseded、不可作為 approval。獨立 Reviewer 必須在相同
  feature path 針對已遷移 plan 產生 fresh verdict；舊 verdict 不保留 gate authority。
- feature 既存的三份歷史 evidence：`human-check.json`、`worktree-preflight.yaml`、
  `red-tests.yaml` 均在 move snapshot 中以 before/after SHA-256 記錄為 immutable historical
  candidates。它們不在六份 move 集合，不得搬、複製、修復、重新建立或升格為本 revision 的
  fresh / forward evidence。`human-check.json` 其後的 Human-authorized update 必須保留為
  ledger 的獨立 post-transfer event；其 current digest 是 Draft PR 的 immutable
  compatibility anchor，但不是 fresh gate。
- Audit baseline 曾確認 `fresh-human-check.json` 與 `forward-preflight.yaml` 不存在；它們後續
  僅能由各自 owner 按序建立。historical evidence 不能補足它們，且它們已完成的
  implementation-entry authority 不會被本次 post-implementation governance rework 改寫。
- 新的 forward authority 順序固定為：successful six-file move -> fresh independent
  feature plan review -> Human-created fresh human check -> Worktree-manager-created forward
  preflight -> read-only historical candidate verification -> Implementer-created absent step
  tracker -> independent implementation review。每一項都在下列 feature-authoritative path
  建立；較晚的 evidence 不得回填或替代較早 gate。
- 目標 implementation contract 不變：`ResponseCache` 是兩個 async operation 的唯一 root
  facade；`CacheKey` 是唯一 identity authority；complete record 的 stale cleanup 使用 atomic
  compare-delete；context 不進入 identity、record、codec payload 或 metadata；known operational
  failures 只依 technical spec 的 closed outcomes 翻譯，cancellation 與 defects 原樣傳播；
  temporary legacy surface 僅能位於 `compat.py`。
- 本 topic 不宣告 stable-library release intent、VERSION bump 或 release workflow。README 與
  docs 僅是之後已核准 implementation 的同步範圍，本 planning rework 不修改它們。
- **Draft PR EOF / historical-evidence compatibility**：historical
  `response-cache-contract-migration.human-check.json` 的 post-transfer immutable anchor
  是 SHA-256 `f6ec59dbf3f5df4ba42359b9978c31bebd4bbf30b1645146ba1a4841508d417b`，且末位元組為
  `0x7d`（無 final LF）。它仍為 non-gating historical evidence，不能替代 fresh human check、
  review 或 merge gate。Draft PR 不得在實際 feature worktree 對此檔執行未排除的
  `pre-commit run --all-files`，因為 `end-of-file-fixer` 必然改寫該 anchor；這不是可接受的
  validation side effect。
- **相容 gate 的唯一形式**：Draft PR preflight 必須執行
  `uv run pre-commit run --files $(git ls-files -co --exclude-standard | rg -v '^plan/response-cache-contract-migration/response-cache-contract-migration\.human-check\.json$')`。
  這是目前已驗證可執行的 `pre-commit --files` 介面，而非不受支援的 `--exclude` CLI；它也不是
  `SKIP`、停用 hook 或廣泛略過 validation。`git ls-files -co --exclude-standard` 列出所有
  non-ignored tracked / untracked candidates，`rg -v` 唯一移除完整 regex 鎖定的 historical
  human-check path；所有 configured hooks（包含 `end-of-file-fixer`）仍對其餘候選檔執行。
  preflight schema 必須記錄 literal command、candidate-selection command、literal excluded-path
  regex、`skip_used: false`、`hook_overrides_used: false`、每個 hook 的 pass result，以及
  historical path 的 pre/post digest、terminal byte 與 working-tree-diff result。任何更寬的
  檔案選取排除、`SKIP`、hook/config 改寫、或對 historical file 補 LF 都是 scope drift。
- **CI workflow contract**：在 fresh plan review 完成後，`.github/workflows/ci.yml` 的
  唯一允許變更是 Run pre-commit 的 `run:` 值，且必須逐字為上段 exact supported selector；
  不得使用 `SKIP`、任何 hook override、`--exclude`、更寬的檔案排除、hook/config 改寫，
  或改寫／修復／補 LF 至 historical `human-check.json`。CI 執行後仍必須證明該 historical
  path 的 SHA-256 為 `f6ec59dbf3f5df4ba42359b9978c31bebd4bbf30b1645146ba1a4841508d417b`、
  末位元組為 `0x7d`，且無 working-tree diff。
- **PR-comment test-hygiene contract**：在 fresh plan review 完成後，Implementer 可處理全部且
  僅限下列五個已授權 threads。`test_entry.py` 的 expected `ModuleNotFoundError` import
  刪除不可能執行的 assertion、保留 ordinary import 並以 `# noqa: F401` 局部抑制，且為兩個
  test-only `type: ignore` 各補一句精確 inline reason；`test_key_factory.py` 與
  `test_in_memory_store.py` 各刪除一個 expected-failure import 後不可達的 assertion，並在
  保留 import 加上 `# noqa: F401`；`test_canonical_feature_hasher.py` 對兩個 expected-failure
  imports 刪除不可達 assertions，並各以 `# noqa: F401` 局部抑制。這五個 imports 仍必須是
  ordinary imports：不得加入 dynamic module loading、`importlib`、loader、`exec`、`eval`、
  `runpy` 或 `__import__`，不得改變測試的 expected exception、assertion 語意或 production code。
- 本次 plan bytes 已改變，現有 `plan-review.json`、Draft PR human check、code review 與
  Draft PR preflight 僅是前一 plan revision 的歷史 evidence，不能核准或發佈此 revision。
  Reviewer 必須先在 declared `plan-review.json` path 產生 fresh independent verdict；其 approved
  verdict 後，後續 Human / Reviewer / Main Agent gates 必須依既有順序為本 revision 重建，且
  Planning actor 不得改寫任何 evidence。
- 此 post-implementation governance rework 不改變已核准的 source/test/doc contract，亦不
  重開已完成的 implementation。它只要求 fresh Plan-Reviewer 核准此 Draft PR gate contract；
  existing code-review conclusion 必須由 Reviewer 寫入 declared `code-review.yaml` 後才能作為
  Draft PR preflight 的前置條件。既有 fresh human check 維持其已完成的 implementation-entry
  authority，不能被改寫或升格為 Draft PR gate。
- 本 revision 的 fresh Plan-Reviewer `approved` 後，Human 必須另行建立
  `draft-pr-human-check.json`，明確清除本 revision 的 `publish-in-progress` gate，並記錄當前
  reviewed plan SHA-256。此 gate 不能由 existing fresh human check、historical human check、
  code review、pre-commit 或 chat 取代，且 Planning actor 不得預填。

## Boundaries / Exclusions

- Planning actor 只可修訂本 topic plan 與已登錄的 transfer-handoff ledger；不得執行 move
  protocol、寫入 reviewer/human/implementer evidence 或修改任何其他檔案。
- Worktree-manager migration lane 唯一負責六份 planning artifacts 的 move / digest protocol；
  該 lane 也在 fresh human check 後建立 forward preflight，但不得建立 reviewer、human 或
  implementer-owned evidence。
- Reviewer 只在 feature-authoritative `plan-review.json` 產生 fresh independent verdict，並在
  step tracker complete 後產生 implementation review；不實作、不建立 tracker、不修改歷史
  evidence。Reviewer 也獨立產生 code-review verdict；Human 單獨建立 fresh human check、
  Draft PR human check 與 human merge。
- Implementer 只在全部較早 gates 成功後，於 feature worktree 建立尚不存在的 step tracker，
  並依核准計畫執行後續 source/test/doc work；不得將 existing RED candidate 偽稱為新做的 RED。
- 未登錄的 planning、source、test、doc、legacy import 或 gate artifact 都必須回到
  `spec-and-plan-finalization`，不能由任一 actor 自行擴張。
- Main Agent 只在 independent code-review 已核准後建立 Draft PR preflight evidence；不得改寫
  historical file、不得以 `SKIP` 略過 hook，也不得把 side-effect 後再還原當作通過。
- Implementer 在 fresh plan review 與既有後續 gate 均符合後，只可依 Artifact Paths 的 CI
  workflow contract 修改 `.github/workflows/ci.yml` 的單一 Run pre-commit invocation；不得
  觸及任何 historical evidence、其他 workflow step、hook configuration 或 source/test/doc。
- Implementer 在同一 fresh-gate 順序後，只可依 PR-comment test-hygiene contract 修改四個
  精確 tests；不得把已授權的 ordinary imports 換成 dynamic loading，不得修改其他測試、production
  source、historical evidence 或已完成 implementation evidence。

## Status / Allowed Transitions

- **Current**：`review-ready`，僅等待本 revision（Draft PR EOF compatibility、全部五個已列明
  PR-comment test-hygiene threads、及 CI selector）的 fresh Plan-Reviewer verdict。已完成的
  implementation 不會由此 planning-only rework 重做；fresh plan review 後，Human 必須清除
  declared Draft PR human check，topic 才回到
  `publish-in-progress`；接著仍必須有 declared `code-review.yaml` 的 Reviewer `approved`
  verdict，再由 Draft PR preflight 決定是否可進入 `pr-open`。既有 dev review、已搬遷的舊
  review、Reviewer 的 needs-rework 覆寫前身，以及任何 feature historical evidence 都不能使
  topic `approved`。
- **Execution model**：原 feature-authoritative review -> explicit human check -> forward
  preflight -> `implement-plan` 順序已完成並保留其 implementation-entry authority。本次
  post-implementation governance rework 從 `review-ready` 進入 fresh plan review，再進入新的
  Draft PR human check，然後回到 `publish-in-progress` 的 code-review / Draft PR preflight；無
  release workflow，終點為 `merged`。
- **Allowed transitions**：
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
- **Authority-migration routing**：Worktree-manager 完成六份逐檔 digest match 並確認 dev source
  removal 後，Planning actor 將 `creator-in-progress` -> `review-ready`。Reviewer 在 feature
  target 的 plan review artifact 產生 JSON-only fresh verdict；只有 `approved` verdict 加上
  feature fresh human check 才能形成 canonical `approved`。若 verdict `needs-rework`，只能走
  `needs-rework` -> `creator-in-progress`；重修後再執行新的 feature re-review。
- **Forward / implementation routing**：approved review -> fresh human check -> forward preflight
  是不可跳過的順序。forward preflight passed 才授權 read-only 檢查 historical candidates 與
  建立 absent tracker；tracker 的所有 implementation entries truthfully complete 後，Reviewer
  才能寫 implementation-review YAML。implementation review 不能證明 plan review 或 human
  check，historical RED 亦不能證明任何 fresh gate。
- `pr-open` -> `merged` 仍需要 feature `human-merge.json` 的 explicit Human gate；不得由
  reviewer silence、chat、歷史檔案或無 release intent 推論。
- **Draft PR routing**：fresh Plan-Reviewer 先核准本相容 contract；Human 接著在 declared
  `draft-pr-human-check.json` 寫入 current-plan-bound `approved` / `cleared` decision，才可回到
  `publish-in-progress`。Reviewer 必須在 declared `code-review.yaml` 寫入 `approved` verdict，
  然後 Main Agent 才可建立 declared `draft-pr-preflight.yaml`。preflight 必須記錄「exact supported
  files command、candidate-selection command、single literal excluded-path regex、no SKIP、no hook
  override、all selected-file hooks passed、historical digest/terminal byte pre/post match、historical
  path 無 working-tree diff」；只有這些條件皆成立時，才可從 `publish-in-progress` 進入 `pr-open`。
  未排除 historical path 的檔案選取造成 EOF mutation、Draft PR human-check 或 code-review artifact
  缺失或非 approved、任一 digest/terminal-byte 不符、任何 hook failure 或 preflight 缺失，都保持
  `publish-in-progress` 並回到此 planning rework；不得開 Draft PR。

## Artifact Paths

此 register 是 closed executable contract。worktree selector 一律以 branch 與 repo-relative
path 表達，不以本機絕對路徑表達。

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Business baseline | `analysis/response-cache-contract-migration/requirements.md` | Worktree-manager migration lane | Dev source -> feature-authoritative target；strict business guardrail。 |
| Technical baseline | `analysis/response-cache-contract-migration/technical-spec.md` | Worktree-manager migration lane | Dev source -> feature-authoritative target；strict execution contract。 |
| Reconciliation baseline | `analysis/response-cache-contract-migration/canonical-reconciliation.md` | Worktree-manager migration lane | Dev source -> feature-authoritative target；mandatory mapping authority。 |
| Topic plan | `plan/response-cache-contract-migration/response-cache-contract-migration.plan.md` | Worktree-manager migration lane, then Planning actor | Dev source -> feature-authoritative target；repo-visible execution contract；本次 planning rework 僅修訂此 plan，既有 ledger 與所有 evidence 保持不變。 |
| Python specification | `plan/response-cache-contract-migration/response-cache-contract-migration.spec.md` | Worktree-manager migration lane | Dev source -> feature-authoritative target；non-trivial behavior contract。 |
| Plan review | `plan/response-cache-contract-migration/response-cache-contract-migration.plan-review.json` | Worktree-manager migration lane, then Reviewer | Dev source -> feature target with digest preservation; transferred verdict is superseded, then Reviewer replaces it with the fresh independent feature-authoritative JSON verdict. |
| Transfer handoff ledger | `plan/response-cache-contract-migration/response-cache-contract-migration.transfer-handoff.yaml` | Worktree-manager migration lane evidence, recorded by Planning actor | Completed six-file source/target digest and removal ledger, plus historical before/after digest record and explicitly classified post-transfer events; it is the only migration-preservation authority. |
| Historical human check | `plan/response-cache-contract-migration/response-cache-contract-migration.human-check.json` | Human | Immutable at the move snapshot; its later Human-authorized post-transfer update is recorded in the transfer ledger. It never satisfies a fresh gate. |
| Historical worktree preflight | `plan/response-cache-contract-migration/response-cache-contract-migration.worktree-preflight.yaml` | Historical Worktree-manager lane | Existing feature-only immutable historical evidence; never move or modify; old human-check reference has no fresh authority. |
| Historical RED evidence | `plan/response-cache-contract-migration/response-cache-contract-migration.red-tests.yaml` | Implementer | Existing feature-only immutable historical evidence; never move, modify, recreate, or promote. |
| Fresh human check | `plan/response-cache-contract-migration/response-cache-contract-migration.fresh-human-check.json` | Human | Feature-authoritative completed implementation-entry gate; never rewrite, reclassify, or use as Draft PR authority. |
| Forward preflight | `plan/response-cache-contract-migration/response-cache-contract-migration.forward-preflight.yaml` | Worktree-manager lane | Feature-authoritative completed implementation-entry gate; binds fresh check, moved-plan digest and immutable historical-preflight digest, but does not substitute for Draft PR preflight. |
| Step tracking | `plan/response-cache-contract-migration/response-cache-contract-migration.step.md` | Implementer | Feature-authoritative completed implementation progress; never copied from historical evidence or rewritten by this governance rework. |
| Implementation review | `plan/response-cache-contract-migration/response-cache-contract-migration.implementation-review.yaml` | Reviewer | Feature-authoritative completed implementation-conformance evidence; Planning actor leaves it untouched. |
| Code review | `plan/response-cache-contract-migration/response-cache-contract-migration.code-review.yaml` | Reviewer | Independent implementation quality/boundary verdict required before Draft PR preflight; Planning actor never pre-fills it. |
| Draft PR human check | `plan/response-cache-contract-migration/response-cache-contract-migration.draft-pr-human-check.json` | Human | Create only after this revision's fresh approved plan review; binds the reviewed current plan SHA-256 and explicitly clears `publish-in-progress` before code-review/preflight can authorize `pr-open`. |
| Draft PR preflight | `plan/response-cache-contract-migration/response-cache-contract-migration.draft-pr-preflight.yaml` | Main Agent | Create only after approved code review; records the exact supported no-SKIP `pre-commit --files` command, its `git ls-files` / `rg -v` selection contract, per-hook result, and historical human-check pre/post byte proof that authorizes `publish-in-progress` -> `pr-open`. |
| Human merge | `plan/response-cache-contract-migration/response-cache-contract-migration.human-merge.json` | Human | Feature-authoritative explicit merge gate after PR comments are clear. |
| CI workflow | `.github/workflows/ci.yml` | Implementer | The sole CI artifact authorized by this revision: after fresh plan review, replace only Run pre-commit's `run:` value with the exact supported no-SKIP selector; no other workflow, hook/config, source, test, documentation, or historical-evidence change is allowed. |
| PR-comment test hygiene | `tests/response_cache/test_entry.py`, `tests/response_cache/test_key_factory.py`, `tests/response_cache/test_canonical_feature_hasher.py`, `tests/response_cache/test_in_memory_store.py` | Implementer | The sole test artifacts authorized by this revision: resolve all five listed PR threads through unreachable-assertion removal, local `# noqa: F401` on the retained expected-failure ordinary imports, and the two stated inline reasons; no behavioral, import-mechanism, or other-test change. |
| Response-cache sources | `src/async_model_gateway/response_cache/__init__.py`, `src/async_model_gateway/response_cache/cache.py`, `src/async_model_gateway/response_cache/key.py`, `src/async_model_gateway/response_cache/entry.py`, `src/async_model_gateway/response_cache/key_factory.py`, `src/async_model_gateway/response_cache/_canonical_feature_hasher.py`, `src/async_model_gateway/response_cache/freshness_policy.py`, `src/async_model_gateway/response_cache/ttl_freshness_policy.py`, `src/async_model_gateway/response_cache/_in_memory_store.py`, `src/async_model_gateway/response_cache/outcomes.py`, `src/async_model_gateway/response_cache/record.py`, `src/async_model_gateway/response_cache/errors.py`, `src/async_model_gateway/response_cache/invalidation.py`, `src/async_model_gateway/response_cache/compat.py` | Implementer | Future implementation scope only; responsibilities and dispositions are frozen in technical spec and reconciliation. |
| Response-cache ports | `src/async_model_gateway/response_cache/ports/__init__.py`, `src/async_model_gateway/response_cache/ports/feature_hasher.py`, `src/async_model_gateway/response_cache/ports/store.py`, `src/async_model_gateway/response_cache/ports/codec.py`, `src/async_model_gateway/response_cache/ports/version_token_factory.py`, `src/async_model_gateway/response_cache/ports/invalidator.py` | Implementer | Future implementation scope only; normal target port boundary. |
| Response-cache tests | `tests/response_cache/test_cache.py`, `tests/response_cache/test_canonical_feature_hasher.py`, `tests/response_cache/test_entry.py`, `tests/response_cache/test_in_memory_store.py`, `tests/response_cache/test_key.py`, `tests/response_cache/test_key_factory.py`, `tests/response_cache/test_response_cache_freshness_policy.py`, `tests/response_cache/test_response_cache_package_surface.py`, `tests/response_cache/test_ttl_freshness_policy.py`, `tests/response_cache/test_response_cache_contract_migration.py` | Implementer | Future direct-import behavior, race, cancellation, migration, and absence coverage; no dynamic module loading. |
| Documentation | `README.md`, `docs/architecture.md`, `docs/specs/response-cache-boundary.md` | Implementer | Future post-GREEN behavior synchronization only; no planning-task edit. |

### Feature authority and transfer verification

- The six rows whose owner begins with Worktree-manager migration lane are the complete transfer
  set. Their feature target is selected by `refs/heads/feat/andrew/response-cache-contract-migration`;
  every source is selected by `refs/heads/dev`; the registered relative path is identical on both
  sides.

| Dev source relative path | Feature-authoritative target relative path | Move owner |
| --- | --- | --- |
| `analysis/response-cache-contract-migration/requirements.md` | `analysis/response-cache-contract-migration/requirements.md` | Worktree-manager migration lane |
| `analysis/response-cache-contract-migration/technical-spec.md` | `analysis/response-cache-contract-migration/technical-spec.md` | Worktree-manager migration lane |
| `analysis/response-cache-contract-migration/canonical-reconciliation.md` | `analysis/response-cache-contract-migration/canonical-reconciliation.md` | Worktree-manager migration lane |
| `plan/response-cache-contract-migration/response-cache-contract-migration.plan.md` | `plan/response-cache-contract-migration/response-cache-contract-migration.plan.md` | Worktree-manager migration lane |
| `plan/response-cache-contract-migration/response-cache-contract-migration.spec.md` | `plan/response-cache-contract-migration/response-cache-contract-migration.spec.md` | Worktree-manager migration lane |
| `plan/response-cache-contract-migration/response-cache-contract-migration.plan-review.json` | `plan/response-cache-contract-migration/response-cache-contract-migration.plan-review.json` | Worktree-manager migration lane |

- Before removal, the lane must inspect the exact six source files, calculate six individual
  SHA-256 values, write and re-hash each feature target, then verify a one-to-one six-row match.
  A target pre-existing with nonmatching bytes is a hard stop. Directory-level hashes, a single
  aggregate hash, wildcard selection, or a claim that files are "equivalent" is insufficient.
- After all six matches, the lane must verify that feature contains exactly the six listed planning
  files at their registered paths and only then remove each dev source. The final check confirms
  all six dev paths are absent and all six feature paths are readable. No historical feature-only
  path is an input to or output from this protocol.
- The new authority starts only after that final check. The moved `plan-review.json` begins as
  superseded transfer material; the next valid review is a fresh, independent Reviewer artifact
  at the same feature path after the move, never a review read from dev.
- The completed, reviewer-verifiable record is
  `plan/response-cache-contract-migration/response-cache-contract-migration.transfer-handoff.yaml`.
  It records the exact six source/target SHA-256 pairs, target readability, individual dev-source
  removal result, and the three historical-evidence before/after digests at the move snapshot.
  Its provenance is the Worktree-manager lane handoff captured in transfer order (source hash,
  target write and re-hash, match, then source removal), not a reconstruction from absent dev
  paths. Any later authorized content event is listed separately and cannot rewrite that snapshot.

## Implementation Steps

After the authority-migration gates in **Status / Allowed Transitions** pass, the Implementer
executes only the following approved response-cache work in the feature worktree. These are not
instructions to perform work in this planning rework.

1. In the listed `tests/response_cache/` files, establish direct-import RED coverage for the
   technical-spec and reconciliation contract; do not rewrite the historical `red-tests.yaml`.
2. In `key.py`, `outcomes.py`, `record.py`, and `errors.py`, establish `CacheKey`, immutable record
   / token, closed outcomes, and the sole operational-error family; remove old direct entry routing
   only through the declared compatibility disposition.
3. In `freshness_policy.py`, `ttl_freshness_policy.py`, and `cache.py`, implement write-time expiry,
   the five keyword-only collaborators, one clock owner, complete record construction, lookup and
   remember outcomes, and unchanged cancellation / defects.
4. In `ports/store.py`, `codec.py`, `version_token_factory.py`, `invalidator.py`, and
   `ports/__init__.py`, establish the target submodule-only ports and remove normal feature-hasher
   dependence as specified.
5. In `_in_memory_store.py` and `invalidation.py`, implement coherent whole-record replacement,
   atomic `delete_if_version`, and key-local invalidation; prove stale cleanup cannot delete a
   concurrent replacement.
6. In `compat.py`, with the declared removals of `entry.py`, `key_factory.py`,
   `_canonical_feature_hasher.py`, and `ports/feature_hasher.py`, implement only the reconciled
   deprecated direct-import surface, warnings, legacy maps, and ignored context sentinel.
7. In `__init__.py` and package-surface tests, expose exactly the target root surface, enforce
   legacy root/direct-path absence, and prove `compat` with ordinary imports only.
8. Update exactly `README.md`, `docs/architecture.md`, and `docs/specs/response-cache-boundary.md`
   after GREEN behavior validation; then complete the feature tracker and request independent
   implementation review.
9. After this revision receives a fresh independent plan-review approval and the existing later
   gate order has been re-established for this revision, update only the four registered tests:
   remove the five unreachable assertions from expected-failure imports, place `# noqa: F401`
   only on those five retained ordinary imports, and add the two locked inline reasons in
   `test_entry.py`; preserve exception assertions, direct-import semantics, and all test behavior.
10. After the same fresh gates, change only the Run pre-commit `run:` value in
    `.github/workflows/ci.yml` to the exact supported selector declared in **Locked Decisions**;
    do not add `SKIP`, a hook override, `--exclude`, another exclusion, or any other workflow
    change, and do not mutate the historical file.

## Validation / Acceptance Checks

- Confirm strict analysis is read only from the three feature-authoritative analysis paths, and
  plan/spec/review authority is read only from their feature targets after the six-file move.
- Confirm the declared transfer-handoff ledger has six, and only six, path pairs; each has the
  recorded matching SHA-256 source/target digests, target readability, and individual dev-source
  removal result. Confirm all six dev sources are absent. Validate the three historical evidence
  before/after digest rows against their stated migration-snapshot provenance; distinguish the
  Human-authorized post-transfer `human-check.json` current immutable anchor from fresh approval.
- Confirm a fresh independent Reviewer writes one JSON object at the feature `plan-review.json`
  target after move. Its `approved` verdict and the subsequently created fresh human check are
  both required; the transferred old review is invalid for approval.
- Confirm audit truth: `fresh-human-check.json` and `forward-preflight.yaml` do not exist before
  their owners create them in order. Validate forward preflight against the fresh check, the
  feature moved-plan SHA-256, and the immutable historical preflight SHA-256; it cannot cite or
  upgrade historical human-check / preflight evidence.
- Confirm historical `human-check.json`, `worktree-preflight.yaml`, and `red-tests.yaml` remain
  byte-identical and read-only. Their existence is candidate provenance only, not a substitute for
  review, fresh check, forward preflight, tracker, or implementation review.
- Confirm the new feature tracker is absent before its gate, begins with the eight unchecked
  implementation entries above, and is Implementer-only thereafter. Only after all entries are
  truthfully complete can an independent Reviewer create `implementation-review.yaml`.
- Draft PR validation replaces the unsupported `pre-commit --exclude` interface with this exact,
  still-hooked files-selection check. Before the command, record the historical human-check SHA-256
  and terminal byte from the transfer ledger. Run the exact command below with no `SKIP` environment
  variable or hook override; it must report every configured hook passed for every selected file.
  Afterwards, require the same SHA-256, terminal byte `0x7d`, and no working-tree diff for the
  historical path. The Main Agent then writes the declared Draft PR preflight artifact with the
  literal command, `git ls-files -co --exclude-standard` candidate-selection command, literal
  `rg -v` excluded-path regex, `skip_used: false`, `hook_overrides_used: false`, per-hook pass
  result, pre/post digest, pre/post terminal byte, and `historical_path_modified: false`. Do not run
  an invocation that includes the historical path as a probe: a mutation followed by restoration is
  a failed gate, not proof.
- Before the compatibility command, require the Human-owned Draft PR human-check artifact to contain
  `decision: approved`, `status: cleared`, `cleared_for: publish-in-progress`, and the SHA-256 of
  this reviewed plan; it is a separate revision gate and does not modify or reuse either existing
  human-check artifact.
- Confirm `.github/workflows/ci.yml` contains the exact same selector only in its Run pre-commit
  `run:` value and has no other CI workflow alteration. The CI result must retain historical
  `human-check.json` SHA-256
  `f6ec59dbf3f5df4ba42359b9978c31bebd4bbf30b1645146ba1a4841508d417b`, terminal byte `0x7d`,
  and no working-tree diff; a `SKIP`, hook override, `--exclude`, mutation, or
  mutate-and-restore sequence fails this check.
- Confirm the diff for the five PR-comment threads is limited exactly to the four registered test
  paths: five unreachable assertions are absent; exactly five retained expected-failure ordinary
  imports carry local `# noqa: F401`; `test_entry.py` has exactly the two declared concise inline
  reasons; the expected exception classes and all remaining assertions retain their prior behavior.
  Confirm no test in this revision uses dynamic module loading (`importlib`, loader, `exec`, `eval`,
  `runpy`, or `__import__`) and no historical evidence bytes change.

```text
uv run pre-commit run --files $(git ls-files -co --exclude-standard | rg -v '^plan/response-cache-contract-migration/response-cache-contract-migration\.human-check\.json$')
```
- Later implementation validation remains:

```text
uv run pytest tests/response_cache -v --no-cov
uv run pytest tests/response_cache/test_entry.py tests/response_cache/test_key_factory.py tests/response_cache/test_canonical_feature_hasher.py tests/response_cache/test_in_memory_store.py -v --no-cov
uv run pytest
uv run ruff check src tests docs README.md analysis/response-cache-contract-migration plan/response-cache-contract-migration
uv run pyright
uv run pre-commit run --files $(git ls-files -co --exclude-standard | rg -v '^plan/response-cache-contract-migration/response-cache-contract-migration\.human-check\.json$')
```

## Reviewer Handoff

```json
{
  "verdict": "approved | needs-rework",
  "blocking_issues": [],
  "copilot_feedback_triage": {
    "ADDRESS": [],
    "DISCUSS": [],
    "SKIP": []
  }
}
```

## Post-merge / release actions

No release workflow required.

## Open Questions / Unresolved Items

None. The exact six-file transfer set, feature targets, historical-evidence exclusions, fresh
evidence order, plan-review authority, implementation boundary, and no-release decision are
frozen.

## Python implementation-planning supplement (13-section extension)

This supplement preserves the non-trivial Python executor contract without replacing or reordering
the canonical sections above. Its planning authority is the moved feature plan plus the three moved
analysis artifacts; implementation must not start until the new feature plan review and human check
are approved.

### Goal

Deliver the strict response-cache migration after authority recovery: one root async facade,
one identity authority, safe complete-record storage, and one temporary legacy adapter.

### Non-goals

- This rework will not move files itself or modify source, documentation, historical feature
  evidence, or tests other than the four exact PR-comment test-hygiene paths.
- The implementation will not add a third facade method, synchronous mirror, public lifecycle,
  root-public port, root legacy export, timeout, retry, or background owner.
- The implementation will not add persistence infrastructure, settings, backend selection,
  eviction, capacity, admission, metrics, tracing, data migration, orchestration, or release work.

### Current Context

The completed six-file migration handoff is recorded in the declared transfer ledger: all six dev
sources are absent and the feature targets are the only planning authority. The feature worktree
retains the three historical candidate paths named in the artifact register; the ledger preserves
their move-snapshot digests and classifies the authorized later Human update as the current
immutable Draft PR anchor. The fresh human check and forward preflight are completed
implementation-entry evidence, not publication evidence. The legacy response-cache implementation
and target behavior remain fully specified by the moved strict analysis; this plan does not
re-decide them.

### Requirements

1. Preserve the completed move's exact six-file source/target SHA-256, readability, and
   dev-removal results in the declared repo-visible transfer ledger; feature targets remain the
   sole planning authority.
2. Require fresh independent plan review at the feature `plan-review.json` target after move;
   transferred old review content cannot approve this revision.
3. Preserve the three existing feature historical candidate before/after migration-snapshot
   digests in the ledger and never elevate them to fresh / forward evidence; classify the
   Human-authorized `human-check.json` post-transfer update separately as a byte-immutable Draft
   PR anchor, never as fresh approval.
4. Recreate fresh human check, forward preflight, step tracker, and implementation review only in
   the stated order and at the feature targets.
5. Later implementation satisfies every technical-spec and reconciliation mapping, including
   direct-import-only tests and no dynamic module loading.
6. After fresh Plan-Reviewer approval of this post-implementation rework, require a separately
  Human-owned, current-plan-bound Draft PR human check before code-review evidence and Draft PR
  preflight can authorize `pr-open`.
7. Resolve all five listed PR-comment threads only in the four registered test files: expected-
   failure imports remain ordinary imports with local `# noqa: F401`, unreachable assertions are
   removed, and only `test_entry.py` receives the two precise type-ignore reasons.

### Decisions

- Async-planning status: triggered — cite trigger evidence: the frozen migration changes async
  facade/store boundaries, cancellation propagation, stale-cleanup race behavior, and explicit
  no-timeout/no-retry policy; these decisions are recorded in technical-spec.
- Module/package placement: all planning authority paths and future source/test/doc paths are the
  exact entries in the canonical Artifact Paths register above.
- New public API: yes — only the target `ResponseCache`, `CacheKey`, and closed outcomes named in
  technical-spec; `lookup(*, key, context)` and `remember(*, key, value, context)` are the two
  facade methods.
- Interface changes: yes — record-based `CacheStore`, codec/token/invalidator ports, and
  `compat.py` are frozen by technical-spec and reconciliation.
- Breaking changes allowed: yes, controlled by the temporary exclusive legacy adapter and its
  separately approved terminal-removal condition.
- New dependencies: no.
- Error-handling strategy: only the closed operational-error family translates at its declared
  boundary; cancellation and all non-family defects propagate unchanged.
- Typing strategy: strict Pyright, frozen slotted dataclasses, closed enum/union outcomes,
  `Protocol` collaborators and invocation-only `TypeVar`; no `Any`, dynamic module loading, or
  context persistence.

### Async boundary decision

Only facade, store, and invalidator I/O are async. Identity, codec work, token construction,
record validation, expiry comparison, and transfer checksum work are synchronous; no sync-to-async
conversion is introduced by authority migration.

### Resource lifecycle decision

The composition root owns store lifecycle. `ResponseCache` retains injected collaborators only for
operations and does not close, reconnect, flush, or reset them. The move lane owns no runtime
resource lifecycle; it performs only bounded planning-artifact transfer verification.

### Concurrency model

Each cache call direct-awaits collaborators. Store coherence is per key with atomic compare-delete;
there is no facade lock, task, worker, fan-out, retry, or cross-key coordination. Planning transfer
is sequential per exact file so digest comparison and source removal cannot be ambiguous.

### Failure model

`CacheOperationalError` family behavior is as frozen by technical-spec. Transfer failures are
workflow failures, not cache outcomes: missing source, nonmatching target, incomplete target set,
or failed dev removal stops authority migration and routes to planning rework.

### Cancellation / timeout policy

Cache callers own cancellation; facade and adapter neither catch nor shield it. No timeout or retry
is introduced. A cancelled or failed move operation must not remove any unmatched dev source or
assert completed authority migration.

### Validation plan

First validate the declared six individual SHA-256 pairs, post-move dev absence, feature
readability, individual source-removal results, and the three historical before/after snapshot
digest rows. Treat the separately recorded Human-authorized post-transfer update as non-gating;
then fresh feature plan review, human check, forward preflight, tracker creation, and later
implementation tests follow in the exact gate order. Later tests cover happy path, invalid input,
edge cases, regression, backward compatibility, cancellation, and races. For Draft PR, use only
the declared exact supported files command, then prove the historical human-check's SHA-256 and
terminal `0x7d` byte are unchanged before writing preflight evidence; no `SKIP`, broad file
selection exclusion, hook override, or mutate-and-restore sequence is valid. First require the
separate Draft PR human check to bind
this plan's reviewed SHA-256; the existing human checks are never publication authority.

### Handoff notes for the implementer

Read the three feature-authoritative analysis artifacts and the feature plan only after the move
gate passes. Do not use the historical three files to infer approval. Stop for rework if an
unregistered path, legacy route, error class, context channel, or backend requirement emerges.

### Public Contract / API Changes

The planned root API remains the technical-spec target: `ResponseCache`, `CacheKey`, and closed
outcomes only; collaborator ports are submodule-public; `CacheInvalidator` is separate; old routes
exist only through deprecated `compat.py`. This authority migration creates no additional API.

### Affected Files / Modules

Likely affected future implementation files are every source/test/doc path listed in the canonical
Artifact Paths register plus the sole CI artifact `.github/workflows/ci.yml` and the four exact
PR-comment test-hygiene artifacts. The only file modified by this planning rework is this topic
plan. After fresh plan review, the CI fix may modify only that workflow's Run pre-commit `run:`
value and the test cleanup may modify only the four registered test files; the other five dev
planning sources were migration inputs, not planning-actor edits. Candidate files to inspect before
later implementation are the three feature analysis artifacts and the feature
`response-cache-contract-migration.spec.md`.

### Implementation Steps

The eight canonical implementation steps above are mirrored by the future feature step tracker.
The Implementer must not create that tracker until fresh review, fresh human check, and passed
forward preflight are present in their feature-authoritative paths. The separately authorized CI
fix is the tenth canonical step and remains limited to the exact selector and historical-byte
proof declared above; the ninth canonical step is the locked five-thread test cleanup and cannot
expand beyond the four registered test paths.

### Test Plan

- Happy path: target facade lookup/remember writes and reads one complete record.
- Invalid input: malformed keys, records, timestamps, metadata, and configuration propagate as
  defects rather than closed outcomes.
- Edge case: expired/unsupported records, cleanup failures, closed store, and cancellation follow
  the technical-spec matrix.
- Regression: coherent replacement and compare-delete race preserve a concurrent fresh record.
- Backward compatibility: direct `compat` imports provide only the reconciled deprecated bridge;
  root and old direct paths remain absent without dynamic module loading.
- PR-comment regression: the four registered tests preserve their expected-failure and direct-import
  behavior while removing only unreachable assertions, applying the five local F401 suppressions,
  and adding the two precise reasons.

### Validation Commands

Use the exact later implementation commands declared in **Validation / Acceptance Checks** after
the feature authority and gate ordering checks pass.

### Risks

- A partial or non-digest-verified transfer could make dev and feature disagree about plan truth.
- Treating a historical candidate or transferred old review as fresh approval would bypass explicit
  human and reviewer gates.
- Creating a tracker or implementation review before forward preflight would falsify workflow
  order and contaminate evidence authority.
- A files invocation that includes the immutable historical human-check would add a final LF through
  the EOF fixer; restoring that side effect cannot make the validation pass. A broader file-selection
  exclusion, hook override, or `SKIP` would silently reduce hook coverage.
- Reusing the implementation-entry fresh human check after this plan revision would leave Draft PR
  authorization without a Human-owned, current-plan-bound gate.

### Rollback Plan

If any transfer check fails, do not remove remaining dev sources; restore an incomplete target only
from its digest-matched source and repeat the bounded six-file protocol after rework. Before a
later code merge, revert only the registered source/test/doc paths with the feature-authoritative
analysis and plan artifacts; never revert or alter the three immutable historical candidates. If
Draft PR preflight fails, do not repair the historical human-check: remove only the failed
non-historical preflight artifact, preserve the anchored bytes, and return to this gate contract.

### Open Questions

None.
