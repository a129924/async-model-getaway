# Agent Handoff Workflow

## Purpose

This document is the repo-level baseline contract for topic execution handoff.
It is informed by the existing agent-skills surfaces, but those skills are not
the higher-order authority. When a skill and this document drift, this document
defines the repo-visible workflow until the skill is refreshed.

## Baseline Rules

- Canonical workflow names are fixed:
  - `spec-and-plan-finalization`
  - `implement-plan`
  - `pr-comment`
  - `pr-comment-review-pr-comments-and-fix`
  - `release`
- `release` is conditional. A topic enters `release` only when its repo-visible
  plan explicitly declares release intent or stable-library timing that requires
  it.
- Approval cannot be inferred from chat consensus. Every approval must resolve
  through a repo-visible artifact or an explicit repo-visible gate state.
- `human check` and `human merge` are explicit gates. They are not implied by a
  green review, a chat message, or the absence of objections.
- `Observer` may dispatch and triage only. `Observer` must not implement, edit
  repo files, close gates on behalf of other actors, or bypass the canonical
  workflow.

## Workflow Order

Canonical routing is:

`spec-and-plan-finalization` -> `implement-plan` -> `pr-comment` ->
`pr-comment-review-pr-comments-and-fix` -> `release` (conditional)

The status names and allowed transitions for a specific topic are defined in
`plan/topic-plan-contract.md`. This document defines the phase order, actor
boundaries, and gate semantics that those statuses must honor.

## Workflow Contracts

### `spec-and-plan-finalization`

Purpose:
- Freeze bounded scope in a repo-visible topic plan.
- Resolve review feedback at the planning-contract layer before implementation
  begins.

Required artifacts:
- `plan/<topic>/<topic>.plan.md`
- any analysis-layer artifacts that the topic plan cites
- the repo-visible plan-review artifact declared by the topic plan

Required exit gates:
- plan review gate: repo-visible review artifact records `approved`
- `human check` gate: repo-visible state marks the plan cleared for
  implementation

Forbidden shortcuts:
- starting implementation from `draft`, `review-ready`, or chat-only approval
- treating reviewer silence as approval

### `implement-plan`

Purpose:
- Execute the approved topic plan without widening scope.

Required entry condition:
- `spec-and-plan-finalization` has completed with repo-visible approval and
  `human check`

Rules:
- execution must stay inside the plan's declared artifact paths and locked
  decisions
- any rework that changes scope, artifact paths, public contract, or release
  intent must return through `spec-and-plan-finalization`
- for Python topics, RED test authoring is the first mandatory subphase inside
  `implement-plan`; it is not a separate repo-level workflow
- for Python topics, `implement-plan` must produce the repo-visible evidence
  needed by later implementation review before PR routing begins

Required exit gates:
- implementation completion is recorded in the repo-visible step or gate
  artifact declared by the topic plan
- when the topic includes Python implementation, the repo-visible
  implementation-review gate declared by the topic plan is complete before
  moving to `pr-comment`

### `pr-comment`

Purpose:
- Open the PR review surface for the implemented topic.

Required entry condition:
- `implement-plan` is complete

Rules:
- PR comments may request fixes, clarification, or rework, but they do not
  retroactively replace the plan-approval gate
- missing planning or implementation gates must be fixed in their own workflow;
  PR discussion is not a substitute approval channel

Exit:
- if actionable review feedback appears, route to
  `pr-comment-review-pr-comments-and-fix`
- if no actionable review feedback remains, the topic may proceed to the
  explicit `human merge` gate

### `pr-comment-review-pr-comments-and-fix`

Purpose:
- Triage review feedback, apply bounded fixes, and loop until merge readiness is
  explicit.

Rules:
- `Observer` may classify, route, and summarize comment threads, but may not
  implement fixes or close gates
- the implementer may address comments only within the approved topic boundary;
  feedback that changes scope or contract returns to
  `spec-and-plan-finalization`
- this workflow may repeat multiple rounds; merge readiness is not implied by
  one pass through the loop

Required exit gate:
- `human merge` gate is explicitly passed in a repo-visible state

### `release`

Purpose:
- Execute the topic's declared release or stable-library publication work after
  merge.

Entry condition:
- the topic is `merged`
- the topic plan explicitly declares that `release` is required

Rules:
- topics with no declared release intent stop at `merged`
- release work must follow the topic's repo-visible release contract; it is not
  an automatic side effect of merge

## Gate Semantics

- A gate is valid only when its evidence location is repo-visible and declared
  in the topic plan.
- A gate may be satisfied by:
  - a repo-visible review artifact with a passing verdict
  - an explicitly updated gate state inside the topic plan
  - a repo-visible PR or release state referenced by the topic plan
- A gate is not satisfied by:
  - chat agreement
  - verbal acknowledgement
  - inferred intent
  - lack of review comments

## Role Boundary Summary

- Planning actor:
  - authors or revises the repo-visible topic plan
- Implementer:
  - changes only approved repo artifacts inside the topic boundary
- Reviewer:
  - issues a repo-visible review verdict; does not implement creator work
- Observer:
  - dispatches and triages only
- Human:
  - closes `human check` and `human merge` gates explicitly
