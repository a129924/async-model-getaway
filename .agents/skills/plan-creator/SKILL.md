---
name: plan-creator
description: Create a valid, repo-visible `plan/<topic>/<topic>.plan.md` for this repository, with correct workflow phases, status transitions, artifact paths, analysis-layer handling, reviewer handoff contract, and stable-library intent handling.
complexity: high
risk_profile:
  - ambiguity_sensitive
  - multi_agent_handoff
use_when:
  - a new repository topic needs `plan/<topic>/<topic>.plan.md`
  - an existing topic plan is missing workflow-critical contract sections
  - the user wants a repo-visible handoff artifact before creator implementation starts
do_not_use_when:
  - the main task is to implement the skill or code artifact itself
  - the task is to review or approve a finished topic plan
  - the task is a tiny wording edit to an already-valid topic plan
  - the request is for a generic project plan outside this repository
inputs:
  - the topic name
  - the intended outcome of the topic
  - the in-scope and out-of-scope boundaries
  - the expected repo-visible artifact paths
  - whether the topic affects stable-library surfaces
  - any locked decisions that should not be rediscovered during implementation
  - optional analysis-layer artifacts at `analysis/<topic>/requirements.md` and `analysis/<topic>/technical-spec.md`
  - any explicit human `override` instruction if chat-time guidance should outrank analysis artifacts
  - the current workflow contract from `plan/agent-handoff-workflow.md`
  - the shared topic-plan contract from `plan/topic-plan-contract.md`
outputs:
  - a repo-visible `plan/<topic>/<topic>.plan.md`
  - explicit scope, boundaries, locked decisions, and analysis-layer routing for the topic
  - exact artifact paths and workflow transitions
  - clear stable-library intent declared or explicitly absent
  - explicit semantic warnings when analysis inputs are missing or incomplete
  - a topic plan ready to hand to creator work
---

# Purpose
Create a valid topic plan for this repository's workflow.

# Trigger / When to use
Use this skill when:
- a new repository topic needs `plan/<topic>/<topic>.plan.md`
- an existing topic plan is missing workflow-critical contract sections
- the user wants a repo-visible handoff artifact before creator implementation starts

Do not use this skill when:
- the main task is to implement the skill or code artifact itself
- the task is to review or approve a finished topic plan
- the task is a tiny wording edit to an already-valid topic plan
- the request is for a generic project plan outside this repository

# Inputs
- the topic name
- the intended outcome of the topic
- the in-scope and out-of-scope boundaries
- the expected repo-visible artifact paths
- whether the topic affects stable-library surfaces
- any locked decisions that should not be rediscovered during implementation
- optional analysis-layer artifacts at `analysis/<topic>/requirements.md` and `analysis/<topic>/technical-spec.md`
- any explicit human `override` instruction if chat-time guidance should outrank analysis artifacts
- the current workflow contract from `plan/agent-handoff-workflow.md`
- the shared topic-plan contract from `plan/topic-plan-contract.md`

# Process
1. Confirm the task is really topic-plan authoring, not creator drafting, review, publish, or release execution.
2. Read the current workflow contract and the shared topic-plan contract, then start from `templates/topic-plan-template.md` instead of drafting the plan from scratch.
3. Inspect `analysis/<topic>/requirements.md` and `analysis/<topic>/technical-spec.md` if either exists before deciding the plan scope.
4. Route analysis-layer priority before drafting:
   - if both files exist, enter strict mode: treat `analysis/<topic>/technical-spec.md` as the execution-facing source of truth, use `analysis/<topic>/requirements.md` as the business-intent guardrail, and map the output plan 100% to the technical spec instead of inventing alternative work from chat context
   - if one file exists without the other, emit an explicit semantic warning that names the missing companion artifact and explains that the analysis layer is incomplete
   - if neither file exists, emit an explicit semantic warning that the plan is being authored without the optional analysis layer
   - analysis-layer artifacts outrank conversation-time instructions unless a human explicitly says `override`
5. Decide whether the topic is:
   - review-ready-only with no stable-library surfaces, or
   - a topic that explicitly affects stable-library surfaces and therefore needs declared timing and stable-library metadata
6. Lock scope, boundaries, and role ownership before drafting the plan body in the local template.
7. Enumerate exact `Artifact Paths`; do not use vague catch-all path descriptions.
8. Write the required topic-plan sections in canonical order from the template.
9. If the topic affects stable-library surfaces, add a `## Stable library metadata` section and fill all workflow-required fields needed by later phases, including README row, VERSION bump, timing, and any release-related metadata. If it does not affect stable-library surfaces, make that non-stable intent explicit instead of leaving the contract implicit.
10. Use only canonical workflow transitions and require machine-consumable reviewer handoff JSON.
11. If scope, artifact paths, role ownership, stable-library timing, stable-library metadata, release intent, or analysis-layer priority is unclear, stop and ask instead of filling placeholders.

# Examples
- **Positive**: Draft `plan/offline-order-capture/offline-order-capture.plan.md` so it uses exact artifact paths, canonical transitions, and JSON reviewer handoff, while entering strict mode because both `analysis/offline-order-capture/requirements.md` and `analysis/offline-order-capture/technical-spec.md` exist.
- **Negative**: Ignore existing analysis files because a newer chat instruction sounds easier, skip semantic warnings when analysis inputs are missing, or draft a plan that says `README/VERSION maybe later`.

# Outputs
- a repo-visible `plan/<topic>/<topic>.plan.md`
- explicit scope, boundaries, locked decisions, and analysis-layer routing for the topic
- exact artifact paths and workflow transitions
- clear stable-library intent: declared or explicitly absent
- explicit semantic warnings when analysis inputs are missing or incomplete
- a topic plan that is ready to hand to creator work

# Validation

## Required Checks
- PASS: topic name, outcome, scope, and artifact paths are all provided
- PASS: the workflow contract at `plan/agent-handoff-workflow.md` is readable
- PASS: the shared topic-plan contract at `plan/topic-plan-contract.md` is readable
- SOFT FAIL: analysis-layer artifacts are missing or incomplete — emit an explicit semantic warning naming what is absent and continue with incomplete-layer routing
- BLOCKED: scope, artifact paths, or stable-library timing cannot be determined without guessing — stop and ask before drafting

## Quality Checks
- all required topic-plan sections are present in canonical order and match `plan/topic-plan-contract.md`
- current status and allowed transitions are explicit and canonical
- `Artifact Paths` are exact, bounded, and role-labeled (see `references/artifact-path-rule.md`)
- reviewer handoff is a single machine-consumable JSON object
- post-merge / release timing matches the topic's actual scope
- stable-library intent is explicitly declared or explicitly absent (see `references/stable-library-rule.md`)
- analysis-layer priority routing is stated before the plan body begins
- strict mode maps the plan 100% to `analysis/<topic>/technical-spec.md` when both analysis artifacts exist
- missing analysis artifacts produce explicit semantic warnings instead of silent fallback
- chat-time instructions do not outrank analysis artifacts unless a human explicitly says `override`

## On Soft Fail
- mark the plan as INCOMPLETE; list missing analysis artifacts or unresolvable scope items explicitly
- emit a named semantic warning when one analysis file exists without its companion
- do not silently fall back to chat context when analysis artifacts exist but are partial

# Red Flags
- the plan mixes review-ready-only work with undeclared stable-library publish intent
- the plan says `TBD`, `later`, or `follow normal process` where the workflow needs an explicit contract
- artifact paths are broad labels instead of concrete repo-visible paths
- creator, reviewer, and Main Agent ownership are blended together
- reviewer handoff is written as Markdown notes instead of JSON
- existing analysis artifacts are ignored because chat context points somewhere else

# Common Rationalizations
- `Reviewer can infer the missing contract later.`
- `We can decide whether this touches README or VERSION after implementation.`
- `Artifact paths do not need to be exact as long as the scope sounds right.`
- `A rough status model is good enough if the intent is obvious.`
- `The latest chat instruction should automatically override analysis files.`

# Boundaries
- Do not implement the topic's actual skill or code artifact.
- Do not review, approve, or publish the topic.
- Do not guess stable-library timing or release intent.
- Do not rely on hidden chat context instead of a repo-visible plan.
- Do not let absent analysis files fail silently; warn explicitly.
- Do not let casual chat instructions override analysis artifacts without an explicit human `override`.
- Do not generate a generic project-management plan for another repository.
- `plan/topic-plan-contract.md` is the shared repo-level fallback contract when the topic-plan template is absent.

# Failure Handling

## Missing Context
- BLOCKED — if the topic name, outcome, or scope is absent, stop and ask before drafting
- BLOCKED — if the workflow contract at `plan/agent-handoff-workflow.md` or the shared topic-plan contract at `plan/topic-plan-contract.md` cannot be read, stop before drafting

## Ambiguous Requirement
- if stable-library timing is unclear, stop and ask rather than guessing; do not fill with `TBD` or `later`
- if artifact paths cannot be determined exactly, stop and list what is missing
- if analysis artifacts conflict with chat-time instructions and no explicit human `override` is present, stop and require the human to choose before continuing

## Execution Limitation
- if the topic-plan template is absent, fall back to the required section list in `plan/topic-plan-contract.md` rather than inventing a new shape
- if a human `override` instruction is ambiguous about which analysis file it overrides, ask for clarification before discarding analysis content

# Workflow State Contract

When participating in a multi-agent plan-authoring and review workflow, include:
- current_step: <step name from Process>
- next_step: <next step or DONE>
- status: IN_PROGRESS | COMPLETE | INCOMPLETE | BLOCKED

Omit this section when the plan is authored outside a multi-agent handoff flow.

# Local references
- `reference.md`: overview of stable authoring rules with pointers to each topic in `references/`
- `plan/topic-plan-contract.md`: shared repo-level authority for required topic-plan sections, fallback behavior, and contract-level blocking semantics
- `references/required-section-meaning.md`: what each mandatory topic-plan section means and must contain
- `references/stable-library-rule.md`: when and how to declare stable-library intent, metadata, release timing, and VERSION/README decisions
- `references/artifact-path-rule.md`: how to declare exact, role-labeled, executable artifact paths
- `references/role-boundary-rule.md`: how to keep planning actor, creator, reviewer, and Main Agent roles distinct
- `references/stop-and-ask-triggers.md`: conditions that require stopping and asking before drafting or continuing
- `references/template-usage-rule.md`: how to use and complete the topic-plan template without leaving scaffolding
- `examples.md`: detailed good and bad topic-plan scenarios, including stable and non-stable cases
- `checklist.md`: repeatable checks for a higher-risk planning skill
- `templates/topic-plan-template.md`: canonical topic-plan skeleton and section prompts for this repository
