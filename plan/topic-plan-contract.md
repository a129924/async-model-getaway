# Topic Plan Contract

## Purpose

This document defines the shared repo-level fallback contract for
`plan/<topic>/<topic>.plan.md`.

It must stay compatible with the current topic-plan authoring and review
surfaces:

- `plan-creator` topic-plan template
- `plan-reviewer` checklist
- Python plan-authoring as a conditional extension path

Python/TDD-specific planning, RED-test routing, and companion artifacts are
conditional extension guidance only. They apply only when a topic explicitly
adopts the Python planning extension path, and they do not create universal
repo-level requirements for all topics.

## Canonical Base Sections

Every topic plan must include these top-level sections in this order:

1. `## Goal / Outcome`
2. `## Scope`
3. `## Locked Decisions`
4. `## Boundaries / Exclusions`
5. `## Status / Allowed Transitions`
6. `## Artifact Paths`
7. `## Implementation Steps`
8. `## Validation / Acceptance Checks`
9. `## Reviewer Handoff`
10. `## Post-merge / release actions`
11. `## Open Questions / Unresolved Items`

Conditional sections:

- `## Stable library metadata`
  - required only when the topic affects stable-library surfaces or declares
    release-facing timing
- Python planning extensions
  - topic-local supplemental sections or companion artifacts may be added when a
    topic enters Python implementation planning
  - these extensions must not replace, rename, or reorder the canonical base
    sections above

Non-canonical planning content such as `Current Context`, `Non-goals`,
`Requirements`, `Analysis Inputs`, and `Implementation Workflow Contract` may be
used only as topic-local supplements or companion artifacts. They are not
repo-level canonical base sections.

## Section Semantics

### `## Goal / Outcome`

- state one bounded repository-visible outcome
- say what should exist or be true when the topic is complete

### `## Scope`

- define concrete in-scope and out-of-scope work
- keep scope specific enough that later rework can be judged against it

### `## Locked Decisions`

- record decisions downstream roles must not rediscover
- declare whether stable-library intent is absent or requires the conditional
  `Stable library metadata` section
- record any analysis-layer routing, override, or workflow decisions when the
  topic depends on them

### `## Boundaries / Exclusions`

- state role boundaries that must remain intact
- call out adjacent work that belongs in a different topic

### `## Status / Allowed Transitions`

- declare the current topic status
- declare only canonical allowed transitions
- keep workflow-specific routing notes here instead of creating a separate
  canonical workflow-contract section

### `## Artifact Paths`

- use an exact repo-relative table
- each row must include:
  - `Artifact`
  - `Path`
  - `Owner`
  - `Role`
- listed paths are an executable contract, not examples

### `## Stable library metadata`

- include this section only when stable-library surfaces or release timing are
  part of the topic
- when present, declare README impact, VERSION impact, timing, and rationale

### `## Implementation Steps`

- keep steps creator-owned and bounded to the topic
- do not mix reviewer verdict logging or main-agent routing work into creator
  steps
- when a topic explicitly adopts the Python planning extension path, topic-local
  workflow notes or companion artifacts may require RED test authoring as the
  first Python subphase inside `implement-plan`

### `## Validation / Acceptance Checks`

- list the signals reviewer and later execution gates must verify
- include workflow-critical checks such as path exactness, status correctness,
  and reviewer handoff shape when relevant
- when a topic explicitly adopts the Python planning extension path, include
  the declared evidence expected from RED testing, step tracking, spec support,
  and later implementation review only when those companion gates are used

### `## Reviewer Handoff`

- define the repo-visible review artifact declared in `Artifact Paths`
- use one machine-consumable JSON object only

### `## Post-merge / release actions`

- explicitly declare either:
  - `No release workflow required`
  - or the concrete release action and timing
- merge is not release

### `## Open Questions / Unresolved Items`

- keep only genuine unresolved items
- if an answer is required to avoid guessing, stop and ask instead of leaving
  the plan vague

## Canonical Status Model

Allowed statuses:

- `planned`
- `creator-in-progress`
- `review-ready`
- `reviewer-in-progress`
- `needs-rework`
- `approved`
- `publish-in-progress`
- `pr-open`
- `merged`
- `released` (conditional)

Allowed transitions:

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
- `merged` -> `released` when the topic explicitly declares release intent

Additional rules:

- `released` is valid only for topics that explicitly require the conditional
  `release` workflow
- approval cannot be inferred from chat consensus
- `approved` requires both:
  - a repo-visible review artifact with an `approved` verdict
  - an explicit repo-visible `human check`
- `merged` requires an explicit repo-visible `human merge`

These are gate semantics that supplement the current workflow. They do not
replace the canonical status names or transition model above.

## Artifact Path Contract

Minimum required artifact rows:

- topic plan:
  - `plan/<topic>/<topic>.plan.md`
- plan review artifact:
  - `plan/<topic>/<topic>.plan-review.json`

When used, the topic plan must list each exact path explicitly:

- analysis-layer artifacts:
  - `analysis/<topic>/requirements.md`
  - `analysis/<topic>/technical-spec.md`
- release-only artifacts, if release applies

Conditional Python extension guidance, only when the topic explicitly adopts
the Python planning extension path:

- Python implementation progress / gate artifact:
  - `plan/<topic>/<topic>.step.md`
- non-trivial Python behavior contract:
  - `plan/<topic>/<topic>.spec.md`
- Python RED-test authoring artifact, if the topic uses one
- Python implementation-review artifact, if the topic uses one

Rules:

- the minimum required set above is the only universal artifact requirement
- any gate or workflow decision that depends on a conditional artifact must name
  that artifact by exact path
- owner labels must keep planning, creator, reviewer, and human-gate
  responsibilities distinct
- when a topic explicitly adopts the Python planning extension path, it may
  declare `*.step.md` support for progress or gate tracking
- non-trivial Python topics on that extension path should declare `*.spec.md`
- if that extension path also adopts implementation-review or RED-test gates,
  the required evidence artifacts must be declared before PR routing begins

## Review Handoff Shape

The repo-visible plan-review artifact must contain exactly one JSON object with
no surrounding prose:

```json
{
  "verdict": "approved | needs-rework",
  "blocking_issues": [
    {
      "issue": "string",
      "file": "string",
      "fix": "string"
    }
  ],
  "copilot_feedback_triage": {
    "ADDRESS": [
      {
        "comment": "string",
        "location": "string",
        "why": "string"
      }
    ],
    "DISCUSS": [
      {
        "comment": "string",
        "optional": true,
        "why": "string"
      }
    ],
    "SKIP": [
      {
        "comment": "string",
        "why": "string"
      }
    ]
  }
}
```

Rules:

- `Reviewer Handoff` stays a single JSON-object contract
- a review verdict of `approved` is necessary but not sufficient for the topic
  to reach `approved`; the explicit repo-visible `human check` is also required
- `needs-rework` must route the topic back through the canonical rework path
