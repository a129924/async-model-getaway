# Topic plan template

Use this template to draft `plan/<topic>/<topic>.plan.md` for this repository.
Delete prompt text after replacing it with real topic-specific content.

## Goal / Outcome

- State the concrete repository-visible result of this topic.
- Say what should exist or be true when the topic is complete.

## Scope

- **In scope**:
  - List the concrete files, folders, or repository-visible outcomes this topic will change.

- **Out of scope**:
  - List nearby work this topic will not do.

## Locked Decisions

- Record decisions downstream roles should not rediscover.
- Say whether this topic is:
  - review-ready-only with no stable-library surfaces, or
  - a stable-library-affecting topic with declared timing
- If this topic uses correction artifacts, lock whether the workflow body stays slim and where detailed correction schema guidance belongs.
- If this topic is a correction-lifecycle refresh, state whether standalone skill extraction is explicitly deferred and what later conditions could justify a separate topic.

## Boundaries / Exclusions

- State the role and scope boundaries that must remain intact.
- Call out adjacent tasks that belong in a different topic.

## Status / Allowed Transitions

- **Current**: `planned`
- **Execution model**: follow the canonical creator -> reviewer -> publish -> merge path; declare if this topic stops before release
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
  - `merged` -> terminal

Conditional transition rule:

- If this topic explicitly declares a release action, add `merged` -> `released`
  and update the terminal-state wording accordingly.

Routing notes:

- Keep any topic-specific routing details here.
- If the topic uses the standard Phase 4.5 rule, say so explicitly.
- Declare a round cap only when the topic truly needs one; do not imply a repository-wide default.

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/<topic>/<topic>.plan.md` | Planning actor | Repo-visible execution contract for this topic |
| [artifact name] | `[exact/path]` | [role] | [why it exists in this topic] |

Artifact path notes:

- Say explicitly whether this topic modifies `README.md`, `VERSION`, or `.github/copilot-instructions.md`.
- Treat listed paths as an executable contract.
- If the topic uses correction artifacts, list each exact parent artifact, each exact correction artifact, and any repo-visible `review-log` / equivalent handoff artifact only when reviewer feedback controls routing or multi-round rework.
- Do not use vague evidence labels such as `merged implementation`, `correction files`, or `latest feedback`.
- Say what should happen if later work drifts outside these paths.

## Stable library metadata

- Include this section **only when** the topic affects stable-library surfaces or
  defers release timing.
- When present, declare:
  - `README row`: exact table row, entry, or explicit no-change decision
  - `VERSION bump`: exact bump direction or explicit no-bump decision
  - `timing`: whether changes happen at `publish-in-progress` or `release`
  - `rationale`: why this stable-library action exists
  - any release-note expectations or other release-timing metadata, when relevant
- Cross-checks:
  - if `timing=release`, `Post-merge / release actions` must declare the release action that executes Phase 10
  - if `timing=publish-in-progress`, the stable-library files must be included in `Artifact Paths`

## Implementation Steps

- Describe what creator work will produce.
- Keep the steps inside the topic's locked boundaries.
- Keep the steps creator-owned; do not assign reviewer verdict logging or main-agent routing work here.
- If correction lifecycle guidance is part of the topic, keep the workflow body focused on lifecycle / routing contract and move field-level correction artifact schema or long examples into reference / example surfaces.
- If correction artifacts are part of the topic, make sure some allowed reference / example surface defines the minimum `correction-plan` and `correction-step` content instead of pushing that schema into the workflow body.

## Validation / Acceptance Checks

- List the signals reviewer and main agent should verify.
- Include workflow-critical checks such as path exactness, status correctness,
  and reviewer handoff shape when relevant.
- When correction artifacts are used, include parent-sync closure, current-truth versus historical-truth separation, and conditional review-log expectations.

## Reviewer Handoff

- Use a single JSON object, not Markdown prose or tables.

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

- Say what happens after merge.
- If no repository release action is required, say so explicitly.
- If release work exists, it must match the topic's declared stable-library timing.

## Open Questions / Unresolved Items

- Keep only the questions that truly remain open.
- If a missing answer blocks correct planning, stop and ask instead of leaving the plan vague.
