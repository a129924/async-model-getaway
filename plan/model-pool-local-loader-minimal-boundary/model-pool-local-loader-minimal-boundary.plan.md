> Semantic warning: `analysis/model-pool-local-loader-minimal-boundary/requirements.md`
> 與 `analysis/model-pool-local-loader-minimal-boundary/technical-spec.md` 均不存在。
> 本 revision 依據已 merged 的 implementation、現有 `model_runtime` /
> `model_artifact` contract，以及人類明確授權的 `v0.4.7` release；不得以此補齊
> broader runtime scope。

# model-pool-local-loader-minimal-boundary

## Goal / Outcome

- 維持 `async_model_gateway.model_runtime.model_pool.ModelPool` 的最小 public
  local runtime-model acquisition boundary，將 private `LocalModelLoader` 改為
  由 type-checker-aware `assert_never(...)` 收束的 explicit `match/case`
  family-dispatch structure。
- `model_artifact` 僅被消費；`LocalModelLoader.load(...) -> object` 只加註已鎖定
  future contract TODO，不建立 `LoadedRuntimeModel` 或任何 abstraction。
- 將已 merged 的最小 `ModelPool` / private `LocalModelLoader` boundary 納入
  `v0.4.7` package baseline：先 commit 並 push 指定 first-read / architecture 文件與
  version metadata，從該 release commit 建立並 push 同名 lightweight git tag，接著
  寫入、另 commit 並 push release evidence，且 evidence commit 不得移動 tag；不建立
  GitHub Release，也不發佈套件。

## Scope

- **In scope**:
  - 移除 private loader 的 `_route_mapping` construction/test seam 與所有
    production mapping-lookup dispatch。
  - 以 `artifact.loader_family` 的 explicit `match/case` 呼叫並 `await` 各
    `_load_<family>` private handler；目前 `PICKLE`、`TORCH`、`ONNX` 各有一個 case，
    並以 `typing_extensions.assert_never(...)` 表示 enum 窮舉後不可達的 fallback。
  - 測試 monkeypatch private family handlers，逐 branch 驗證 route，而非注入 mapping。
  - 在 `LocalModelLoader.load(self, artifact: ModelArtifact) -> object` 加入精確
    two-line TODO；重建本 revision 的 plan、RED-test、implementation-review 與
    code-review gates。
  - 更新 `README.md`、`docs/architecture.md`、
    `docs/specs/model-side-boundary.md`、
    `docs/specs/core-abstractions-boundary.md` 與
    `docs/specs/canonical-input-boundary.md`，使其只反映已落地的最小 acquisition
    boundary，且不宣稱 artifact I/O、完整 lifecycle、runtime-model contract 或
    provider abstraction 已完成。
  - 將 `src/async_model_gateway/__version__.py`、`pyproject.toml` 與 `uv.lock`
    的 package version 從 `0.4.6` 同步 bump 至 `0.4.7`；在同步後的 `dev` release
    commit 建立並推送 lightweight `v0.4.7` git tag，記錄 release evidence，並以獨立
    evidence commit push 該 artifact，而不移動 tag。
- **Out of scope**:
  - artifact I/O、serialization/framework imports、provider adapter、runtime-model
    concrete type、Protocol、provider abstraction。
  - cache/reuse、close/unload、timeout、retry、background task、fan-out、broader
    lifecycle policy。
  - `ModelGateway`、`ModelExecution`、`model_registry`、`response_cache`、
    `model_artifact` source/tests/exports/fields/vocabulary/validation。
  - GitHub Release、PyPI 或其他套件發佈、release note、dependency / packaging policy
    變更，以及任何未列出的文件或 source/test path。

## Locked Decisions

- D1 verdict: `non-trivial`；此 revision changes an internal test seam and async
  dispatch structure across source, tests, spec, and workflow evidence.
- `ModelPool` remains the only `model_pool` package-root public export. Its public
  signature remains exactly `async def acquire(self, artifact: ModelArtifact) -> object`.
  No constructor injection, factory API, lifecycle method, root re-export, or
  `model_runtime` umbrella re-export is added.
- `pool.py` retains private `def _create_local_model_loader() -> LocalModelLoader`.
  `ModelPool.__init__` calls it exactly once and retains its result; `acquire(...)`
  validates `ModelArtifact` and directly awaits that loader.
- `LocalModelLoader` stays private at
  `async_model_gateway.model_runtime.model_pool._local_model_loader`; it accepts no
  `_route_mapping` or replacement injection seam. The pool factory remains a
  pool-wiring test seam only.
- `LocalModelLoader.load(self, artifact: ModelArtifact) -> object` contains exactly:

  ```python
  # TODO: Replace `object` with the agreed runtime-model contract
  # (tentatively `LoadedRuntimeModel`) once that boundary is defined.
  ```

  This is documentation only: do not create `LoadedRuntimeModel`, a Protocol, or a
  provider abstraction.
- `load(...)` reads only `artifact.loader_family` and uses explicit `match/case`:
  `LoaderFamily.PICKLE -> await self._load_pickle(artifact)`,
  `LoaderFamily.TORCH -> await self._load_torch(artifact)`, and
  `LoaderFamily.ONNX -> await self._load_onnx(artifact)`. No mapping lookup, path
  inference, content/options inference, fallback, or `KeyError` dispatch is allowed.
  `case _` must call `typing_extensions.assert_never(artifact.loader_family)`;
  it is the type-checker-aware unreachable path for the closed `LoaderFamily` enum,
  not input validation and not a new domain exception. `typing_extensions` is an
  existing runtime dependency required by the Python 3.10 baseline; do not add a
  dependency or use `typing.assert_never`.
- Known family handlers remain no-I/O and raise `NotImplementedError`. Invalid public
  `ModelPool.acquire` input remains `TypeError`; existing invalid `ModelArtifact`
  construction remains `ValueError`; route failures and `asyncio.CancelledError`
  propagate unchanged. No test or behavior contract is added for a fabricated
  non-`LoaderFamily` value at the unreachable fallback. Do not add
  `UnsupportedLocalModelLoaderError`.
- `ModelArtifact` / `LoaderFamily` are consumed-only shared read contracts; no source,
  test, export, field, vocabulary, or validation change is authorized.
- Async-planning is a focused retrofit, not a new lifecycle design: direct await,
  caller-owned cancellation, no timeout/retry, and no external resource ownership
  remain locked.
- Stable-library release intent is explicit: baseline `0.4.6` receives exactly one
  patch bump to `0.4.7`. The executable version sources are
  `src/async_model_gateway/__version__.py`, `pyproject.toml`, and `uv.lock`; there
  is no root `VERSION` file. README and the four named architecture/spec documents
  require a bounded wording update. The post-merge release action commits and pushes
  those synchronized metadata and documentation updates, creates and pushes lightweight
  tag `v0.4.7` from that exact release commit, then commits and pushes release evidence
  without moving the tag. Do not create a GitHub Release or publish a package.
- Release clearance is a fresh Human-owned artifact for revision
  `v0.4.7-release-contract-sequenced`. It may exist only after the declared
  release-plan review artifact records `verdict: approved`, and it must contain the
  topic, that exact revision, `decision: approved`, `status: cleared`,
  `release_plan_review_path`, `release_plan_review_verdict: approved`,
  `cleared_for: release`, and `cleared: true`. No documentation, version, lock,
  commit, push, tag, or evidence work may begin before this artifact exists.
- Existing plan-review, human-check, RED-test, implementation-review, and code-review
  evidence record the completed `assert-never-explicit-dispatch` implementation and
  must remain unmodified historical truth. They do not approve this later release
  contract; the release-specific reviewer and Human artifacts declared below are the
  only new gates.

## Boundaries / Exclusions

- Planning actor edits only planning artifacts; Tester authors fresh RED evidence;
  Implementer changes only approved source/tests/step progress; independent reviewers
  issue plan-, implementation-, and code-review verdicts; Human alone clears human
  check and human merge gates.
- If any change needs public `LocalModelLoader`, actual artifact loading, different
  runtime-model typing, provider behavior, a new exception hierarchy, or an adjacent
  model runtime owner, stop and return to `spec-and-plan-finalization`.
- No implementation path outside the exact table below is authorized.

## Status / Allowed Transitions

- **Current**: `merged` — implementation, PR, and human-merge history remain
  complete. Only the declared post-merge release workflow remains; it does not reopen
  the merged implementation.
- **Execution model**: `spec-and-plan-finalization -> implement-plan -> pr-comment ->
  pr-comment-review-pr-comments-and-fix -> release`; the `release` phase is required
  for this explicitly declared stable-library promotion.
- **Allowed transition**: `merged` -> `released`, only after all post-merge release
  gates and release implementation steps below complete in order.

  The already completed Python workflow remains historical evidence for the merged
  implementation. The fresh release gate sequence is: (5) Plan-Reviewer approves the
  declared `release-plan-review`; (6) Human writes the bound
  `release-human-check`; then (7) Implementer commits and pushes the bounded
  docs/version release change, (8) creates and pushes its exact lightweight tag, and
  (9) commits and pushes release evidence without moving the tag. This does not rerun
  RED tests or rewrite implementation/code-review evidence.

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/model-pool-local-loader-minimal-boundary/model-pool-local-loader-minimal-boundary.plan.md` | Planning actor | execution contract |
| Python spec | `plan/model-pool-local-loader-minimal-boundary/model-pool-local-loader-minimal-boundary.spec.md` | Planning actor | behavior contract |
| Step tracking | `plan/model-pool-local-loader-minimal-boundary/model-pool-local-loader-minimal-boundary.step.md` | Implementer | progress/gate tracking |
| Plan review | `plan/model-pool-local-loader-minimal-boundary/model-pool-local-loader-minimal-boundary.plan-review.json` | Plan-Reviewer | historical implementation plan-review evidence; not a release gate |
| Human check | `plan/model-pool-local-loader-minimal-boundary/model-pool-local-loader-minimal-boundary.human-check.json` | Human | historical implementation clearance; not a release gate |
| Release plan review | `plan/model-pool-local-loader-minimal-boundary/model-pool-local-loader-minimal-boundary.release-plan-review.json` | Plan-Reviewer | fresh release gate for this post-merge release-contract revision |
| Release human check | `plan/model-pool-local-loader-minimal-boundary/model-pool-local-loader-minimal-boundary.release-human-check.json` | Human | fresh release gate bound to this topic/revision and approved release-plan review |
| RED-test evidence | `plan/model-pool-local-loader-minimal-boundary/model-pool-local-loader-minimal-boundary.red-tests.yaml` | Tester | historical implementation evidence; not a release gate |
| Implementation review | `plan/model-pool-local-loader-minimal-boundary/model-pool-local-loader-minimal-boundary.implementation-review.yaml` | Reviewer | historical implementation evidence; not a release gate |
| Code review | `plan/model-pool-local-loader-minimal-boundary/model-pool-local-loader-minimal-boundary.code-review.yaml` | Reviewer | historical implementation evidence; not a release gate |
| Package root | `src/async_model_gateway/model_runtime/model_pool/__init__.py` | Implementer | `ModelPool` re-export only |
| Public pool | `src/async_model_gateway/model_runtime/model_pool/pool.py` | Implementer | public acquisition / retained loader |
| Private loader | `src/async_model_gateway/model_runtime/model_pool/_local_model_loader.py` | Implementer | explicit family dispatch |
| Package tests | `tests/model_runtime/model_pool/test_model_pool_package_surface.py` | Tester | public surface / TODO regression |
| Pool tests | `tests/model_runtime/model_pool/test_model_pool.py` | Tester | acquire wiring/failures/cancellation |
| Loader tests | `tests/model_runtime/model_pool/test_local_model_loader.py` | Tester | every `match/case` branch / default handlers |
| Project summary | `README.md` | Implementer | first-read baseline and minimal ModelPool / LocalModelLoader availability wording |
| Architecture summary | `docs/architecture.md` | Implementer | narrow model-runtime implementation-status wording |
| Model-side specification | `docs/specs/model-side-boundary.md` | Implementer | minimal implemented ModelPool / private loader boundary wording |
| Core-abstractions specification | `docs/specs/core-abstractions-boundary.md` | Implementer | remove the stale LocalModelLoader-only-deferred claim |
| Canonical-input specification | `docs/specs/canonical-input-boundary.md` | Implementer | preserve model_artifact ownership while updating local-acquisition status |
| Package runtime version | `src/async_model_gateway/__version__.py` | Implementer | exact `0.4.7` patch bump |
| Packaging metadata version | `pyproject.toml` | Implementer | exact `0.4.7` patch bump |
| Lockfile metadata | `uv.lock` | Implementer | synchronized package-version metadata |
| Release evidence | `plan/model-pool-local-loader-minimal-boundary/model-pool-local-loader-minimal-boundary.release.yaml` | Implementer | post-tag evidence: release-commit SHA, tag resolution, remote-tag verification, no-GitHub-Release/no-publish outcome; committed and pushed separately without moving the tag |

All `model_artifact` paths, root package paths, `model_registry`, `response_cache`,
and every documentation path not listed above are explicit no-change paths. Existing
plan-review, human-check, RED-test, implementation-review, and code-review artifacts
remain historical evidence and must not be edited. Evidence rows are routing
declarations only; the planning actor does not write reviewer, Human, or Implementer
evidence artifacts.

## Stable library metadata

- `README row`: update the existing 「目前階段」 / model-runtime summary and
  「尚未實作」 wording so it names the minimal `ModelPool.acquire(...)` and private
  explicit-dispatch `LocalModelLoader` availability, while retaining deferral of
  artifact I/O, full lifecycle, a concrete runtime-model contract, provider
  abstraction, `ModelGateway`, and `ModelExecution`.
- `VERSION bump`: patch bump from `0.4.6` to `0.4.7` in the two executable version
  sources and synchronized `uv.lock` package metadata.
- `timing`: `release`, on `dev` after the implementation PR is merged and after the
  fresh approved release-plan-review plus the bound release-human-check gate exist.
- `rationale`: the bounded public `ModelPool` acquisition surface is already merged;
  this authorized promotion aligns only stale documentation and package metadata with
  that fact, without reopening runtime architecture or behavior.
- `release-note expectation`: none. Commit and push the bounded docs/version change;
  create and push lightweight git tag `v0.4.7` from that exact commit; then commit and
  push release evidence without moving the tag. Do not create a GitHub Release and do
  not publish a package.

## Implementation Steps

The merged Python implementation (historical sequence 1–4 in the step tracker) is not
an action in this post-merge release plan. Only the Implementer-owned release steps
remain here; the prerequisite reviewer and Human gates are in
`Post-merge / release actions`.

7. Implementer, only after release gates 5 and 6 are complete, updates the five declared
   documentation files to distinguish the implemented minimal acquisition boundary
   from deferred artifact I/O / wider runtime work, synchronizes the three declared
   version metadata files to `0.4.7`, runs release validation, and commits and pushes
   exactly those eight documentation/version changes on `dev` as the release commit.
8. Implementer creates lightweight tag `v0.4.7` from the exact release commit in step
   7 and pushes that tag. The tag must resolve locally and remotely to the release
   commit.
9. Implementer writes the declared release evidence with the release-commit SHA, tag
   resolution, remote-tag verification, and no-GitHub-Release/no-publish result; then
   commits and pushes that evidence artifact separately on `dev`. This evidence commit
   must not move, replace, delete, or retarget `v0.4.7`.

## Validation / Acceptance Checks

- `LocalModelLoader.load` has exactly the specified signature and two-line TODO;
  neither `LoadedRuntimeModel` nor a Protocol/provider abstraction exists.
- Production dispatch contains explicit `match artifact.loader_family` cases for all
  three current families. Each case directly awaits only its matching private handler;
  no `_route_mapping`, mapping lookup, or `KeyError` dispatch remains. The only
  fallback is `typing_extensions.assert_never(artifact.loader_family)`, preserving
  static enum exhaustiveness rather than defining a runtime invalid-family policy.
- Tests monkeypatch the three private handler methods and demonstrate every branch,
  path-independent family choice, default `NotImplementedError`, TypeError/ValueError
  surfaces that remain applicable, unchanged route failures, and unchanged cancellation;
  they do not fabricate an unforeseen family or expect `ValueError` from the
  unreachable fallback.
- `ModelPool` public API, one-time factory retention, public exports, direct await,
  `model_artifact` consumed-only contract, and all scope exclusions remain unchanged.
- The five declared documentation files say the same limited truth: `ModelPool` is
  the package-root public minimal local acquisition boundary; `LocalModelLoader` is
  private, consumes `ModelArtifact`, selects only explicit current families, and has
  no artifact I/O. They retain all deferred wider runtime boundaries.
- `src/async_model_gateway/__version__.py`, `pyproject.toml`, and `uv.lock` all
  record exactly `0.4.7`; no other dependency or packaging policy changes occur.
- Before release work, the release-human-check artifact exists and identifies topic
  `model-pool-local-loader-minimal-boundary`, revision
  `v0.4.7-release-contract-sequenced`, and the approved declared release-plan-review
  artifact; it records `decision: approved`, `status: cleared`, `cleared_for: release`,
  and `cleared: true`.
- The release evidence identifies the `dev` release commit containing the bounded
  docs/version changes and pushed lightweight tag `v0.4.7`, confirms the tag resolves
  locally and remotely to that commit, and records that no GitHub Release was created
  and no package was published. The evidence is committed and pushed only after the
  tag push; its separate commit does not move the tag.
- The declared implementation plan-review, human-check, RED-test,
  implementation-review, and code-review artifacts remain historical evidence for
  the merged implementation; they are not re-opened or revalidated as release gates.
- Targeted validation: `uv run pytest --no-cov tests/model_runtime/model_pool -v`.
  Full coverage gate: `uv run pytest -v`. Static gates: `uv run ruff check src tests
  plan/model-pool-local-loader-minimal-boundary` and `uv run pyright`.
- Release metadata checks: `rg -n '0\\.4\\.7' README.md pyproject.toml
  src/async_model_gateway/__version__.py uv.lock`; record the release-commit SHA
  before tagging; `git rev-parse v0.4.7^{commit}` equals that SHA; and
  `git ls-remote --tags origin v0.4.7` verifies the pushed tag before release evidence
  is written, committed, and pushed without retagging.

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

This handoff applies only to fresh release Gate 5. Plan-Reviewer must review the
post-merge release-contract delta: exact release
paths, `0.4.7` timing, documentation boundaries, version/lock synchronization,
lightweight tag creation/push, and explicit no-GitHub-Release/no-publish intent. It
must write its verdict only to
`plan/model-pool-local-loader-minimal-boundary/model-pool-local-loader-minimal-boundary.release-plan-review.json`.
The existing planning, human, RED-test, implementation-review, and code-review
artifacts are historical and must not be changed or treated as the release gate.
Only after that approved release-plan review may the Human write the bound
release-human-check artifact described in Locked Decisions. Only after the clearance
exists may the bounded release actions in this plan proceed; any scope/contract change
returns to `spec-and-plan-finalization`.

## Post-merge / release actions

- **Gate 5 — Plan-Reviewer**: record `verdict: approved` in the declared
  `release-plan-review` artifact for revision `v0.4.7-release-contract-sequenced`.
- **Gate 6 — Human**: only after Gate 5, create the bound `release-human-check`
  artifact with the locked approval and clearance fields. No release implementation
  work may begin before this fresh Human gate exists.
- **Step 7 — Implementer**: update the declared docs/version/lock paths on `dev`,
  validate them, and commit and push those eight bounded changes as the release commit.
- **Step 8 — Implementer**: create and push lightweight `v0.4.7` from that exact
  release commit.
- **Step 9 — Implementer**: only after the tag push, record the release commit and
  remote-tag verification in
  `plan/model-pool-local-loader-minimal-boundary/model-pool-local-loader-minimal-boundary.release.yaml`,
  commits and pushes that evidence separately, and does not move the tag. Do not create
  a GitHub Release or publish a package. All wider local-loader behavior remains a
  separate topic.

## Open Questions / Unresolved Items

- None.

## Non-goals

- No artifact file read, pickle/torch/onnx integration, concrete runtime-model type,
  Protocol, or provider abstraction.
- No cache/reuse, close/unload, sharing, timeout, retry, batching, fan-out, or
  background ownership.
- No ModelGateway, ModelExecution, registry/cache integration, model_artifact change,
  new domain exception, GitHub Release, package publication, or additional release
  work beyond the declared docs/version/lock/tag paths.

## Requirements

1. `ModelPool.acquire` remains the sole new public local acquisition method.
2. `LocalModelLoader` remains private and dispatches each current family through its
   matching explicit `match/case` branch only.
3. The exact TODO records future typing without creating the deferred contract.
4. Default handlers remain no-I/O `NotImplementedError`; applicable invalid input uses
   existing TypeError/ValueError validation, the enum fallback is `assert_never(...)`,
   and async failures/cancellation are unwrapped.
5. Tests cover happy path, invalid input, edge case, regression, backward
   compatibility, and async safety without dynamic loading.

## Decisions

- Async-planning status: triggered — cite trigger evidence: the existing public
  `async ModelPool.acquire(...)` directly awaits a private loader and this revision
  preserves cancellation/failure routing.
- Module/package placement: the merged implementation remains limited to the three
  declared `model_pool` source paths and three test paths. The release delta may
  change only its separately declared docs/version/lock/evidence paths.
- New public API: none; existing `ModelPool.acquire(...) -> object` is preserved.
- Interface changes: private mapping seam removed; no public contract expansion.
- Breaking changes allowed: no public breaking change; the locked internal test seam
  is deliberately replaced and must be re-reviewed.
- New dependencies: none.
- Error handling strategy: TypeError for non-ModelArtifact acquire input, existing
  ValueError validation for invalid artifact construction, NotImplementedError for
  known no-I/O families, `assert_never(...)` for the statically unreachable enum
  fallback, and unwrapped route exceptions/cancellation; no domain exception.
- Typing strategy: keep `object`; record only the exact deferred-contract TODO.

### Async boundary decision

`ModelPool.acquire` and `LocalModelLoader.load` stay async. `load` performs one direct
await of its selected private handler; no external I/O is introduced.

### Resource lifecycle decision

`ModelPool` owns one retained in-memory loader returned by its private factory. No
external resource exists, so no close/unload/context-manager surface is added.

### Concurrency model

One acquisition directly awaits one matching handler. No task creation, fan-out,
locks, queue, semaphore, batching, cache, or coalescing is established.

### Failure model

Known selected family handlers raise `NotImplementedError` until later I/O work. The
closed enum's fallback calls `assert_never(...)`; it does not define support or
validation behavior for fabricated family values. Route result and exception surfaces
remain unwrapped.

### Cancellation / timeout policy

Caller owns cancellation. Neither boundary catches `asyncio.CancelledError`; no timeout
or retry wrapper is introduced.

### Validation plan

Monkeypatch each private family handler and assert every explicit branch independently,
then validate retained loader wiring and unchanged error/cancellation behavior. Run all
four declared commands before fresh implementation review.

### Handoff notes for the implementer

The historical implementation must retain the exact TODO, direct `match/case`, and
matching `_load_<family>` awaits. Release work changes only its declared
docs/version/lock/evidence paths; do not replace the removed mapping seam or add
deferred types/exceptions.

### Async contradiction log

None: user-locked direct-await/no-I/O/caller-cancellation baseline is unchanged; only
the internal dispatch/test seam is corrected.

## Public Contract / API Changes

- No new public API or public signature change.
- `ModelPool` remains package-root public; `LocalModelLoader` and family handlers stay
  private. Removal of `_route_mapping` is an intentional internal seam change only.

## Affected Files / Modules

- `src/async_model_gateway/model_runtime/model_pool/__init__.py`
- `src/async_model_gateway/model_runtime/model_pool/pool.py`
- `src/async_model_gateway/model_runtime/model_pool/_local_model_loader.py`
- `tests/model_runtime/model_pool/test_model_pool_package_surface.py`
- `tests/model_runtime/model_pool/test_model_pool.py`
- `tests/model_runtime/model_pool/test_local_model_loader.py`
- `README.md`
- `docs/architecture.md`
- `docs/specs/model-side-boundary.md`
- `docs/specs/core-abstractions-boundary.md`
- `docs/specs/canonical-input-boundary.md`
- `src/async_model_gateway/__version__.py`
- `pyproject.toml`
- `uv.lock`
- `plan/model-pool-local-loader-minimal-boundary/model-pool-local-loader-minimal-boundary.release.yaml`

## Test Plan

- Happy path: monkeypatch each private family handler with distinct async sentinel
  result and verify its corresponding `LoaderFamily` case only.
- Invalid input: non-artifact acquire input is TypeError; existing invalid artifact
  construction remains ValueError without a new exception class. Tests do not
  manufacture a non-`LoaderFamily` fallback input.
- Edge case: a PICKLE artifact path ending in `.onnx` still reaches `_load_pickle`.
- Regression: exact TODO remains; `_route_mapping` is absent; factory retention and
  ModelPool-only package export remain locked.
- Backward compatibility: root, umbrella, and model_artifact exports remain unchanged.
- Async safety: known default handlers raise NotImplementedError and generic failure /
  `asyncio.CancelledError` propagate unchanged.

## Validation Commands

```bash
uv run pytest --no-cov tests/model_runtime/model_pool -v
uv run pytest -v
uv run ruff check src tests plan/model-pool-local-loader-minimal-boundary
uv run pyright
```

## Risks

- A replacement injection seam or mapping lookup would make test and production
  dispatch diverge again.
- A catch, runtime fallback policy, or replacement exception around a handler would
  alter failure/cancellation semantics and undermine closed-enum exhaustiveness.
- Actual loading or typing abstraction would widen this bounded topic.

## Rollback Plan

- If the bounded release change must be rolled back before tagging, revert only the
  docs/version release commit; release evidence does not yet exist. Do not alter the
  merged model_pool source, tests, historical evidence, or `model_artifact`. If
  `v0.4.7` has already been pushed, stop for human release remediation rather than
  moving or deleting the tag; do not automatically revert the separate evidence commit.
