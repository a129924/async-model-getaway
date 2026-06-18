# Business Intent Alignment Examples

Use these examples after `SKILL.md` has already narrowed the task to requirement alignment rather than technical design.

## Positive example: challenge a vague speed goal until it becomes measurable

**Starting claim**
- `We need partner onboarding to be much faster.`

**Socratic interviewer in action**
- `Which partner type is in scope: reseller, marketplace, or direct supplier?`
- `What counts as onboarding complete: account created, compliance approved, or first transaction processed?`
- `What is the current median completion time, and what target replaces it?`
- `What happens if compliance review is pending for more than one business day?`
- `What changes when the requester is missing approval rights or starts the flow outside business hours?`

**Aligned baseline excerpt**

```md
# Partner onboarding requirements
- Actor: partner operations analyst
- Requirement: create a new reseller onboarding case and submit it for compliance review in under 15 minutes from first data entry
- Evidence: system timestamps show draft start and review submission times
- Constraint: onboarding is not complete until compliance review status is `approved`
- Contradiction resolved: `same-day activation` applies only to low-risk resellers; high-risk resellers keep manual review
- Extreme boundary: if the compliance API is unavailable, the analyst must still save a complete draft and receive a retry status within 2 minutes
```

**Why this is correct**
- the interviewer forced a business definition of `faster`
- actor, scope, metric, and dependency behavior are explicit
- the compliance contradiction is surfaced rather than hidden

## Positive example: expose offline and interruption assumptions

**Starting claim**
- `Field reps should be able to place orders anywhere.`

**Socratic interviewer in action**
- `Does anywhere include no-network warehouses and rural customer sites?`
- `Can every field rep submit, or do some roles only draft orders?`
- `What happens if the device dies after line items are captured but before submission?`
- `What volume is expected during peak sales events?`
- `What business harm occurs if duplicate orders are created after reconnection?`

**Aligned baseline excerpt**

```md
# Mobile order capture requirements
- Actor: field sales representative
- Requirement: create and save a draft order with up to 50 line items without network access in under 2 minutes
- Requirement: only territory-approved reps may submit orders; trainees may save drafts but may not submit
- Requirement: if the device restarts before sync, the latest saved draft must be recoverable on the same device
- Acceptance signal: duplicate submitted orders caused by reconnection retries must remain below 0.1% of submitted orders per month
```

**Why this is correct**
- offline, wrong-role, interruption, and peak-volume realities were tested
- the baseline became measurable instead of aspirational
- the result is ready for technical translation without inventing business meaning later

## Negative example: soft wording that hides contradiction

**Input**
- `Customers want a simple dashboard and compliance wants full audit history.`

**Wrong response**
- `Requirement: provide a simple dashboard with full audit detail.`

**Why this fails**
- `simple` is still undefined
- the convenience vs audit-detail contradiction was never surfaced
- no actor, metric, or edge-case behavior appears

## Negative example: jump to solution before the baseline exists

**Input**
- `Make approvals faster for managers.`

**Wrong response**
- `We should build a new approval microservice and add push notifications.`

**Why this fails**
- the response switched from business alignment to technical design
- no measurable success target exists
- wrong-role, interruption, and dependency edge cases remain unknown
