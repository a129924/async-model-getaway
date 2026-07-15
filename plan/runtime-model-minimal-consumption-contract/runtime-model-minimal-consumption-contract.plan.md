> Semantic warning: `analysis/runtime-model-minimal-consumption-contract/requirements.md` 與 `analysis/runtime-model-minimal-consumption-contract/technical-spec.md` 均不存在；本 plan 僅依已鎖定 contract，禁止擴張 scope。

# runtime-model-minimal-consumption-contract

## Goal / Outcome

在真實 local artifact I/O 前，建立具名、abstract、opaque 的 `LoadedRuntimeModel` consumption contract，使 `ModelPool.acquire()` 與 private local loader 不再以 `object` 作長期 public return contract；future `ModelExecution` 可於另一 topic 透過 non-public handoff 消費它。

## Scope

- **In scope:** abstract consumption contract、private local concrete implementation/factory、local acquisition return annotations、指定 fresh RED tests，以及 post-merge v0.5.0 docs/version metadata。
- **Out of scope:** real I/O、pickle security、execution/provider framework、lifecycle/cache、`ModelGateway`、registry、response cache、未列 paths。

## Locked Decisions

- **Correction supersedes the previous immutable-concrete-handle revision.** `LoadedRuntimeModel` 是使用 `ABC` 的 public abstract nominal consumption contract；不是 dataclass、value object、type alias、Protocol 或 Generic。唯一 public semantic 為 readonly abstract `loader_family: LoaderFamily`；它沒有 public constructor/raw payload/unwrap/invoke/lifecycle API。
- `LoadedRuntimeModel` 另定義 `_provider_runtime(self) -> object` 作 model-side non-public internal handoff，僅供 future `ModelExecution` topic；它不是 package-consumer public API。
- `loaded_runtime_model.py` 定義但不 export：`_LocalLoadedRuntimeModel` 與 `_create_loaded_runtime_model(*, loader_family: LoaderFamily, provider_model: object) -> LoadedRuntimeModel`。private concrete class 使用一般 `__init__` 保存 loader family/provider runtime；禁止 `__new__`、手寫 `__setattr__`、frozen dataclass、constructor token 與 immutable 宣稱。helper/private class 不進 `__all__`，tests 可 static import factory 作 internal seam，禁止 dynamic loading。
- `runtime_model` root 只 export `LoadedRuntimeModel`；root package 和 `model_runtime` umbrella 不 re-export。
- `ModelPool.acquire`、`LocalModelLoader.load`、三個 family handler 均 return `LoadedRuntimeModel`；保留 ModelPool-only export、private loader、retained loader、TypeError/ValueError、explicit match/case、`assert_never`、direct await、no-I/O `NotImplementedError`，generic failure/`CancelledError` 原樣傳播。
- `ModelArtifact`/`LoaderFamily` 仍是 consumed-only shared read contract；不加 `TypeVar`、`Generic`、`ModelArtifact[ProviderRuntimeT]` 或 `LoadedRuntimeModel[object]`，也不加 domain exception、dependency、timeout/retry/background task。
- D1 `non-trivial`；async-planning exempt，因僅收窄既有 direct-await return contract，沒有新 I/O/lifecycle/concurrency/timeout/cancellation decision。

## Boundaries / Exclusions

Planning actor 僅改三份 topic artifact；Tester 只寫 fresh RED/evidence；Implementer 僅做 approved paths；Reviewer 和 Human gate 不得由 Implementer 代替。任何 public `LocalModelLoader`、real loading、provider behavior、新 exception 或 path/contract drift，回到 `spec-and-plan-finalization`。

## Status / Allowed Transitions

- **Current:** `review-ready` (contract-correction revision)。既有 plan-review、human-check、RED、implementation-review、code-review artifacts 僅為已否決 immutable revision 的歷史 evidence，不得作為本 revision approval。
- canonical re-review loop：`approved -> creator-in-progress -> review-ready -> reviewer-in-progress -> approved|needs-rework`。
- complete transitions：`planned -> creator-in-progress -> review-ready -> reviewer-in-progress -> approved|needs-rework`；`approved -> creator-in-progress|publish-in-progress`；`publish-in-progress -> pr-open|merged`；`pr-open -> needs-rework|merged`；本 release topic `merged -> released`。
- 新 Plan-Reviewer `approved` 加 fresh Human `human-check` 才能 Tester 重新寫 RED evidence；fresh RED evidence 後才 Implementer correction；新的 implementation review 和 independent code review approved 才 PR；Human merge 後 fresh release human check 才 release。

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
| Runtime handle | `src/async_model_gateway/model_runtime/runtime_model/loaded_runtime_model.py` | Implementer | abstract contract、private concrete implementation 與 private factory |
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

1. **Tester** authors fresh replacement RED tests/evidence first, static-importing private factory; tests supersede immutable/direct-construction/mutation expectations and use no dynamic loading.
2. **Implementer** corrects runtime handle source/package export: public `ABC` contract, non-public `_provider_runtime()`, ordinary-`__init__` private local implementation, and exact private factory seam.
3. **Implementer** narrows `pool.py` return contract preserving validation/retention/direct await.
4. **Implementer** narrows private loader/handlers preserving dispatch/assert-never/no-I/O stubs.
5. **Implementer** runs validation and records truthful tracker progress.

## Validation / Acceptance Checks

- Fresh RED precedes production correction; tests use static private-factory import and cover abstract direct-instantiation rejection, factory return boundary/provenance, `_provider_runtime()` internal seam, opacity, annotations, exports, dispatch, and unchanged failures/cancellation.
- `LoadedRuntimeModel` has no public payload/lifecycle/execution API; `_provider_runtime()` is internal-only. `runtime_model` root exports only `LoadedRuntimeModel`; root/umbrella do not re-export it.
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

Human alone creates fresh release-human-check after explicit merge. Only then may
Implementer update exactly `README.md`, `docs/architecture.md`,
`docs/specs/model-side-boundary.md`, `docs/specs/core-abstractions-boundary.md`,
`src/async_model_gateway/__version__.py`, `pyproject.toml`, and `uv.lock`; validate
v0.5.0 consistency; create/push lightweight `v0.5.0` from that release commit; and
write `release.yaml` with version/tag/remote/no-publish evidence. These conditional
post-merge actions are not implementation-review completion steps.

## Open Questions / Unresolved Items

None.

## Goal

See canonical Goal / Outcome: typed abstract consumption contract before I/O.

## Non-goals

See canonical Scope: no I/O, execution, lifecycle, provider framework, cache, or adjacent owners.

## Current Context

See canonical Locked Decisions: current `object` annotations and locked private loader baseline.

## Requirements

See canonical Locked Decisions: abstract contract, private local implementation/factory, payload isolation, narrowed annotations, unchanged failures.

## Decisions

- Async-planning status: exempt — cite exemption evidence: 僅收窄既有 async direct-await return contract；不新增 I/O、resource lifecycle、concurrency、timeout、retry 或 cancellation policy。
  Module/API/error/typing decisions and exact helper seam are frozen in canonical Locked Decisions.

## Public Contract / API Changes

`LoadedRuntimeModel.loader_family: LoaderFamily` is the only public handle semantic. `_provider_runtime(self) -> object` is an internal model-side handoff, not a package-consumer API. `ModelPool.acquire(self, artifact: ModelArtifact) -> LoadedRuntimeModel` is the sole changed public signature.

## Affected Files / Modules

The canonical Artifact Paths table above is the complete exact path/owner/role contract. **Deleted:** None.

## Implementation Steps

Tester RED first, then the four pre-merge Implementer actions, exactly as defined in
canonical Implementation Steps and mirrored in `.step.md`; reviewer/Human gates and
conditional post-merge release remain outside implementation-review completion.

## Test Plan

### TestCase

- Happy: private factory-created handle preserves family and is typed as `LoadedRuntimeModel`.
- Invalid: non-artifact `TypeError`; invalid artifact `ValueError` unchanged.
- Edge: abstract contract cannot be directly instantiated; no public payload/invoke/close/unload; `_provider_runtime()` is exercised only through an internal static-import seam.
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

Payload leakage couples future execution to providers; public provider handoff, Protocol/alias/Generic/invoke/lifecycle expand architecture; changed direct-await failures alter cancellation semantics.

## Rollback Plan

Before merge revert listed source/tests/artifacts; before tag revert only release docs/version/lockfile; after tag use corrective topic and never retarget it.

## Open Questions

None.
