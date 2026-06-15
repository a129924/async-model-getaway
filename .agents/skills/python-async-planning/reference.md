# Python Async Planning Reference

Use this file with `SKILL.md` when you need the stable decision rules behind the async-planning gate.

## Trigger evidence

Async planning is triggered when the topic introduces planning-stage uncertainty around one or more of these signals:

| Evidence | Why it triggers planning |
| --- | --- |
| `async def`, `await`, `asyncio`, or AnyIO with architecture impact | The plan must freeze where async begins and why |
| FastAPI async endpoints | Request lifecycle, cancellation, and dependency ownership can change implementation shape |
| `httpx.AsyncClient`, `aiohttp`, `AsyncSession`, or async engine | Client / session ownership and cleanup must be frozen |
| async repository or async Unit of Work design | Transaction and lifetime boundaries move across layers |
| workers, queues, schedulers, or background tasks | Ownership, retry, timeout, and shutdown rules matter before coding |
| semaphores, pools, rate limits, retries, timeouts, cancellation, or backpressure | Concurrency and failure semantics cannot be left implicit |
| multiple external I/O calls | The plan must justify sequential, concurrent, batch, or streaming execution |
| sync-to-async conversion | Existing boundaries and compatibility assumptions may change |

## Exemption rules

Do not trigger async planning for these by default:

| Exempt case | Why it stays out of scope |
| --- | --- |
| syntax-only async / await teaching | No planning-stage architecture decision is being made |
| a single missing `await` or local coroutine bug | Local repair does not require a frozen async baseline |
| lint, formatting, or typing-only work | No async boundary or lifecycle decision changes |
| pure CPU-bound work with no worker or offload design | Async I/O planning is not the real problem |
| synchronous refactors with no async resource or failure-model change | The workflow should stay lightweight |
| a topic that already has a complete async baseline and does not change it | Re-freezing the same decision adds noise without new control |

When you exempt a topic, cite the exemption explicitly. Silent exemption is not good enough for review.

## Required plan placement

For triggered topics, place the async baseline inside `## Decisions` of the target plan using these exact subsection names:

1. `### Async boundary decision`
2. `### Resource lifecycle decision`
3. `### Concurrency model`
4. `### Failure model`
5. `### Cancellation / timeout policy`
6. `### Validation plan`
7. `### Handoff notes for the implementer`

Recommended pattern:
- keep each subsection short and decision-focused
- name owners, boundaries, and failure semantics directly
- avoid framework-only wording unless the topic truly depends on that framework

## Async contradiction log format

When request, plan, review, or existing baseline disagree, add `### Async contradiction log` under `## Decisions` and use this table:

| Contradiction | Source A | Source B | Risk impact | Decision owner / next action | Classification |
| --- | --- | --- | --- | --- | --- |
| ... | ... | ... | ... | ... | blocking / non-blocking |

Use `No async contradictions.` only when the reviewer or author explicitly checked for conflicts and found none.

## Retrofit required

Use `retrofit required` when async risk is discovered after a plan already exists.

Minimum retrofit expectation:
- add the seven named async-planning subsections under `## Decisions`
- freeze at least the boundary, lifecycle, concurrency, failure, cancellation / timeout, validation, and handoff decisions before implementation continues
- add `### Async contradiction log` when the new baseline conflicts with existing plan text
- keep unrelated plan sections stable unless contradiction resolution forces a targeted edit

`retrofit required` is a controlled backfill, not permission for silent continuation and not a demand for a full re-plan by default.

## Portability boundaries

Keep the core rule set portable across general Python async I/O planning:
- FastAPI, SQLAlchemy, httpx, queue runners, and DDD layering may appear in examples only
- domain layers should not depend directly on `asyncio`, FastAPI runtime objects, ORM session objects, or HTTP client objects unless the topic explicitly requires that boundary
- choose async only where the plan can justify async I/O, async resource lifetime, or explicit async orchestration
