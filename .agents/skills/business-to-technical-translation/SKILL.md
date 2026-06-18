---
name: business-to-technical-translation
description: Translate a frozen business baseline into `analysis/<topic>/technical-spec.md` with technical tasks, feasibility constraints, architecture-compliance checks, cost-of-realization estimates, and rollback-to-alignment behavior when reality conflicts with intent.
complexity: medium
risk_profile:
  - ambiguity_sensitive
use_when:
  - "`analysis/<topic>/requirements.md` exists and the next step is technical decomposition or feasibility analysis"
  - the workflow needs explicit technical tasks, artifacts, constraints, and dependency mapping before execution planning starts
  - architecture fit, delivery cost, or operational burden must be tested against the business baseline
  - the request needs a pessimistic implementer view instead of optimistic solution selling
do_not_use_when:
  - the business baseline is missing, contradictory, or still vague; route back to `business-intent-alignment`
  - the task is direct implementation, coding, or runtime debugging
  - the main work is architecture invention without a frozen baseline to translate
inputs:
  - topic name and intended `analysis/<topic>/technical-spec.md` path
  - "`analysis/<topic>/requirements.md` as the business baseline"
  - current repository, platform, or system constraints that the design must obey
  - available architecture rules, dependency boundaries, and compliance obligations
  - staffing, timeline, integration, operational, and cost constraints
  - known failure tolerances, rollback expectations, and non-negotiable business priorities
outputs:
  - "`analysis/<topic>/technical-spec.md` as the implementation-facing technical baseline"
  - requirement-to-technical mapping with tasks, artifacts, and dependency notes
  - cost-of-realization and feasibility constraints for each major workstream
  - architecture-compliance results, conflicts, and rollback-to-alignment triggers
---

# Purpose
Turn a frozen business baseline into a technical specification that names the required engineering work, feasibility constraints, and rollback triggers.

# Trigger / When to use
Use this skill when:
- `analysis/<topic>/requirements.md` exists and the next step is technical decomposition or feasibility analysis
- the workflow needs explicit technical tasks, artifacts, constraints, and dependency mapping before execution planning starts
- architecture fit, delivery cost, or operational burden must be tested against the business baseline
- the request needs a pessimistic implementer view instead of optimistic solution selling

Do not use this skill when:
- the business baseline is missing, contradictory, or still vague; route back to `business-intent-alignment`
- the task is direct implementation, coding, or runtime debugging
- the main work is architecture invention without a frozen baseline to translate

# Inputs
- topic name and intended `analysis/<topic>/technical-spec.md` path
- `analysis/<topic>/requirements.md` as the business baseline
- current repository, platform, or system constraints that the design must obey
- available architecture rules, dependency boundaries, and compliance obligations
- staffing, timeline, integration, operational, and cost constraints
- known failure tolerances, rollback expectations, and non-negotiable business priorities

# Process
1. Confirm the task is technical translation, not business discovery or implementation. If the baseline is missing, vague, or contradictory, stop spec authoring and route back to `business-intent-alignment` with the exact gap.
2. Adopt a pessimistic implementer posture. Assume hidden coupling, operational cost, migration effort, and failure handling all count until proven otherwise.
3. Map each requirement to the minimum technical realization: components, interfaces, data changes, operational dependencies, validation artifacts, and owner-facing tasks.
4. Estimate the cost of realization for each major workstream in concrete terms: complexity, sequencing, staffing pressure, integration burden, and ongoing operational overhead.
5. Run an architecture-compliance self-check against existing standards, boundaries, and supported patterns. Name every fit, mismatch, waiver need, and missing prerequisite explicitly.
6. Detect conflicts between technical reality and business intent, including schedule impossibility, platform limitations, security/compliance gaps, data constraints, and rollback-risk surfaces.
7. When conflicts are material, trigger rollback to alignment instead of forcing a false technical plan. State which business assumption failed, what must be renegotiated, and which work remains blocked.
8. Write `analysis/<topic>/technical-spec.md` with requirement traceability, technical tasks and artifacts, feasibility assessment, architecture-compliance results, conflict notes, and rollback triggers.

# Examples
- **Positive**: Translate a frozen offline-order baseline into a technical spec that names local-storage needs, sync tasks, architecture fit checks, staffing pressure, and a rollback trigger if secure offline storage is unavailable on the approved platform.
- **Negative**: Invent a technical plan from a vague request, ignore platform mismatch because the feature is `strategic`, or skip cost and rollback analysis because the team can `figure it out during implementation`.

# Outputs
- `analysis/<topic>/technical-spec.md` as the implementation-facing technical baseline
- requirement-to-technical mapping with tasks, artifacts, and dependency notes
- cost-of-realization and feasibility constraints for each major workstream
- architecture-compliance results, conflicts, and rollback-to-alignment triggers

# Verification
- confirm every business requirement maps to concrete technical work or an explicit blocker
- confirm cost, sequencing, and operational burden are stated instead of implied
- confirm architecture-compliance self-check results are explicit
- confirm material conflicts trigger rollback guidance instead of optimistic hand-waving

# Red Flags
- the spec proceeds even though the business baseline is missing or contradictory
- the plan assumes architecture exceptions without naming them
- feasibility risk is hidden behind generic words such as `straightforward` or `minor`
- the document promises delivery without naming integration, migration, or operational cost

# Common Rationalizations
- `We can estimate after implementation starts.`
- `Architecture exceptions are just details.`
- `If the requirements and platform disagree, we can build around it later.`
- `The business baseline is close enough even though success still is not technically testable.`

# Boundaries
- Do not silently rewrite business intent to make implementation easier.
- Do not continue when the baseline is too vague to translate honestly.
- Do not start coding, scaffolding, or runtime execution.
- Do not hide impossible scope behind optimism or omit rollback triggers.

# Validation

## Required Checks
- PASS: `analysis/<topic>/requirements.md` exists and is readable before any technical decomposition begins
- BLOCKED: if the business baseline is missing, vague, or internally contradictory — stop spec authoring and route back to `business-intent-alignment` with the exact gap named

## Quality Checks
- every business requirement maps to concrete technical work or an explicit blocker
- cost, sequencing, and operational burden are stated rather than implied
- architecture-compliance self-check results are explicit
- material conflicts trigger rollback guidance rather than optimistic hand-waving

## On Soft Fail
- mark output as INCOMPLETE if partial technical tasks can be mapped but one or more requirements remain untranslatable without further clarification
- list each untranslatable requirement explicitly rather than silently omitting it

# Failure Handling

## Missing Context
- BLOCKED — if `analysis/<topic>/requirements.md` is not provided or cannot be read, stop and route back to `business-intent-alignment`; do not begin technical decomposition

## Ambiguous Requirement
- if a requirement is present but too vague to translate honestly, surface the specific ambiguity and stop rather than proceeding with guesswork
- if platform constraints or architecture rules are missing and their absence would change the feasibility result, name them as required inputs before continuing

## Execution Limitation
- if architecture-compliance rules are unavailable, mark the compliance section as INCOMPLETE and flag that a full architecture check could not be performed; do not omit rollback triggers because rules are missing
- do not force a technical plan when the baseline is too vague; return the vague requirements as explicit gaps

# Local references
- `reference.md`: stable rules for frozen-baseline gating, technical-spec shape, cost framing, architecture self-checks, and rollback behavior
- `examples.md`: detailed pessimistic-implementer scenarios, including conflict detection and rollback-to-alignment cases
- `checklist.md`: repeatable medium-risk misuse-prevention checks before declaring the technical spec review-ready
