> Semantic warning: `analysis/runtime-model-minimal-consumption-contract/requirements.md` 與 `analysis/runtime-model-minimal-consumption-contract/technical-spec.md` 均不存在；本 plan 僅依已鎖定 contract，禁止擴張 scope。

# runtime-model-minimal-consumption-contract

## Goal / Outcome

在真實 local artifact I/O 前，建立具名、immutable、opaque 的 `LoadedRuntimeModel` contract，使 `ModelPool.acquire()` 與 private local loader 不再以 `object` 作長期 public return contract；future `ModelExecution` 可於另一 topic 消費它。

## Scope

- **In scope:** minimal handle、local acquisition return annotations、指定 fresh RED tests，以及 post-merge v0.5.0 docs/version metadata。
- **Out of scope:** real I/O、pickle security、execution/provider framework、lifecycle/cache、`ModelGateway`、registry、response cache、未列 paths。

## Locked Decisions

- `LoadedRuntimeModel` 是 concrete nominal immutable handle，唯一 public semantic 為 readonly `loader_family: LoaderFamily`；不是 alias 或 public Protocol，沒有 public constructor/raw payload/unwrap/invoke/lifecycle API。
- `loaded_runtime_model.py` 定義但不 export：`_create_loaded_runtime_model(*, loader_family: LoaderFamily, provider_model: object) -> LoadedRuntimeModel`。handle 私有 `__loader_family` 與 `__provider_model` slots；直接 construction/mutation 均拒絕。helper 不進 `__all__`，tests 可 static import，禁止 dynamic loading。
- `runtime_model` root 只 export `LoadedRuntimeModel`；root package 和 `model_runtime` umbrella 不 re-export。
- `ModelPool.acquire`、`LocalModelLoader.load`、三個 family handler 均 return `LoadedRuntimeModel`；保留 ModelPool-only export、private loader、retained loader、TypeError/ValueError、explicit match/case、`assert_never`、direct await、no-I/O `NotImplementedError`，generic failure/`CancelledError` 原樣傳播。
- `ModelArtifact`/`LoaderFamily` 仍是 consumed-only shared read contract；不加 domain exception、dependency、timeout/retry/background task。
- D1 `non-trivial`；async-planning exempt，因僅收窄既有 direct-await return contract，沒有新 I/O/lifecycle/concurrency/timeout/cancellation decision。

## Boundaries / Exclusions

Planning actor 僅改三份 topic artifact；Tester 只寫 fresh RED/evidence；Implementer 僅做 approved paths；Reviewer 和 Human gate 不得由 Implementer 代替。任何 public `LocalModelLoader`、real loading、provider behavior、新 exception 或 path/contract drift，回到 `spec-and-plan-finalization`。

## Status / Allowed Transitions

- **Current:** `reviewer-in-progress`。
- canonical re-review loop：`reviewer-in-progress -> needs-rework -> creator-in-progress -> review-ready -> reviewer-in-progress`。
- complete transitions：`planned -> creator-in-progress -> review-ready -> reviewer-in-progress -> approved|needs-rework`；`approved -> creator-in-progress|publish-in-progress`；`publish-in-progress -> pr-open|merged`；`pr-open -> needs-rework|merged`；本 release topic `merged -> released`。
- Plan-Reviewer `approved` 加 Human `human-check` 才能 Tester RED；RED evidence 後才 Implementer；implementation review 和 independent code review approved 才 PR；Human merge 後 fresh release human check 才 release。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/runtime-model-minimal-consumption-contract/runtime-model-minimal-consumption-contract.plan.md` | Plan-Creator | execution contract |
| Python spec | `plan/runtime-model-minimal-consumption-contract/runtime-model-minimal-consumption-contract.spec.md` | Plan-Creator | behavior contract |
| Step tracker | `plan/runtime-model-minimal-consumption-contract/runtime-model-minimal-consumption-contract.step.md` | Implementer | progress tracking |
| Plan review | `plan/runtime-model-minimal-consumption-contract/runtime-model-minimal-consumption-contract.plan-review.json` | Plan-Reviewer | plan verdict |
| Human check | `plan/runtime-model-minimal-consumption-contract/runtime-model-minimal-consumption-contract.human-check.json` | Human | implementation clearance |
| RED evidence | `plan/runtime-model-minimal-consumption-contract/runtime-model-minimal-consumption-contract.red-tests.yaml` | Tester | RED verdict |
| Implementation review | `plan/runtime-model-minimal-consumption-contract/runtime-model-minimal-consumption-contract.implementation-review.yaml` | Reviewer | conformance verdict |
| Code review | `plan/runtime-model-minimal-consumption-contract/runtime-model-minimal-consumption-contract.code-review.yaml` | Reviewer | quality verdict |
| Release human check | `plan/runtime-model-minimal-consumption-contract/runtime-model-minimal-consumption-contract.release-human-check.json` | Human | release clearance |
| Release evidence | `plan/runtime-model-minimal-consumption-contract/runtime-model-minimal-consumption-contract.release.yaml` | Implementer | release/tag evidence |
| Runtime boundary | `src/async_model_gateway/model_runtime/runtime_model/__init__.py` | Implementer | handle-only export |
| Runtime handle | `src/async_model_gateway/model_runtime/runtime_model/loaded_runtime_model.py` | Implementer | opaque handle/private seam |
| Pool | `src/async_model_gateway/model_runtime/model_pool/pool.py` | Implementer | public return type |
| Private loader | `src/async_model_gateway/model_runtime/model_pool/_local_model_loader.py` | Implementer | private return types |
| Runtime handle tests | `tests/model_runtime/runtime_model/test_loaded_runtime_model.py` | Tester | handle semantics |
| Runtime surface tests | `tests/model_runtime/runtime_model/test_runtime_model_package_surface.py` | Tester | export regression |
| Pool tests | `tests/model_runtime/model_pool/test_model_pool.py` | Tester | contract/failure regression |
| Loader tests | `tests/model_runtime/model_pool/test_local_model_loader.py` | Tester | dispatch/no-I/O regression |
| Pool surface tests | `tests/model_runtime/model_pool/test_model_pool_package_surface.py` | Tester | signature regression |
| Release README | `README.md` | Implementer | post-merge wording |
| Release architecture | `docs/architecture.md` | Implementer | typed boundary wording |
| Release model-side spec | `docs/specs/model-side-boundary.md` | Implementer | typed boundary wording |
| Release core spec | `docs/specs/core-abstractions-boundary.md` | Implementer | type ownership wording |
| Release version | `src/async_model_gateway/__version__.py` | Implementer | v0.5.0 |
| Release metadata | `pyproject.toml` | Implementer | v0.5.0 |
| Release lockfile | `uv.lock` | Implementer | v0.5.0 metadata |
| ReadOnly umbrella | `src/async_model_gateway/model_runtime/__init__.py` | No change | preserve empty export |
| ReadOnly artifact root | `src/async_model_gateway/model_runtime/model_artifact/__init__.py` | No change | preserve shared export |
| ReadOnly artifact model | `src/async_model_gateway/model_runtime/model_artifact/artifact.py` | No change | preserve contract |
| ReadOnly family | `src/async_model_gateway/model_runtime/model_artifact/loader_family.py` | No change | preserve vocabulary |
| ReadOnly package root | `src/async_model_gateway/__init__.py` | No change | preserve root export |
| ReadOnly family test | `tests/model_runtime/model_artifact/test_loader_family.py` | No change | preserve baseline |
| ReadOnly artifact test | `tests/model_runtime/model_artifact/test_model_artifact.py` | No change | preserve baseline |
| ReadOnly artifact surface | `tests/model_runtime/model_artifact/test_model_artifact_package_surface.py` | No change | preserve export |
| ReadOnly canonical spec | `docs/specs/canonical-input-boundary.md` | No change | out of scope |
| ReadOnly orchestrator spec | `docs/specs/orchestrator-boundary.md` | No change | out of scope |

## Stable library metadata

- README row: release phase states only that `LoadedRuntimeModel` is minimal typed consumption contract; no real I/O/execution claim.
- VERSION bump: `0.4.7 -> 0.5.0` in `src/async_model_gateway/__version__.py`, `pyproject.toml`, `uv.lock`.
- timing/rationale: Human merge plus fresh release human check; public annotation narrowing needs traceable promotion, and merge is not release.

## Implementation Steps

1. **Tester** authors fresh RED tests/evidence first, static-importing private helper; no dynamic loading.
2. **Implementer** adds runtime handle source/package export with exact helper/private seam.
3. **Implementer** narrows `pool.py` return contract preserving validation/retention/direct await.
4. **Implementer** narrows private loader/handlers preserving dispatch/assert-never/no-I/O stubs.
5. **Implementer** runs validation and records truthful tracker progress.
6. **Implementer**, after Human merge/release check, updates only seven release docs/version paths and validates v0.5.0.
7. **Implementer** creates/pushes lightweight `v0.5.0` and writes release evidence; no GitHub Release/publish.

## Validation / Acceptance Checks

- Fresh RED precedes source; tests use static private-helper import and cover handle provenance/immutability/opacity, annotations, exports, dispatch, and unchanged failures/cancellation.
- Handle has no payload/lifecycle/execution API; root/umbrella do not re-export it.
- All declared commands pass; no artifact outside the table changes.

## Reviewer Handoff

```json
{
  "verdict": "approved | needs-rework",
  "blocking_issues": [{"issue": "string", "file": "string", "fix": "string"}],
  "copilot_feedback_triage": {
    "ADDRESS": [{"comment": "string", "location": "string", "why": "string"}],
    "DISCUSS": [{"comment": "string", "optional": true, "why": "string"}],
    "SKIP": [{"comment": "string", "why": "string"}]
  }
}
```

## Post-merge / release actions

Human alone creates fresh release-human-check after explicit merge. Only then may Implementer update declared release paths, validate, create/push lightweight `v0.5.0`, and write `release.yaml` with version/tag/remote/no-publish evidence.

## Open Questions / Unresolved Items

None.

## Goal

See canonical Goal / Outcome: typed opaque handle before I/O.

## Non-goals

See canonical Scope: no I/O, execution, lifecycle, provider framework, cache, or adjacent owners.

## Current Context

See canonical Locked Decisions: current `object` annotations and locked private loader baseline.

## Requirements

See canonical Locked Decisions: handle-only export, narrowed annotations, payload isolation, unchanged failures.

## Decisions

- Async-planning status: exempt — cite exemption evidence: 僅收窄既有 async direct-await return contract；不新增 I/O、resource lifecycle、concurrency、timeout、retry 或 cancellation policy。
  Module/API/error/typing decisions and exact helper seam are frozen in canonical Locked Decisions.

## Public Contract / API Changes

`LoadedRuntimeModel.loader_family: LoaderFamily` is the only public handle semantic; `ModelPool.acquire(self, artifact: ModelArtifact) -> LoadedRuntimeModel` is the sole changed public signature.

## Affected Files / Modules

The canonical Artifact Paths table above is the complete exact path/owner/role contract. **Deleted:** None.

## Implementation Steps

Tester RED first, then the six Implementer actions, exactly as defined in canonical Implementation Steps and mirrored in `.step.md`; reviewer/Human gates are not Implementer rows.

## Test Plan

### TestCase

- Happy: helper-created handle preserves family.
- Invalid: non-artifact `TypeError`; invalid artifact `ValueError` unchanged.
- Edge: immutable handle, no payload/invoke/close/unload.
- Regression: family-only dispatch, path independence, no-I/O stubs, `assert_never`, narrow exports.
- Failure/backward compatibility: handler failure and cancellation propagate; no root/umbrella export.

## Validation Commands

```bash
uv run pytest --no-cov tests/model_runtime/runtime_model tests/model_runtime/model_pool -v
uv run pytest -v
uv run ruff check src tests plan/runtime-model-minimal-consumption-contract
uv run pyright
uv lock --check
```

Release-only: `rg -n '0\.5\.0' README.md pyproject.toml src/async_model_gateway/__version__.py uv.lock`.

## Risks

Payload leakage couples future execution to providers; Protocol/alias/invoke/lifecycle expands architecture; changed direct-await failures alter cancellation semantics.

## Rollback Plan

Before merge revert listed source/tests/artifacts; before tag revert only release docs/version/lockfile; after tag use corrective topic and never retarget it.

## Open Questions

None.
