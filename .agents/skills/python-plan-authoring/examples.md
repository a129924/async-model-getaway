# Python Plan Authoring Examples

Detailed examples for `python-plan-authoring`.

---

## Positive exempt `## Decisions` excerpt: adding `validate_email()` to a utils module

**Feature request**
> Add a `validate_email(email: str) -> bool` function to the existing `src/utils/validation.py` module. It should raise `ValueError` for obviously malformed input and return `True` for valid addresses.

**Decisions supplied by the user**
- Module: `src/utils/validation.py`
- New public API: yes — `validate_email(email: str) -> bool`
- Interface changes: no existing interfaces modified
- Breaking changes: no
- New dependencies: no — use `re` from the standard library
- Error handling: raise `ValueError("Invalid email format: <value>")` for strings that are clearly not email addresses (empty, no `@`, no domain)
- Typing: fully typed with `str` parameter and `bool` return; no `Any`

**Non-goals supplied by the user**
- Will not modify the existing `validate_url()` function
- Will not add a CLI command or script
- Will not introduce an external email-validation library

**Required `## Decisions` excerpt**

```markdown
## Decisions
- Async-planning status: exempt — cite exemption evidence: synchronous validation helper with no async boundary, lifecycle, concurrency, timeout, or cancellation change
- Module/package placement: `src/utils/validation.py`
- New public API: yes — `def validate_email(email: str) -> bool`
- Interface changes: no existing interfaces modified
- Breaking changes allowed: no
- New dependencies: no — use `re` from the standard library
- Error handling strategy: raise `ValueError("Invalid email format: <value>")` for strings that are clearly not email addresses
- Typing strategy: fully typed with `str` parameter and `bool` return; no `Any`
```

**Why this passes**
- the exact required `Async-planning status` field is present
- the exemption reason is explicit in repo-visible plan text
- the plan correctly omits the async-planning subsection block because the topic is exempt

---

## Positive async-capable example: request-scoped DB plus concurrent upstream I/O

**Feature request**
> Add a FastAPI route that loads a user with `AsyncSession`, calls two upstream APIs with `httpx.AsyncClient`, and returns a merged response within a 2-second timeout budget.

**Why async planning is required**
- async endpoint boundary is explicit
- request-scoped DB resource lifetime matters
- multiple external I/O calls need a concurrency choice
- timeout and cancellation policy affect correctness before coding begins

**Required `## Decisions` shape**

```markdown
## Decisions
- Async-planning status: triggered — cite trigger evidence: FastAPI async route, `AsyncSession`, `httpx.AsyncClient`, concurrent upstream I/O, and a 2-second timeout budget
- Module/package placement: `src/app/routes/user_summary.py` and `src/app/services/user_summary.py`
- New public API: yes — `async def get_user_summary(user_id: UUID) -> UserSummaryResponse`
- Interface changes: no changes to existing route signatures outside the new endpoint
- Breaking changes allowed: no
- New dependencies: none
- Error handling strategy: infra exceptions translate at the API boundary; domain helpers stay exception-transparent
- Typing strategy: fully typed with existing project aliases

### Async boundary decision
The FastAPI route and application service are async because they await DB and HTTP I/O. Domain formatting helpers remain synchronous.

### Resource lifecycle decision
`AsyncSession` stays request-scoped through the existing dependency. A shared application-owned `httpx.AsyncClient` is created at startup and closed at shutdown.

### Concurrency model
The two upstream HTTP calls run concurrently under one application-service owner after the DB read completes. No detached background tasks are allowed.

### Failure model
DB failures propagate to the API boundary. If either upstream call fails, return a translated application error instead of partial success.

### Cancellation / timeout policy
One 2-second timeout owner wraps the upstream fan-out. Cancellation propagates to child awaits and cleanup stays in `finally` blocks.

### Validation plan
Cover happy path, upstream timeout, upstream failure, cancellation cleanup, and regression for request-scoped session closure.

### Handoff notes for the implementer
Do not move `AsyncSession` into domain-layer objects. Preserve the single timeout owner and shared-client lifetime.
```

**Why this passes**
- the normal 13 plan sections still exist
- async-capable evidence is recorded in the plan-visible `Async-planning status` field
- `python-async-planning` can be used as a routing aid for freezing the async baseline
- the plan freezes the async baseline before implementation begins

---

## Anti-pattern: async-capable topic with no async baseline

**Plan problem**
The plan says it will add a queue worker with retries, semaphore-limited HTTP fan-out, and `AsyncSession`, but `## Decisions` either omits `Async-planning status` or claims `exempt` without a citation and then ends after the standard seven bullets.

**Why this fails**
- the request is async-capable
- the plan artifact does not record a reviewable trigger or exemption decision
- lifecycle, concurrency, failure, and cancellation decisions are left for the implementer
- reviewer must return the plan for rework or `retrofit required`

**Correct repair**
Append the seven async-planning subsections under `## Decisions` before the plan is handed to review.

---

## Stop-and-ask: insufficient context before drafting an async-capable plan

**User request**
```
Create a plan for adding retry logic and async fan-out to our HTTP client.
```

**Why this is not authorable yet**
The request is missing the normal planning decisions and the async-planning baseline. Drafting now would require inventing module paths, ownership, timeout policy, and concurrency rules.

**What the skill should ask before drafting**
```
Before I draft the plan, I need:

1. The normal planning decisions:
   - target module or package
   - public API shape
   - interface changes and breaking-change policy
   - dependency decision
   - error handling strategy
   - typing strategy
2. At least 3 Non-goals.
3. Validation commands or the project config file to reference.
4. File-level implementation steps.
5. Async-planning inputs needed to freeze the triggered async baseline (use `python-async-planning` as the routing aid if needed):
   - What stays synchronous and what becomes async?
   - Who owns the HTTP client, retries, and cleanup?
   - Is fan-out sequential, bounded concurrent, batch, or streaming?
   - What is the timeout and cancellation owner?
   - How should grouped failures be surfaced?
   - What validation cases must prove the async design?
```

**What the skill must NOT do**
- invent a module path such as `src/http/retry.py`
- assume `httpx.AsyncClient` ownership without input
- write `Implementation Steps` like `"Add async retry logic"`
- skip the async-planning block because the details look implementation-specific
