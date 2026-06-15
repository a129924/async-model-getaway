---
name: plan-reviewer
description: Independently review a repo-visible `plan/<topic>/<topic>.plan.md` for this repository after the plan exists and before execution proceeds. Use this when a topic plan needs a contract-level verdict against the repository workflow and plan-authoring rules.
complexity: high
risk_profile:
  - ambiguity_sensitive
  - multi_agent_handoff
use_when:
  - "a repo-visible `plan/<topic>/<topic>.plan.md` already exists"
  - "the plan needs an independent review before branch preparation or creator implementation begins"
  - "an existing topic plan was revised and needs contract re-review"
  - "Main Agent is routing plan review through a separate independent reviewer path"
do_not_use_when:
  - "the main task is to author or revise the topic plan itself"
  - "the task is to review a skill folder or implementation draft"
  - "the request is for a generic project plan outside this repository"
  - "the task is to rewrite the canonical workflow spec itself"
inputs:
  - "the target `plan/<topic>/<topic>.plan.md`"
  - "the current workflow contract from `plan/agent-handoff-workflow.md`"
  - "the shared topic-plan contract from `plan/topic-plan-contract.md`"
  - "any contextual review feedback, including Copilot feedback, if it exists"
outputs:
  - "exactly one machine-consumable JSON object with no trailing prose"
  - "verdict set to approved or needs-rework"
  - "blocking_issues list with issue, file, and fix for each contract-breaking problem"
  - "copilot_feedback_triage with ADDRESS, DISCUSS, and SKIP arrays"
---

# Purpose
Review a repo-visible topic plan as a planning-contract gate before execution proceeds.

# Trigger / When to use
Use this skill when:
- a repo-visible `plan/<topic>/<topic>.plan.md` already exists
- the plan needs an independent review before branch preparation or creator implementation begins
- an existing topic plan was revised and needs contract re-review
- Main Agent is routing plan review through a separate independent reviewer path

Do not use this skill when:
- the main task is to author or revise the topic plan itself
- the task is to review a skill folder or implementation draft
- the request is for a generic project plan outside this repository
- the task is to rewrite the canonical workflow spec itself

# Inputs
- the target `plan/<topic>/<topic>.plan.md`
- the current workflow contract from `plan/agent-handoff-workflow.md`
- the shared topic-plan contract from `plan/topic-plan-contract.md`
- any contextual review feedback, including Copilot feedback, if it exists

# Process
1. Confirm the task is topic-plan review, not plan authoring, skill review, publish routing, or workflow-spec editing.
2. Read the target topic plan plus the shared contract sources before judging the plan.
3. Verify the topic plan path, required sections, canonical status model, artifact-path exactness, stable-library intent, reviewer handoff JSON shape, post-merge timing, and role boundaries.
4. Treat placeholders such as `TBD`, `later`, or `follow normal process` as contract failures when the workflow requires explicit decisions.
5. Treat missing sections, invalid transitions, vague artifact paths, undeclared stable intent, wrong timing, non-JSON reviewer handoff, and role-boundary confusion as blocking issues.
6. Keep the review focused on contract-breaking issues rather than wording polish or stylistic preferences that do not change workflow meaning.
7. Return exactly one JSON object with this fixed schema:
   - `verdict`: `approved` or `needs-rework`
   - `blocking_issues[]`: objects with `issue`, `file`, and `fix`
   - `copilot_feedback_triage.ADDRESS[]`: objects with `comment`, `location`, and `why`
   - `copilot_feedback_triage.DISCUSS[]`: objects with `comment`, `optional`, and `why`
   - `copilot_feedback_triage.SKIP[]`: objects with `comment` and `why`

# Examples
- **Positive**: Review `plan/python-docstrings/python-docstrings.plan.md` after the plan exists, reject no contract-breaking issues, and return one JSON object that confirms non-stable intent, exact artifact paths, canonical transitions, and machine-consumable reviewer handoff.
- **Negative**: Use this skill to draft the topic plan, approve a plan that says `README/VERSION maybe later`, or return Markdown prose instead of the required JSON verdict.

# Outputs
- exactly one machine-consumable JSON object and no trailing prose
- `verdict`: `approved` or `needs-rework`
- `blocking_issues`: only true contract-breaking problems; each item contains `issue`, `file`, and `fix`
- `copilot_feedback_triage.ADDRESS`: direct required feedback items; each item contains `comment`, `location`, and `why`
- `copilot_feedback_triage.DISCUSS`: optional discussion items; each item contains `comment`, `optional`, and `why`
- `copilot_feedback_triage.SKIP`: explicitly inapplicable feedback items; each item contains `comment` and `why`

# Verification
- confirm the review basis explicitly includes `plan/agent-handoff-workflow.md` and `plan/topic-plan-contract.md`
- confirm required sections are present and named correctly
- confirm transitions stay canonical and execution timing is coherent
- confirm `Artifact Paths` are exact, bounded, and repo-visible
- confirm stable-library intent is explicit: clearly absent or explicitly declared
- confirm the verdict stays JSON-only with no prose outside the object

# Red Flags
- the plan invents a new status model or skips canonical phases
- `Artifact Paths` use broad labels such as `docs`, `skill folder`, or `maybe version files`
- stable-library timing is implied but not declared
- `Reviewer Handoff` is a table, prose note, or mixed-format report instead of one JSON object
- planning actor, creator, reviewer, and Main Agent responsibilities are blended together

# Common Rationalizations
- "The reviewer can infer the missing contract later."
- "The exact paths are obvious from context."
- "We can decide stable-library timing after implementation."
- "A rough status model is good enough if everyone understands the goal."

# Boundaries
- Do not rewrite the topic plan on behalf of the planning actor.
- Do not invent a second topic-plan schema that conflicts with `plan-creator` or the canonical workflow.
- Do not approve a plan that still has contract-breaking ambiguity.
- Do not turn this skill into implementation review, branch preparation, or publish execution.
- Do not emit anything except the single JSON verdict object.

# Validation

## Required Checks
- PASS: the shared contract sources are readable before review begins
- PASS: the target plan file exists at the expected path
- BLOCKED: the plan file cannot be read or does not exist — return `needs-rework` in the fixed JSON schema with the missing file recorded as a blocking issue

## Quality Checks
- all required topic-plan sections are present and named correctly
- canonical status model and transitions are used without invention
- artifact paths are exact, bounded, and repo-visible
- stable-library intent is explicitly declared or explicitly absent
- reviewer handoff is exactly one JSON object with no trailing prose
- post-merge timing is coherent with the topic scope

## On Soft Fail
- treat placeholder text (`TBD`, `later`, `follow normal process`) as a contract failure, not a soft gap
- a plan with any blocking issue must return `needs-rework`; partial approval is not allowed

# Failure Handling

## Missing Context
- BLOCKED — if `plan/agent-handoff-workflow.md` or `plan/topic-plan-contract.md` cannot be read, stop before issuing any verdict
- BLOCKED — if the target plan path cannot be resolved, still return the fixed JSON verdict schema with `verdict: "needs-rework"` and a `blocking_issues` entry describing the unresolved path; do not guess or infer a path

## Ambiguous Requirement
- if a section name is subtly wrong but the intent is clear, flag it as a contract failure rather than silently accepting it
- if the plan's stable-library intent is partially declared, treat partial declaration as undeclared

## Execution Limitation
- if a plan section is ambiguously present (e.g., combined with another section), flag it and return `needs-rework` rather than accepting ambiguous structure
- if Copilot feedback input is absent, populate the `ADDRESS`, `DISCUSS`, and `SKIP` lists as empty arrays rather than omitting them

# Workflow State Contract

When participating in a multi-agent plan review or creator-reviewer handoff, include:
- current_step: <step name from Process>
- next_step: <next step or DONE>
- status: APPROVED | NEEDS_REWORK | INCOMPLETE | BLOCKED

These fields are for internal agent state coordination only and MUST NOT appear inside the final JSON verdict object; the delivered output must remain the single fixed-schema JSON object (verdict / blocking_issues / copilot_feedback_triage) in all operating modes, whether standalone or in a multi-agent handoff.

Omit this section when the review is performed as a standalone action.

# Local references
- `reference.md`: stable review basis, severity rules, and workflow-position guidance for topic-plan review
- `plan/topic-plan-contract.md`: shared repo-level authority for required topic-plan sections, fallback behavior, and contract-level blocking semantics
- `examples.md`: approved and needs-rework plan-review scenarios, including stable and non-stable cases
- `checklist.md`: repeatable contract checks for this higher-risk planning gate
