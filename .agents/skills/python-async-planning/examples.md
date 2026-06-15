# Python Async Planning Examples

Use these examples after `SKILL.md` has already narrowed the task to Python planning-stage async risk.

---

## Positive: async-capable API orchestration plan

**Topic request**
> Add a FastAPI endpoint that reads with `AsyncSession`, calls two upstream services with `httpx.AsyncClient`, and returns a merged response within a 2-second timeout budget.

**Why the skill triggers**
- async endpoint ownership is explicit
- `AsyncSession` lifecycle must be frozen
- multiple external I/O calls require a concurrency decision
- timeout budget and failure behavior materially affect implementation

**Expected async-planning block inside `## Decisions`**

```markdown
### Async boundary decision
The FastAPI route handler and the application service it calls are async because they await DB and HTTP I/O. Domain policy helpers remain synchronous.

### Resource lifecycle decision
Request-scoped `AsyncSession` is created by the existing dependency provider and closed at request end. A shared application-owned `httpx.AsyncClient` is created at startup and closed at shutdown.

### Concurrency model
The two upstream HTTP calls run under bounded concurrency with a single owner in the route service. The DB read completes before fan-out so the transaction scope stays explicit.

### Failure model
Database failures propagate as infrastructure errors to the API boundary. If either upstream call fails, the service returns a translated application error rather than partial success.

### Cancellation / timeout policy
The route owner enforces a 2-second timeout around the upstream fan-out. Cancellation propagates to child awaits and cleanup runs in `finally` blocks only.

### Validation plan
Add tests for happy path, one-upstream failure, timeout, cancellation cleanup, and regression around request-scoped session closure.

### Handoff notes for the implementer
Do not move `AsyncSession` into domain-layer objects. Keep the shared `AsyncClient` at the application boundary and preserve the single timeout owner.
```

**Why this passes**
- all seven required subsections are present
- resource ownership and concurrency are explicit
- the plan stays Python-specific but framework-portable in its core rules

---

## Negative: syntax-only coroutine fix

**Topic request**
> Fix a missing `await` in `tests/test_worker.py`.

**Why the skill does not trigger**
- this is a local bug repair
- there is no new async boundary, lifecycle, concurrency, or cancellation decision
- forcing the async-planning gate would create a false positive

**Correct behavior**
- keep the task outside `python-async-planning`
- if planning is still needed, use ordinary `python-plan-authoring` without the async-planning block

---

## Retrofit required: late-discovered async risk

**Existing plan problem**
A drafted plan already says it will add a queue worker, semaphore-limited HTTP fan-out, and retry policy, but `## Decisions` contains only the standard seven plan-authoring bullets and no async-planning subsections.

**Correct review reaction**
- verdict stays `needs-rework`
- the blocking issue must say `retrofit required`
- the fix is a focused backfill of the async-planning subsections, not a silent pass and not an automatic full re-plan

**Reviewer wording example**

```yaml
verdict: needs-rework
blocking_issues:
  - section: Decisions
    issue: Async-capable evidence is present (queue worker ownership, semaphore-limited HTTP fan-out, retry / timeout policy), but the required async-planning subsections are missing. retrofit required.
    fix: Under `## Decisions`, add `### Async boundary decision`, `### Resource lifecycle decision`, `### Concurrency model`, `### Failure model`, `### Cancellation / timeout policy`, `### Validation plan`, and `### Handoff notes for the implementer` before implementation continues.
```

---

## Contradiction example: reviewer must log, not smooth over

**Plan conflict**
- `### Async boundary decision` says the service layer stays synchronous.
- `### Resource lifecycle decision` later says the same service owns a shared `AsyncSession` and awaits DB work directly.

**Correct behavior**
Add an async contradiction log instead of silently editing one subsection to match the other.

```markdown
### Async contradiction log
| Contradiction | Source A | Source B | Risk impact | Decision owner / next action | Classification |
| --- | --- | --- | --- | --- | --- |
| Service layer described as synchronous, but later text gives it direct `AsyncSession` ownership and awaited DB work | `### Async boundary decision` | `### Resource lifecycle decision` | Layer leakage and incorrect implementation ownership | Technical lead to confirm whether async stays at API boundary or moves into application service before coding starts | blocking |
```

**Why this matters**
Without the log, review would silently choose a design and the frozen baseline would drift.
