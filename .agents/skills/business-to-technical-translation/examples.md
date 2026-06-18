# Business-to-Technical Translation Examples

Use these examples after `SKILL.md` has already narrowed the task to technical translation of a frozen baseline.

## Positive example: pessimistic implementer translates an offline baseline honestly

**Source baseline facts**
- field sales representatives must save an order with up to 50 line items offline in under 2 minutes
- only territory-approved reps may submit orders
- duplicate submitted orders after reconnect must stay below 0.1% per month

**Pessimistic implementer in action**
- `Offline capture means local encrypted storage, sync recovery, duplicate detection, and role enforcement on device. Which approved mobile storage options already exist?`
- `If none exist, this is not a small extension; it becomes a platform capability gap.`
- `Submission rights cannot rely only on server-time role checks because the device must still enforce draft-versus-submit behavior while offline.`
- `The duplicate-rate target creates a technical need for idempotency keys and reconciliation reporting, not only a sync button.`

**Technical-spec excerpt**

```md
# Mobile order capture technical spec
| Requirement | Technical realization | Dependencies | Cost / burden | Status |
| --- | --- | --- | --- | --- |
| save 50-line-item draft offline in under 2 minutes | encrypted on-device draft store, local validation, background sync queue | approved mobile storage library, device performance baseline | high implementation + medium support burden | feasible with prerequisites |
| only approved reps may submit | cached role snapshot, submit-gate on device, server reconciliation | identity service, device policy refresh | medium implementation burden | feasible |
| duplicates below 0.1% | idempotency key, sync retry ledger, duplicate-reporting job | order API change, analytics dashboard | medium implementation + ongoing monitoring | feasible |
```

**Architecture-compliance note**
- `Fits with prerequisites` if the approved mobile stack allows encrypted local storage.
- `Rollback trigger`: if the security policy prohibits approved encrypted local storage on the current platform, return to alignment and renegotiate the offline promise.

**Why this is correct**
- the translation stayed faithful to the baseline instead of shrinking it silently
- cost, prerequisites, and operational burden are explicit
- rollback behavior is defined before implementation starts

## Positive example: detect conflict and roll back instead of forcing a plan

**Source baseline facts**
- managers want customer-support tickets auto-routed with zero false assignments
- no additional model-training budget is approved this quarter
- routing must be explainable for audit review

**Pessimistic implementer in action**
- `Zero false assignments is stronger than any realistic probabilistic classifier target.`
- `Explainable audit review removes black-box routing as the default option.`
- `No training budget eliminates the highest-confidence machine-learning path for this quarter.`

**Correct rollback note**

```md
## Conflict requiring rollback to alignment
- Failing assumption: fully automatic routing can reach zero false assignments this quarter.
- Contradicting technical fact: the approved budget and explainability constraint eliminate the likely implementation paths that could approach the target.
- Required renegotiation: choose one of these before planning continues:
  - lower the target to measurable assisted-routing accuracy
  - fund a training and validation workstream
  - keep human confirmation in the routing flow
```

**Why this is correct**
- the implementer surfaced the technical impossibility early
- the response did not fake a compliant spec
- the rollback path names exactly what must change

## Negative example: optimism that hides real work

**Input baseline**
- `Partners should receive same-day activation after onboarding approval.`

**Wrong response**
- `Add an activation endpoint and a cron job. Effort should be small.`

**Why this fails**
- no traceability to prerequisites, approvals, or operational burden
- `small` is not a cost estimate
- no architecture-compliance check appears
- no rollback trigger exists if approvals or downstream systems cannot support same-day activation

## Negative example: proceed without a frozen baseline

**Input**
- `Users want a better dashboard soon.`

**Wrong response**
- `We'll build a new reporting service and redesign the UI.`

**Why this fails**
- the baseline is still vague and not measurable
- technical translation began before business alignment finished
- the response silently invented scope and architecture
