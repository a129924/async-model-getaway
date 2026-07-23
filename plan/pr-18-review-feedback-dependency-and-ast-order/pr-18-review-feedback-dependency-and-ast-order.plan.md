> Semantic warning: `analysis/pr-18-review-feedback-dependency-and-ast-order/requirements.md`
> 與 `analysis/pr-18-review-feedback-dependency-and-ast-order/technical-spec.md` 均不存在。
> 本 plan 依 PR #18 的兩個明確 review threads 與 Human 已鎖定 decisions 撰寫；不得
> 擴張為 runtime、API、architecture、documentation 或其他 PR feedback work。

# pr-18-review-feedback-dependency-and-ast-order

## Goal / Outcome

在正常 dev environment 中提供既有 ONNX Runtime test dependency，讓 CI 回復 plain
frozen dev sync，並使 `_provider_runtime_call_paths()` 的 AST scan 回傳順序可重現，以
完成 PR #18 的兩個指定 review threads。另以同 topic 的 bounded validation-hygiene
retrofit 修正此 topic human-check 的 missing terminal LF，讓全量 pre-commit 可通過而不
改變已核准 gate semantics。

## Scope

### In scope

- 處理 PR #18 thread
  [`discussion_r3629182514`](https://github.com/a129924/async-model-getaway/pull/18#discussion_r3629182514)：
  保留 published `[project.optional-dependencies].onnx` 的既有
  `onnxruntime>=1.22.0,<1.22.1` constraint，並將同一 constraint 加入 dev group。
- 更新 `uv.lock`，使 direct dev-group dependency metadata 與 `pyproject.toml` 一致，
  不升級或變更既有 resolved package versions。
- 將 `.github/workflows/ci.yml` 的 `Sync dependencies` command 回復為
  `uv sync --frozen --group dev`；CI 不再以 `--extra onnx` 補足 test dependency。
- 處理 PR #18 thread
  [`discussion_r3629184495`](https://github.com/a129924/async-model-getaway/pull/18#discussion_r3629184495)：
  僅在 `_provider_runtime_call_paths()` AST helper 對 collected `Path` values 做
  deterministic sort。
- 完成此 topic 的 plan/step，並在 implementation 前取得 fresh plan-review 與 Human
  `cleared_for: implement-plan` gate。
- 處理 CI failure 所揭露的 same-topic validation hygiene：唯一 remediation target 是
  `plan/pr-18-review-feedback-dependency-and-ast-order/pr-18-review-feedback-dependency-and-ast-order.human-check.json`。
  Human 只可在其既有 terminal `}` 後補一個 LF；parsed JSON 必須仍精確為
  `{"cleared_for":"implement-plan"}`。
- 由 fresh Plan-Reviewer 重新核准 amended plan、Human 寫入 exact final-LF gate，再由
  validation-only Reviewer 執行 pre-commit all-files 與 diff/JSON semantic guard。

### Out of scope

- `onnxruntime` optional-extra constraint 的移除、版本變更、移至 `[project.dependencies]`
  或新增其他 dependency。
- 任何 runtime source、public API、`ModelExecution` behavior、ONNX acquisition、async
  semantics、package export 或 architecture 變更。
- README、architecture/spec documentation、release/version、CI trigger/action/Python
  version/其他 validation command 的修改。
- 新增或重設 test scenario；只修正既有 AST helper 的 deterministic return ordering。
- 在 PR #18 reply、resolve、re-request review、commit、push、open/update PR；這些動作
  需要 implementation/review gates 完成後的另一個 explicit Human permission。
- validation-hygiene retrofit 的任何 `pyproject.toml`、`uv.lock`、CI、test、source、docs
  或 PR-state change；這些 original repair paths 只作 historical ReadOnly evidence。

## Locked Decisions

- D1 verdict: `trivial`。這是 existing dependency placement 與 existing test helper
  ordering 的 bounded review-feedback repair；不建立 `*.spec.md` 或 fresh RED artifact。
- `onnxruntime>=1.22.0,<1.22.1` 保留在 published `onnx` optional extra，並以完全相同
  constraint 同時列入 `[dependency-groups].dev`。
- CI 的唯一 allowed change 是 `Sync dependencies` 回復為
  `uv sync --frozen --group dev`；不得保留或新增 `--extra onnx`，不得改其他 CI line。
- AST deterministic repair 只發生於
  `tests/model_runtime/model_execution/test_model_execution_package_surface.py` 的
  `_provider_runtime_call_paths()`；在 return 前排序 collected relative `Path` list，
  不改 scan predicate、assertion target 或 production source。
- 無 public API、interface、runtime behavior、error handling、typing contract 或 async
  behavior change；stable-library intent 與 release intent 均明確缺席。
- Fresh Plan-Reviewer `approved` verdict 與 Human `cleared_for: implement-plan` 是
  implementation 前的必要 gates。PR reply/resolve 不是 implementation authorization 的
  一部分，必須另有 explicit Human permission。
- Validation-hygiene retrofit D1 verdict: `trivial`。舊 plan-review、Human
  implementation clearance、implementation-review 與 code-review 不涵蓋新增的
  human-check final-LF path，均不得當作本 retrofit gate；必須 fresh Plan-Reviewer
  `approved`，再由 Human 重寫 exact gate file 並加入唯一 terminal LF。
- This retrofit's sole remediation is the human-owned
  `pr-18-review-feedback-dependency-and-ast-order.human-check.json`. Its only byte
  change is one terminal LF after the existing `}`; JSON values, key order,
  whitespace before `}`, and all non-final bytes are immutable. Parsed JSON remains
  exactly `{"cleared_for":"implement-plan"}`.
- After Human writes that gate, a validation-only Reviewer runs `pre-commit run
  --all-files`, `git diff --check`, raw diff inspection, and parsed JSON/terminal-LF
  guards. No Implementer write is authorized for this retrofit.

## Boundaries / Exclusions

- Plan-Creator 只建立/更新 plan 與 step；Plan-Reviewer writes fresh plan-review verdict；
  Human writes the exact final-LF human-check gate；validation-only Reviewer writes its
  review evidence after checks. No Implementer write is authorized for this retrofit.
- `pyproject.toml`、`uv.lock`、`.github/workflows/ci.yml`、
  `tests/model_runtime/model_execution/test_model_execution_package_surface.py` are
  Historical ReadOnly original-repair evidence; no Implementer writable path exists for
  this final-LF retrofit.
- 所有未列 Artifact Path 的 source、test、docs、CI、planning artifact 與 PR state
  都是 ReadOnly；需要額外 path 或 contract change 時回到
  `spec-and-plan-finalization`。
- 不得以 CI-only extra、lazy-import suppression、test skip 或 order-insensitive assertion
  來迴避兩個 review findings。
- 不得重用本 amendment 前的 plan-review、Human clearance、implementation-review 或
  code-review 作為 final-LF path 的 approval，也不得由 Plan-Creator 或 Reviewer 代替
  Human 寫入 gate file。

## Status / Allowed Transitions

- **Current**: `review-ready`；CI failure 新增 human-check terminal-LF scope。先前
  `pr-comment` state 的 plan-review、Human implementation clearance 和後續 review
  evidence 均不適用；等待 fresh independent Plan-Reviewer verdict。
- **Execution model**: `spec-and-plan-finalization -> implement-plan -> pr-comment ->
  pr-comment-review-pr-comments-and-fix`；本 topic 在 `merged` 停止，沒有 `release`
  workflow。
- **Allowed transitions**:
  - `review-ready` -> `reviewer-in-progress`
  - `reviewer-in-progress` -> `approved`
  - `reviewer-in-progress` -> `needs-rework`
  - `needs-rework` -> `creator-in-progress`
  - `approved` -> `publish-in-progress`
  - `publish-in-progress` -> `pr-open`
  - `pr-open` -> `needs-rework`
  - `pr-open` -> `merged`

Routing notes:

- Human must write the exact final-LF `cleared_for: implement-plan` gate only after the
  declared plan-review artifact records fresh `approved`.
- D1 is trivial: no fresh spec or RED artifact is required. This retrofit has no
  Implementer work; Human's byte-only gate write is followed by validation-only review.
- PR reply/resolve is deferred beyond code review and requires separate Human permission;
  this plan does not infer that authorization from the implementation gates.

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/pr-18-review-feedback-dependency-and-ast-order/pr-18-review-feedback-dependency-and-ast-order.plan.md` | Plan-Creator | Repo-visible execution contract |
| Step tracker | `plan/pr-18-review-feedback-dependency-and-ast-order/pr-18-review-feedback-dependency-and-ast-order.step.md` | Plan-Creator, then phase owner | Workflow and implementation progress |
| Plan review | `plan/pr-18-review-feedback-dependency-and-ast-order/pr-18-review-feedback-dependency-and-ast-order.plan-review.json` | Plan-Reviewer | Fresh independent verdict for the final-LF scope |
| Human check / sole remediation | `plan/pr-18-review-feedback-dependency-and-ast-order/pr-18-review-feedback-dependency-and-ast-order.human-check.json` | Human | Rewrite exact cleared gate with only one terminal LF; no semantic/non-final byte change |
| Validation-only review | `plan/pr-18-review-feedback-dependency-and-ast-order/pr-18-review-feedback-dependency-and-ast-order.implementation-review.yaml` | Reviewer | Fresh pre-commit and raw-diff/JSON-semantic validation verdict |
| Code review | `plan/pr-18-review-feedback-dependency-and-ast-order/pr-18-review-feedback-dependency-and-ast-order.code-review.yaml` | Historical ReadOnly | Original PR #18 repair review; not approval for final-LF scope |
| Project dependency declaration | `pyproject.toml` | Historical ReadOnly | Original PR #18 dependency repair evidence; no retrofit write |
| Resolved dependency metadata | `uv.lock` | Historical ReadOnly | Original PR #18 lock repair evidence; no retrofit write |
| CI workflow | `.github/workflows/ci.yml` | Historical ReadOnly | Original PR #18 CI repair evidence; no retrofit write |
| AST ownership test | `tests/model_runtime/model_execution/test_model_execution_package_surface.py` | Historical ReadOnly | Original PR #18 deterministic-sort evidence; no retrofit write |

### ReadOnly

- All paths except the exact Human-owned human-check remediation target, including
  `src/`, `pyproject.toml`, `uv.lock`, `.github/workflows/ci.yml`, tests, README,
  `docs/`, other topic artifacts, PR state, and all other CI workflow lines.

### Written

- Plan-Creator writes revised plan/step; Plan-Reviewer writes fresh plan-review;
  Human writes the exact final-LF human-check; validation-only Reviewer writes fresh
  implementation-review evidence. No other retrofit write is permitted.

### Updated

- For this retrofit, only the exact Human-owned human-check path may change after fresh
  plan review; it receives only the terminal LF. Original four implementation paths are
  Historical ReadOnly.

### Deleted

- None. Any deleted path or removed dependency is scope drift.

## Implementation Steps

1. Treat the prior dependency, lock, CI, and AST-helper repair as Historical ReadOnly
   evidence; do not write its four implementation paths for this retrofit.
2. After fresh Plan-Reviewer `approved`, Human writes
   `plan/pr-18-review-feedback-dependency-and-ast-order/pr-18-review-feedback-dependency-and-ast-order.human-check.json`
   with its existing JSON semantics and exactly one terminal LF after `}`.
3. Validation-only Reviewer runs pre-commit all-files plus raw diff, terminal-LF, and
   parsed-JSON guards; it records a fresh verdict and does not modify source,
   dependency, lock, workflow, test, docs, or PR state.

## Validation / Acceptance Checks

- Prior original repair diffs remain preserved as Historical ReadOnly; the sole new
  remediation diff is the declared Human-owned human-check path.
- Its only byte representation change is the missing-final-newline marker removal:
  exactly one terminal LF is present after `}`, with no other byte change.
- Parsing that file yields exactly `{"cleared_for":"implement-plan"}`.
- No source, dependency, lock, workflow, test, docs, PR response, commit, or push is
  performed for this retrofit.
- Run:

```bash
uv run --no-sync pre-commit run --all-files
git diff --check
git diff -- plan/pr-18-review-feedback-dependency-and-ast-order/pr-18-review-feedback-dependency-and-ast-order.human-check.json
uv run --no-sync python -c 'import json; from pathlib import Path; path = Path("plan/pr-18-review-feedback-dependency-and-ast-order/pr-18-review-feedback-dependency-and-ast-order.human-check.json"); raw = path.read_bytes(); assert raw.endswith(b"\n"); assert json.loads(raw) == {"cleared_for": "implement-plan"}'
```

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

No release workflow required. After merge, stop. PR #18 reply/resolve may occur only
after a separate explicit Human permission; it is not an automatic post-merge action.

## Open Questions / Unresolved Items

None. The two bound threads and all implementation decisions are explicit.

## Python Implementation

### Goal

Resolve the two bounded PR #18 findings without changing Python runtime behavior or any
public contract, then correct the same-topic human-check terminal-LF hygiene failure
without changing its cleared gate semantics.

### Non-goals

- No production Python source or public API modification.
- No new dependency/version, optional-extra removal, lockfile-wide refresh, or CI policy
  change.
- No new test scenario, dynamic module loading, or assertion semantic change.
- No README/docs/architecture/release/PR reply or resolve action.
- No source/dependency/lock/workflow/test modification for the final-LF retrofit.

### Current Context

- `pyproject.toml` publishes `onnxruntime>=1.22.0,<1.22.1` through the `onnx` optional
  extra, while the dev group has the ONNX model fixture but not ONNX Runtime.
- `.github/workflows/ci.yml` currently compensates with `--extra onnx` on frozen dev
  sync.
- `_provider_runtime_call_paths()` appends results from `Path.rglob("*.py")` without
  sorting, so list equality can vary by filesystem traversal order.
- The original PR #18 repair is complete, but the declared human-check currently ends
  at `}` without a terminal LF and fails full pre-commit text-file hygiene.

### Requirements

1. Normal `uv sync --frozen --group dev` installs an importable ONNX Runtime.
2. The published `onnx` extra remains a supported independent installation surface with
   its exact existing ONNX Runtime constraint.
3. CI sync does not request an optional extra.
4. The AST helper order is deterministic and its ownership assertion stays unchanged.
5. All declared normal-dev, focused, full, static, lint, pre-commit, and diff checks
   pass.
6. The final-LF retrofit changes only the Human-owned gate file; parsing remains exactly
   `{"cleared_for":"implement-plan"}`.

### Decisions

- Async-planning status: exempt — cite exemption evidence: this topic changes dependency
  metadata, one CI sync flag, and deterministic ordering in a test helper; it introduces
  no async boundary, lifecycle, concurrency, failure, cancellation, or timeout policy.
- Module/package placement: `pyproject.toml`, `uv.lock`, `.github/workflows/ci.yml`,
  and the existing AST helper test only; no package module receives code.
- New public API: no.
- Interface changes: no.
- Breaking changes allowed: no; the published optional extra remains intact and normal
  dev setup becomes complete for existing tests.
- New dependencies: no new package or version; the existing ONNX Runtime constraint is
  additionally declared in the dev group.
- Error handling strategy: no runtime error path changes; uv resolution/import failures
  remain command failures and existing test assertions remain unchanged.
- Typing strategy: retain `list[Path]` and `Path` values; use the standard deterministic
  sort without `Any`, casts, or suppression.
- Validation-hygiene ownership: Human alone appends the terminal LF after fresh plan
  approval; validation-only Reviewer confirms raw representation and parsed semantics.

### Public Contract / API Changes

No public API changes. The published `onnx` optional extra remains available with the
same ONNX Runtime constraint; dev installation metadata only gains the same existing
test-runtime dependency.

### Affected Files / Modules

Historical ReadOnly original-repair files:

- `pyproject.toml`
- `uv.lock`
- `.github/workflows/ci.yml`
- `tests/model_runtime/model_execution/test_model_execution_package_surface.py`

Current sole remediation target:

- `plan/pr-18-review-feedback-dependency-and-ast-order/pr-18-review-feedback-dependency-and-ast-order.human-check.json`

Planning/review artifacts to inspect:

- `plan/pr-18-review-feedback-dependency-and-ast-order/pr-18-review-feedback-dependency-and-ast-order.plan.md`
- `plan/pr-18-review-feedback-dependency-and-ast-order/pr-18-review-feedback-dependency-and-ast-order.step.md`

### Implementation Steps

1. Preserve the completed original-repair files without writing them.
2. After fresh plan-review, Human adds only the terminal LF to the declared human-check
   file while preserving parsed `cleared_for: implement-plan` semantics.
3. Validation-only Reviewer runs pre-commit all-files and raw diff/JSON semantic guards;
   it records a verdict without PR thread actions.

### Test Plan

Validation target: `plan/pr-18-review-feedback-dependency-and-ast-order/pr-18-review-feedback-dependency-and-ast-order.human-check.json`

Test cases:

- Happy path: full pre-commit passes after the Human-owned terminal LF is present.
- Invalid input: parsed JSON must not differ from `{"cleared_for":"implement-plan"}`.
- Edge case: the only raw diff representation is removal of the missing-final-newline
  marker; no whitespace before `}` or other byte may change.
- Regression: original dependency/CI/AST repair paths remain unchanged during this
  retrofit.
- Backward compatibility: human gate remains cleared for implementation with identical
  parsed semantics.

### Validation Commands

```bash
uv run --no-sync pre-commit run --all-files
git diff --check
git diff -- plan/pr-18-review-feedback-dependency-and-ast-order/pr-18-review-feedback-dependency-and-ast-order.human-check.json
uv run --no-sync python -c 'import json; from pathlib import Path; path = Path("plan/pr-18-review-feedback-dependency-and-ast-order/pr-18-review-feedback-dependency-and-ast-order.human-check.json"); raw = path.read_bytes(); assert raw.endswith(b"\n"); assert json.loads(raw) == {"cleared_for": "implement-plan"}'
```

### Risks

- Adding a non-identical dev constraint could create resolver drift or silently change
  published optional-extra behavior.
- Editing more than the CI sync line could alter CI policy instead of addressing the
  dependency placement finding.
- Sorting a different collection or changing the AST predicate could weaken ownership
  governance rather than only remove filesystem-order nondeterminism.
- Reformatting the human-check file or changing its gate value would silently alter the
  Human decision instead of making the bounded terminal-LF repair.

### Rollback Plan

For the final-LF retrofit, remove only the terminal LF from the declared human-check
file through its dedicated change. Do not revert or rewrite the historical original
repair paths or alter PR thread state as part of rollback.

### Open Questions

None.
