---
name: scope-draft-plan
description: Converge a vague or over-fragmented product or engineering request into one independently acceptable Bounded Context Mission Draft Plan. Use before implementation planning when scope needs to become a complete end-to-end capability.
complexity: medium
risk_profile:
  - ambiguity_sensitive
inputs:
  - the user's stated product or engineering need
  - the minimum available repository, domain, contract, and planning context
  - known actors, constraints, ownership boundaries, and irreversible risks
outputs:
  - one conversational BC Mission Draft Plan
  - at most three material clarification questions when a safe recommendation is impossible
use_when:
  - a request is vague, spans too many independent outcomes, or has been split into technical-layer tasks
  - the user asks to cut scope, identify a first mission, focus on the core path, or prepare for SDD planning
  - a complete business capability must be selected before an implementation plan is written
do_not_use_when:
  - the mission boundary and acceptance conditions are already approved and the user asks for an implementation plan
  - the user asks for direct implementation or a small, already-bounded bug fix
  - the work is only a research or feasibility spike with no intended business capability
---

# Purpose

Converge one vague or over-fragmented request into one right-sized Bounded
Context (BC) Mission Draft Plan. The Mission is the smallest complete,
observable end-to-end business capability, not a technical layer.

# Trigger / When to use

Use this skill when:

- a request needs a sensible first Mission before SDD or implementation planning;
- a proposed scope is only a repository, DTO, database, service, API, adapter,
  controller, or test task;
- a request bundles several independently valuable lifecycle outcomes; or
- ownership, primary BC, or the core result needs bounded scope convergence.

Do not use this skill when:

- an approved Mission already has clear boundaries and needs an implementation
  plan;
- the requested work is direct implementation, code review, or a bounded bug
  fix; or
- the output should be a pure feasibility spike rather than a deliverable
  business capability.

# Inputs

- the original request and intended actor or system outcome, if known;
- the minimum relevant repository context: `AGENTS.md`, domain/architecture
  documents, glossary, invariants, contracts, existing plans, and directly
  related code when available;
- known BC ownership, public contracts, dependencies, security constraints, and
  irreversible effects.

# Process

1. Confirm that scope convergence is the needed job. Do not turn a request for
   implementation planning, code changes, or a bounded fix into a new Draft
   Plan.
2. Read only the context needed to identify the business meaning and boundary.
   Treat repository governance and established ownership as constraints; do not
   conduct a whole-codebase audit or invent missing architecture.
3. Restate the request in one to three sentences. Identify the actor, core
   problem, observable result, and consequence of not solving it.
4. Name the primary BC, its likely aggregate or domain object, actor, and data
   owner. When an exact BC name is unavailable, use a functional responsibility
   and label it as an assumption.
5. Internally compare plausible cuts, then recommend exactly one Mission: one
   primary BC, one main result, one happy path, and the necessary core failure
   path. Keep repository, DTO, database, service, API, and verification work as
   technical tasks within that Mission.
6. Apply the sizing rules in `references/scope-sizing.md`. Move separate
   valuable outcomes, unrelated lifecycle stages, and unowned cross-BC work to
   follow-up or dependent Missions.
7. Ask at most three clarification questions only when an answer would
   materially change the primary BC, core result, data ownership, public
   contract, irreversible risk, or whether the work is a spike. Otherwise state
   a reasonable assumption and continue.
8. Produce the localizable Draft Plan using
   `references/output-template.md`. Default to Traditional Chinese when
   repository governance or the human does not specify another language. Keep
   it conversational; do not write repository artifacts.
9. Offer only conditional, non-binding next-step guidance using
   `references/handoff-routing.md`, then stop. Do not invoke a skill, dispatch
   an agent, require a workflow gate, create files, or start implementation.

# Examples

- Positive: Reframe “create an `OrderRepository`” into a Mission that lets the
  intended actor create a basic order, preserves the necessary order snapshot,
  returns an identifier, and lists persistence and API work as one technical
  task map.
- Negative: Produce separate Missions for an order table, repository, DTO,
  service, endpoint, and tests, or silently include payment, refund, shipment,
  and return flows in the first order-creation Mission.

# Outputs

- exactly one recommended BC Mission Draft Plan in the requested or default
  language;
- explicit assumptions, in-scope and out-of-scope boundaries, observable
  acceptance criteria, risk gates, and follow-up capabilities;
- optional non-binding next-step suggestions, or up to three blocking questions
  when no truthful recommendation can be made.

# Validation

## Required Checks

- PASS: the recommendation describes one observable business capability with a
  primary BC, actor, ownership boundary, happy path, and essential failure path.
- PASS: every technical layer remains inside the same Mission's technical task
  map rather than becoming its own SDD project.
- PASS: the Draft Plan has explicit in/out boundaries, Given/When/Then behavior,
  implementation-independent acceptance criteria, assumptions, and follow-ups.
- BLOCKED: stop for human input when unresolved alternatives would materially
  change the primary BC, core result, data ownership, public contract,
  irreversible risk, or spike-versus-Mission classification.

## Quality Checks

- the recommended Mission can be independently demonstrated, tested, reviewed,
  and rolled back;
- cross-BC work is named as a contract dependency or dependent Mission, not
  silently absorbed;
- the output does not contain file-by-file implementation steps or require a
  particular technical design.

## On Soft Fail

- mark the Draft Plan's scope confidence as low or medium;
- state the missing context and bounded assumptions explicitly;
- continue only when those gaps do not alter the recommended Mission's core
  boundary.

# Failure Handling

## Missing Context

- Use the smallest defensible assumption set when missing details do not change
  the Mission boundary; show those assumptions in the Draft Plan.
- Return INCOMPLETE guidance and name the missing context when it prevents a
  credible sizing or acceptance decision.

## Ambiguous Requirement

- Ask no more than three focused questions and wait when competing answers
  materially change the Mission.
- Do not manufacture a generic technical solution to avoid a BC, ownership, or
  public-contract decision.

## Execution Limitation

- State when relevant domain, contract, or ownership evidence is unavailable.
- Do not fabricate repository facts, contracts, migrations, or implementation
  details to make the Draft Plan look complete.

# Boundaries

- Do not write a full implementation plan, create `analysis/` or `plan/`
  artifacts, modify code, create migrations, or implement the Mission.
- Do not dispatch agents, invoke downstream skills, impose mandatory routing, or
  claim approval.
- Do not reopen locked architecture, path, ownership, or contract decisions.
- Do not treat technical layers as independent Missions or turn every technical
  task into a separate SDD workflow.
- Stop after the Draft Plan and any non-binding next-step guidance.

# Local references

- `reference.md`: local glossary, output boundary, and reference-routing rules.
- `references/scope-sizing.md`: signals and remedies for too-small, too-large,
  and right-sized Missions.
- `references/output-template.md`: localizable, implementation-neutral Draft
  Plan structure.
- `references/handoff-routing.md`: advisory-only next-step suggestions and stop
  rules.
- `examples.md`: detailed positive, negative, cross-BC, and ambiguity cases.
- `checklist.md`: repeatable pre-output scope and handoff checks.
