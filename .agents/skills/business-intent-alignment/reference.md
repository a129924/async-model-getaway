# Business Intent Alignment Reference

Use this file after `SKILL.md` has already narrowed the task to turning business intent into a measurable baseline.

## Frozen baseline shape

A strong `analysis/<topic>/requirements.md` usually includes:
- a short problem statement in business terms
- named actors and permission boundaries
- measurable requirements with condition, metric, target, and evidence signal
- explicit assumptions and non-goals
- a contradiction log or a clear statement that no contradictions survived review
- blocker notes when unresolved decisions still prevent technical translation

Recommended requirement framing:

| Element | Question |
| --- | --- |
| Actor | Who needs the outcome or performs the action? |
| Condition | Under what situation does the requirement apply? |
| Observable result | What must happen that another person could verify? |
| Metric or decision rule | How do we know the result is good enough? |
| Failure meaning | What business harm occurs if this fails? |

## Measurability conversion rules

Turn soft language into evidence:
- `fast` -> specific completion time, queue time, or response deadline
- `simple` -> maximum steps, required training level, or error-rate threshold
- `accurate` -> precision, reconciliation tolerance, or defect ceiling
- `better` -> named baseline plus a target delta

If stakeholders cannot name a numeric metric, require an observable decision rule instead. `Manager can verify the correct escalation path in one screen without opening a second system` is stronger than `easier workflow`.

## Contradiction surfacing rules

Treat these as common contradiction families:
- convenience vs compliance
- automation vs mandatory approval
- broad access vs role restrictions
- speed vs auditability
- one shared workflow vs channel-specific exceptions

Record contradictions explicitly:
1. statement A
2. statement B
3. why both cannot be true at the same time
4. which human decision is required

Do not average contradictory statements into watered-down prose.

## Extreme-boundary probes

At minimum, probe these conditions:
- no network, slow dependency, or partial third-party outage
- wrong user role, expired permission, or missing approver
- interrupted flow, duplicate submission, or partial completion
- minimum usage and peak usage
- cut-off windows, compliance retention, or audit reconstruction

Useful prompts:
- `What must still happen if the external dependency is unavailable for 30 minutes?`
- `What changes when the actor has view access but not approval rights?`
- `What is the acceptable state if the process stops halfway through?`
- `Which rule changes at the highest expected volume?`

## Freeze rule

Only treat the baseline as ready for downstream technical translation when:
- each in-scope requirement has a named actor and observable outcome
- vague adjectives have been converted to measurable or decision-rule language
- contradictions are resolved or explicitly marked as blockers
- extreme-boundary checks did not reveal hidden requirement changes

If blockers remain, the file should say it is not ready for technical translation yet. Do not disguise a blocked baseline as a frozen one.
