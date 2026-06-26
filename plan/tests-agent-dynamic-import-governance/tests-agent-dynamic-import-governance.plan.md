> Semantic warning:
> `analysis/tests-agent-dynamic-import-governance/requirements.md` and
> `analysis/tests-agent-dynamic-import-governance/technical-spec.md` were not
> found at authoring time. This plan is authored from repo exploration and the
> explicit topic request only.

# tests-agent-dynamic-import-governance

## Goal / Outcome

- Define a bounded governance implementation topic that prevents agents from
  using dynamic module loading inside `tests/` to make tests fit implementation
  unless the current topic plan explicitly authorizes a necessary exception
  that the reviewer can verify.
- When this topic is complete, the formal control plane is explicit in root
  `AGENTS.md` plus the reviewer gate, `tests/AGENTS.md` is not treated as an
  authoritative policy surface, the known grandfathered exception is recorded
  only as history, and no release work is introduced.

## Scope

- **In scope**:
  - Add the repo-visible plan, step-tracking artifact, and plan-review
    handoff artifact for `tests-agent-dynamic-import-governance`.
  - Plan implementation only in `AGENTS.md` and
    `.codex/agents/reviewer.toml` as the bounded governance surfaces that
    define and enforce agent behavior in `tests/`.
  - Record the grandfathered exception policy for
    `tests/model_registry/model_payload/test_canonical_hash.py` without
    rewriting that test file.

- **Out of scope**:
  - Any `src/`, `tests/`, `docs/`, `README.md`, workflow-contract, or release
    change.
  - Creating, legitimizing, or depending on `tests/AGENTS.md` as a formal
    policy surface.
  - Any repo-wide blanket `importlib` ban or governance outside `tests/`.

## Locked Decisions

- This topic is not a stable-library topic and does not declare release-facing
  timing. `## Stable library metadata` is intentionally absent.
- Root `AGENTS.md` plus the reviewer gate are the only formal control plane for
  this topic.
- `tests/AGENTS.md` does not have formal effect and must not be introduced as a
  controlling surface under this topic.
- This topic does not impose a repo-wide blanket `importlib` ban.
- Governance is limited to agent behavior in `tests/` when dynamic module
  loading is used to make tests fit implementation constraints.
- The only allowed path for dynamic module loading in `tests/` is a topic-plan
  exception that is explicitly authorized and reviewer-verifiable for
  necessity.
- `tests/model_registry/model_payload/test_canonical_hash.py` is a
  grandfathered known exception. This topic records it, but does not rewrite
  it.
- `*.step.md` is used here as a repo-visible workflow companion artifact only;
  this topic does not declare Python TDD, RED-test, or implementation-review
  companion artifacts.

## Boundaries / Exclusions

- The planning actor only authors repo-visible planning artifacts for this
  topic.
- The implementer may only change the exact governance surfaces declared in
  `## Artifact Paths`; drift outside those paths returns the topic to
  `spec-and-plan-finalization`.
- The reviewer checks unauthorized dynamic module loading in `tests/` against
  the locked decisions and declared exception path; the reviewer does not
  rewrite policy on behalf of the implementer.
- Refactoring the grandfathered test, broadening import discipline outside
  `tests/`, or changing workflow-contract files belongs in a different topic.

## Status / Allowed Transitions

- **Current**: `reviewer-in-progress`
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

- `approved` requires both the repo-visible plan-review artifact with an
  `approved` verdict and the human-owned gate evidence at
  `plan/tests-agent-dynamic-import-governance/tests-agent-dynamic-import-governance.human-check.json`.
- The `human check` gate is satisfied only when that repo-visible
  `*.human-check.json` artifact explicitly records that the approved plan is
  cleared for `implement-plan`.
- Until both
  `tests-agent-dynamic-import-governance.plan-review.json`
  and `tests-agent-dynamic-import-governance.human-check.json` pass their
  respective gates, this topic must not enter `implement-plan`.
- The reviewer gate for this topic must reject new or expanded dynamic module
  loading in `tests/` unless the topic plan names the exception and why it is
  necessary.
- Any scope change that adds test rewrites, repo-wide import rules, or
  additional governance surfaces returns to `spec-and-plan-finalization`.

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/tests-agent-dynamic-import-governance/tests-agent-dynamic-import-governance.plan.md` | Planning actor | Repo-visible execution contract for this topic |
| Topic step tracking | `plan/tests-agent-dynamic-import-governance/tests-agent-dynamic-import-governance.step.md` | Planning actor | Repo-visible implementation-progress companion artifact |
| Plan review artifact | `plan/tests-agent-dynamic-import-governance/tests-agent-dynamic-import-governance.plan-review.json` | Reviewer | Repo-visible planning gate verdict |
| Human check gate evidence | `plan/tests-agent-dynamic-import-governance/tests-agent-dynamic-import-governance.human-check.json` | Human | Human-owned repo-visible gate evidence that clears the approved plan for `implement-plan` |
| Root agent governance surface | `AGENTS.md` | Implementer | Formal control-plane policy for agent behavior in `tests/` |
| Reviewer gate surface | `.codex/agents/reviewer.toml` | Implementer | Repo-local reviewer instruction surface that enforces the topic-plan exception rule for dynamic module loading in `tests/` |

Artifact path notes:

- This topic does not modify `README.md`, `VERSION`, workflow-contract files,
  `src/`, `tests/`, or `docs/`.
- `tests-agent-dynamic-import-governance.human-check.json` is human-owned gate
  evidence; planning, implementer, and reviewer work must not pre-fill it on
  behalf of Human.
- Do not create or rely on `tests/AGENTS.md` as a governance artifact under
  this topic.
- Treat listed paths as an executable contract.
- If later work needs additional agent surfaces, test rewrites, or any source
  change, stop and route back through `spec-and-plan-finalization`.

## Implementation Steps

1. Update `AGENTS.md` so the root repo policy explicitly forbids agents from
   using dynamic module loading in `tests/` to make tests fit implementation
   unless the current topic plan names a reviewer-verifiable necessity
   exception; state that root `AGENTS.md` plus the reviewer gate are the formal
   control plane and `tests/AGENTS.md` is not.
2. Update `.codex/agents/reviewer.toml` so reviewer instructions treat
   unauthorized dynamic module loading in `tests/` as a bounded governance
   violation, require the topic plan to name any allowed exception and why it
   is necessary, and record
   `tests/model_registry/model_payload/test_canonical_hash.py` only as a
   grandfathered known exception rather than a reusable precedent.
3. Run bounded validation over `AGENTS.md`, `.codex/agents/reviewer.toml`, and
   existing `tests/` dynamic-import call sites so the grandfathered exception
   remains the only recorded known case, then update
   `tests-agent-dynamic-import-governance.step.md` to reflect implementer-owned
   completion without pre-filling reviewer or human gates.

## Validation / Acceptance Checks

- Canonical topic-plan sections, status names, artifact paths, and reviewer
  handoff shape remain compatible with the repo workflow contracts.
- `Artifact Paths` stay exact and limited to the declared planning/governance
  surfaces; no `src/`, `tests/`, `docs/`, `README.md`, or workflow-contract
  path is added under this topic.
- `tests-agent-dynamic-import-governance.human-check.json` is declared as the
  human-owned repo-visible gate evidence for `human check`, and
  `implement-plan` entry remains blocked until it explicitly clears the
  approved plan for implementation.
- Stable-library intent remains explicitly absent and `Post-merge / release
  actions` continues to say no release workflow is required.
- `tests/AGENTS.md` is excluded from the formal control plane and is not
  created or relied upon by this topic.
- The governance rule remains scoped to agent behavior in `tests/`; it does
  not become a repo-wide blanket `importlib` ban.
- Any allowed dynamic-import exception in `tests/` must be named in the topic
  plan and reviewer-verifiable for necessity.
- `tests/model_registry/model_payload/test_canonical_hash.py` is recorded only
  as a grandfathered known exception and is not promised a rewrite in this
  topic.
- `tests-agent-dynamic-import-governance.step.md` mirrors every numbered
  implementation step and does not pre-fill plan review, human check, or
  implementation completion before those workflow events actually occur.
- `tests-agent-dynamic-import-governance.plan-review.json` exists as a
  reviewer-owned repo-visible artifact and currently records an `approved`
  review verdict.

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
- After merge, stop; do not change README, VERSION, tags, or release state
  under this topic.

## Open Questions / Unresolved Items

- None.
