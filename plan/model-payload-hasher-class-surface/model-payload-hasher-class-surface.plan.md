> Semantic warning: `analysis/model-payload-hasher-class-surface/requirements.md`
> and `analysis/model-payload-hasher-class-surface/technical-spec.md` were not
> found at authoring time. This plan is authored from repo exploration and the
> explicit topic request only.

# model-payload-hasher-class-surface

## Goal / Outcome

- Replace the function-first public surface for the bounded `model-payload`
  hashing core with a class-first public owner:
  `ModelPayloadHasher.hash_model_payload(self, model_payload: dict[str, JSONLike]) -> str`.
- When this topic is complete, the repository exposes the canonical hashing
  surface from `async_model_gateway.model_registry.model_payload` through
  `ModelPayloadHasher`, removes the standalone public function, preserves the
  existing hashing semantics, and keeps the change bounded to the hashing core
  plus the repo-visible documents that describe that public surface.

## Scope

- **In scope**:
  - Add the bounded follow-up topic plan, step tracking artifact, behavior
    spec, repo-visible plan-review artifact, RED-test artifact, and
    implementation-review artifact for
    `model-payload-hasher-class-surface`.
  - Update the bounded hashing implementation and tests in
    `src/async_model_gateway/model_registry/model_payload/canonical_hash.py`,
    `src/async_model_gateway/model_registry/model_payload/__init__.py`, and
    `tests/model_registry/model_payload/test_canonical_hash.py`.
  - Update repo-visible documents that explicitly describe the hashing public
    surface in `README.md`, `docs/architecture.md`,
    `docs/specs/canonical-input-boundary.md`, and
    `docs/specs/model-side-boundary.md`.
  - Insert `create worktree` as the operational preflight before
    `implement-plan` for this topic only.

- **Out of scope**:
  - Any change to `ResponseCache`, `orchestrator`, `ModelPool`, `ModelGateway`,
    registry freshness flow, cache-key wiring, or runtime-model acquisition.
  - Any change to canonicalization rules, semantic-equivalence handling,
    loader inference, or hashing algorithm details.
  - Any hierarchy, ABC, `Protocol`, strategy, DI, dual-surface compatibility
    wrapper, or extra public API beyond the single class-first owner.

## Locked Decisions

- This topic is not a stable-library topic and does not declare release-facing
  timing. `## Stable library metadata` is intentionally absent.
- This topic explicitly adopts the Python planning extension path.
- Async-planning status: exempt — the change stays inside synchronous hashing,
  tests, and docs updates with no async boundary, lifecycle, or concurrency
  behavior.
- D1 verdict: `non-trivial` — the topic changes an existing public contract,
  adds a new public class owner, removes the previous function-first public
  surface, and requires companion `*.step.md` and `*.spec.md` artifacts.
- The only public owner added by this topic is `ModelPayloadHasher`.
- `ModelPayloadHasher` is a single concrete class with one public instance
  method:
  `hash_model_payload(self, model_payload: dict[str, JSONLike]) -> str`.
- The standalone public function `hash_model_payload(...)` is removed and is
  not retained as a compatibility wrapper.
- `async_model_gateway.model_registry.model_payload` may re-export only
  `ModelPayloadHasher`; `model_registry/__init__.py` must not re-export the
  hashing surface.
- Hashing behavior stays unchanged: recursive nested-dict canonicalization,
  list-order significance, scalar non-normalization, SHA-256 lowercase hex
  output, and `TypeError` fail-closed behavior for unsupported types.
- `create worktree` is a required operational preflight after plan approval and
  before `implement-plan`, but it is not a repo-level canonical workflow phase.
- Dispatchable repo-local agent surfaces remain only `planner`,
  `implementer`, and `reviewer`; `Plan-creator`, `Plan-reviewer`,
  `Worktree-manager`, `Code-Implementer`, `Code-Tester`, and `Code-reviewer`
  are aliases or workflow lanes, not additional agent surfaces.

## Boundaries / Exclusions

- The planning actor authors or revises only repo-visible planning artifacts
  for this topic.
- The implementer may change only the exact implementation, test, document, and
  planning artifact paths declared in `## Artifact Paths`.
- The reviewer validates contract adherence and later gate evidence; the
  reviewer does not implement fixes or widen scope.
- The worktree-manager capability is used only to create or inspect the managed
  task worktree; it does not authorize branch reuse, removal, or release by
  implication.
- This topic does not rewrite repo-level workflow names, status names, or gate
  semantics beyond topic-local routing notes.

## Status / Allowed Transitions

- **Current**: `approved`
- **Execution model**: follow
  `spec-and-plan-finalization -> implement-plan -> pr-comment -> pr-comment-review-pr-comments-and-fix`;
  stop at `merged` because this topic does not use the conditional `release`
  workflow.
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

- `spec-and-plan-finalization` completes only after the repo-visible topic plan
  exists, the repo-visible plan-review artifact records `approved`, and the
  repo-visible `human check` is explicitly passed.
- For this topic, the repo-visible `human check` is satisfied by the recorded
  human direction to implement the approved follow-up plan on `2026-06-19`.
- After `approved` plus `human check`, `create worktree` is a required
  operational preflight before any implementation work begins.
- `create worktree` does not authorize `release worktree`, `remove worktree`,
  or branch reuse by implication.
- RED test authoring is the first mandatory Python subphase inside
  `implement-plan`.
- `python-implementation-review` must be complete before the topic may enter
  `pr-comment`.
- Any scope change to the public owner, method signature, import surface,
  canonicalization rules, or implementation artifact paths must return to
  `spec-and-plan-finalization`.

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/model-payload-hasher-class-surface/model-payload-hasher-class-surface.plan.md` | Planning actor | Repo-visible execution contract for this follow-up topic |
| Topic step tracking | `plan/model-payload-hasher-class-surface/model-payload-hasher-class-surface.step.md` | Implementer | Repo-visible implementer-progress companion artifact |
| Topic behavior spec | `plan/model-payload-hasher-class-surface/model-payload-hasher-class-surface.spec.md` | Planning actor | Non-trivial Python behavior contract for TDD and later review |
| Plan review artifact | `plan/model-payload-hasher-class-surface/model-payload-hasher-class-surface.plan-review.json` | Reviewer | Repo-visible planning gate verdict |
| RED test artifact | `plan/model-payload-hasher-class-surface/model-payload-hasher-class-surface.red-tests.yaml` | Implementer | Repo-visible TDD gate evidence produced during `implement-plan` |
| Implementation review artifact | `plan/model-payload-hasher-class-surface/model-payload-hasher-class-surface.implementation-review.yaml` | Reviewer | Repo-visible implementation-review gate evidence |
| Project summary | `README.md` | Implementer | Repo-visible first-read document that must describe the class-first hashing owner accurately |
| Architecture summary | `docs/architecture.md` | Implementer | Repo-visible architecture summary aligned to the class-first hashing owner |
| Canonical input boundary spec | `docs/specs/canonical-input-boundary.md` | Implementer | Repo-visible spec that must describe the class-first hashing owner accurately |
| Model side boundary spec | `docs/specs/model-side-boundary.md` | Implementer | Repo-visible spec that must describe the class-first hashing owner accurately |
| Public model-payload import surface | `src/async_model_gateway/model_registry/model_payload/__init__.py` | Implementer | Topic-local public import surface for `ModelPayloadHasher` |
| Canonical hashing core | `src/async_model_gateway/model_registry/model_payload/canonical_hash.py` | Implementer | Internal recursive canonicalization plus the class-first hashing owner |
| Canonical hash tests | `tests/model_registry/model_payload/test_canonical_hash.py` | Implementer | Bounded pytest coverage for class-first hashing behavior and public-surface removal |

Artifact path notes:

- `src/async_model_gateway/model_registry/__init__.py` is intentionally not in
  scope because the package boundary already satisfies the locked decision of
  not re-exporting the hashing surface.
- Treat listed paths as an executable contract.
- If later work needs registry freshness wiring, cache integration, or broader
  tests outside the listed paths, stop and route back through
  `spec-and-plan-finalization`.

## Implementation Steps

1. Update
   `tests/model_registry/model_payload/test_canonical_hash.py` and record
   `plan/model-payload-hasher-class-surface/model-payload-hasher-class-surface.red-tests.yaml`
   so the bounded pytest coverage targets `ModelPayloadHasher`, confirms the
   old public function is absent from the allowed import surface, preserves the
   existing hashing semantics, and keeps `model_registry` free of re-exports.
2. Update
   `src/async_model_gateway/model_registry/model_payload/canonical_hash.py`
   and `src/async_model_gateway/model_registry/model_payload/__init__.py` so
   `ModelPayloadHasher` becomes the only allowed public owner, the old
   standalone function is removed, and the internal canonicalization helper
   continues to enforce the existing runtime validation and digest behavior.
3. Update `README.md`, `docs/architecture.md`,
   `docs/specs/canonical-input-boundary.md`, and
   `docs/specs/model-side-boundary.md` so every repo-visible description of the
   hashing core matches the class-first public contract without widening the
   architecture scope.
4. Run `uv run pytest tests/model_registry/model_payload/test_canonical_hash.py -v`,
   `uv run ruff check README.md docs src tests plan/model-payload-hasher-class-surface`,
   and `uv run pyright`, then update
   `plan/model-payload-hasher-class-surface/model-payload-hasher-class-surface.step.md`
   to reflect the completed implementer-owned work before reviewer inspection.

## Validation / Acceptance Checks

- Canonical topic-plan sections, status names, artifact paths, and reviewer
  handoff shape remain compatible with repo workflow contracts.
- `model-payload-hasher-class-surface.spec.md` exists because this topic is
  locked as `non-trivial`.
- `model-payload-hasher-class-surface.step.md` mirrors every numbered
  implementation step and reflects only implementer-owned progress truthfully.
- The plan-review artifact records an independent reviewer verdict against this
  new follow-up topic, not against the historical
  `model-payload-canonical-hash-core` topic.
- The RED-test artifact maps requirements to class-first tests and confirms the
  standalone function is no longer part of the allowed public surface.
- The implementation-review artifact verifies that only the locked paths
  changed, that `ModelPayloadHasher` is the only public hashing owner under the
  allowed import surface, and that hashing behavior did not drift.
- Validation must show dict-order-insensitive hashing, list-order sensitivity,
  scalar non-normalization, empty-payload determinism, and `TypeError`
  rejection for unsupported input without touching broader registry or cache
  code.

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
- After merge, stop; do not change VERSION, tags, or release state under this
  topic.

## Open Questions / Unresolved Items

- None.

## Non-goals

- This topic does not introduce a compatibility wrapper or dual public owner.
- This topic does not modify hashing semantics, loader behavior, or registry
  freshness policy.
- This topic does not create a new repo-level workflow phase for
  `create worktree`.
- This topic does not add new dependencies or change the package entrypoint.

## Current Context

- The existing hashing core lives in
  `src/async_model_gateway/model_registry/model_payload/canonical_hash.py` and
  currently exposes only the standalone public function
  `hash_model_payload(model_payload: dict[str, JSONLike]) -> str`.
- The existing test module and multiple repo-visible documents explicitly name
  that function-first public surface.
- The historical topic `model-payload-canonical-hash-core` already completed
  implementation and review for the function-first contract, so this topic must
  stand as a separate follow-up artifact set rather than overwrite that
  history.

## Requirements

1. `async_model_gateway.model_registry.model_payload` must expose
   `ModelPayloadHasher` as the only public hashing owner for this topic.
2. `ModelPayloadHasher.hash_model_payload(...)` must accept only top-level
   `dict[str, JSONLike]` input and return a SHA-256 lowercase hex string.
3. Recursive nested-dict canonicalization, list-order significance, and scalar
   non-normalization must remain unchanged from the existing hashing behavior.
4. Unsupported runtime input types anywhere in the payload tree must still
   raise `TypeError`.
5. The standalone public function `hash_model_payload(...)` must no longer be
   exported from the allowed import surface.
6. `model_registry/__init__.py` must remain free of hashing re-exports.
7. `README.md`, `docs/architecture.md`,
   `docs/specs/canonical-input-boundary.md`, and
   `docs/specs/model-side-boundary.md` must all describe the class-first public
   owner accurately.
8. The implementation must remain bounded to the locked artifact paths and must
   not touch `ResponseCache`, `orchestrator`, `ModelPool`, or `ModelGateway`.

## Decisions

- Public owner: `ModelPayloadHasher`
- Public method:
  `hash_model_payload(self, model_payload: dict[str, JSONLike]) -> str`
- Compatibility policy: remove the standalone public function; no wrapper
- Import policy: only `async_model_gateway.model_registry.model_payload`
  re-exports `ModelPayloadHasher`
- Error behavior: keep `TypeError` fail-closed behavior unchanged
- Typing policy: keep strict typing with the existing `JSONScalar` / `JSONLike`
  aliases internal to `canonical_hash.py`
