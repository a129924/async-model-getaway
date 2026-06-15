# Python Plan Review Examples

Use these examples after `SKILL.md` has already narrowed the task to reviewing a Python `*.plan.md` for executability.

---

## Approved / fully complete async-capable plan

A plan that:
- contains all 13 required top-level sections
- Decisions section addresses all 7 required decision topics with concrete answers
- includes the exact triggered async-planning subsections because the topic uses `AsyncSession`, `httpx.AsyncClient`, and timeout ownership
- Non-goals has 3 explicit `will not` items
- Implementation Steps are numbered, each naming a specific file and action
- Test Plan names all 5 required categories plus the async validation cases
- Validation Commands list specific runnable commands
- Risks and Rollback Plan each have at least one concrete item
- Open Questions has no blocking entries

**Abbreviated plan (relevant sections shown):**

```markdown
## Non-goals
- Will not convert domain entities to async objects.
- Will not add detached background tasks.
- Will not change unrelated route signatures.

## Decisions
- Async-planning status: triggered — cite trigger evidence: `AsyncSession`, `httpx.AsyncClient`, concurrent upstream HTTP calls, and a 2-second timeout owner
- Module placement: `src/app/routes/user_summary.py` and `src/app/services/user_summary.py`
- Public API: yes — add `GET /users/{user_id}/summary`
- Interface changes: additive route only
- Breaking changes: none
- New dependencies: none
- Error-handling strategy: infra failures translate at the API boundary
- Typing strategy: strict mypy with full annotations

### Async boundary decision
Route and application service are async because they await DB and HTTP I/O. Domain formatting helpers remain synchronous.

### Resource lifecycle decision
`AsyncSession` stays request-scoped. Shared `httpx.AsyncClient` is application-owned and closed at shutdown.

### Concurrency model
Run the two upstream HTTP calls concurrently under one service owner after the DB read completes.

### Failure model
If either upstream call fails, raise a translated application error; no partial success.

### Cancellation / timeout policy
A single 2-second timeout owner wraps the concurrent upstream calls. Cancellation propagates to child awaits and cleanup stays in `finally`.

### Validation plan
Cover timeout, cancellation cleanup, grouped upstream failure, and request-scoped session closure.

### Handoff notes for the implementer
Keep `AsyncSession` and `AsyncClient` out of domain objects. Do not introduce detached tasks.

## Test Plan
- Happy path: valid user summary request returns merged response
- Invalid input: malformed user id returns validation error
- Edge case: one upstream returns empty payload and the route still returns deterministic output
- Regression: existing synchronous domain formatting helpers still pass their tests unchanged
- Backward compatibility: unrelated route signatures and existing response envelope remain unchanged
- Async validation: timeout, cancellation cleanup, grouped failure, and request-scoped session closure cases are covered

## Validation Commands
pytest -v tests/test_user_summary.py && ruff check src/app && mypy src/app
```

**Verdict:**

```yaml
verdict: approved
blocking_issues: []
```

---

## Approved / exempt non-trigger case

A plan mentions async only to say the work will **not** change existing async behavior.

**Abbreviated plan excerpt:**

```markdown
## Non-goals
- Will not change the existing async worker topology.
- Will not add new I/O concurrency.
- Will not modify timeout or cancellation policy.

## Current Context
The repository already has an async worker baseline for ingest jobs, but this task only renames one internal DTO field used by synchronous formatters.

## Decisions
- Async-planning status: exempt — cite exemption evidence: internal synchronous DTO rename only; existing async worker topology, I/O concurrency, timeout, and cancellation baseline remain unchanged
- Module placement: `src/formatters/ingest_payload.py`
- Public API: no
- Interface changes: internal DTO field rename only
- Breaking changes: no
- New dependencies: none
- Error-handling strategy: keep current `ValueError` behavior
- Typing strategy: strict mypy
```

**Why this still passes without async subsections**
- the exact required `Async-planning status` field explicitly cites that async boundary, lifecycle, concurrency, timeout, and cancellation behavior are unchanged
- no new async-capable planning evidence is introduced

**Verdict:**

```yaml
verdict: approved
blocking_issues: []
```

---

## Needs-rework / retrofit required

A plan is already drafted, but review notices async-capable evidence and no async-planning coverage.

**Abbreviated plan problem:**

```markdown
## Current Context
The new worker will poll an external API with `httpx.AsyncClient`, use a semaphore to bound concurrency, and persist results through `AsyncSession`.

## Decisions
- Async-planning status: exempt — cite exemption evidence: no new async baseline claimed
- Module placement: `src/workers/sync_jobs.py`
- Public API: no
- Interface changes: none
- Breaking changes: none
- New dependencies: none
- Error-handling strategy: log and retry transient failures
- Typing strategy: fully typed
```

**Correct review behavior**
- async-capable evidence is present in the plan text
- reviewer must not silently accept the contradictory exemption claim or assume the missing boundary, lifecycle, timeout, and cancellation decisions
- the result is `needs-rework` with `retrofit required`

**Verdict:**

```yaml
verdict: needs-rework
blocking_issues:
  - section: Decisions
    issue: Async-capable evidence is present (`httpx.AsyncClient`, semaphore-bounded concurrency, `AsyncSession`), but `Async-planning status` incorrectly claims exemption and the required async-planning subsections are missing. retrofit required.
    fix: Replace the exemption line with `Async-planning status: triggered — cite trigger evidence: ...` and add `### Async boundary decision`, `### Resource lifecycle decision`, `### Concurrency model`, `### Failure model`, `### Cancellation / timeout policy`, `### Validation plan`, and `### Handoff notes for the implementer` under `## Decisions` before implementation continues.
```

---

## Needs-rework / missing exemption citation

A plan correctly stays outside the async-planning gate, but the exemption reason is not reviewable.

**Abbreviated plan problem:**

```markdown
## Decisions
- Async-planning status: exempt
- Module placement: `src/utils/slugify.py`
- Public API: no
- Interface changes: none
- Breaking changes: none
- New dependencies: none
- Error-handling strategy: preserve current `ValueError` behavior
- Typing strategy: fully typed
```

**Correct review behavior**
- the plan may be exempt, but the exemption reason is missing from the designated field
- reviewer must fail this as a contract issue, not as a style suggestion

**Verdict:**

```yaml
verdict: needs-rework
blocking_issues:
  - section: Decisions
    issue: `Async-planning status` claims `exempt` but does not cite the exemption evidence in repo-visible plan text.
    fix: Change the line to `Async-planning status: exempt — cite exemption evidence: ...` and name the specific exemption reason.
```

---

## Needs-rework / contradiction log required

The plan contains two conflicting async statements.

**Conflicting text:**

```markdown
## Decisions
- Async-planning status: exempt — cite exemption evidence: service layer remains synchronous

### Async boundary decision
Application services remain synchronous; only the route handler awaits external I/O.

### Resource lifecycle decision
The application service owns a shared `AsyncSession` and awaits DB queries directly.
```

**Correct review behavior**
- do not silently choose one statement
- require `### Async contradiction log` or a triggered retrofit
- keep the verdict in review space only

**Verdict:**

```yaml
verdict: needs-rework
blocking_issues:
  - section: Decisions
    issue: Plan-visible async evidence conflicts with the exemption claim and the async-planning subsections conflict on service-layer ownership, but no `### Async contradiction log` records the disagreement.
    fix: Add `### Async contradiction log` under `## Decisions` and record the contradiction, source A, source B, risk impact, decision owner / next action, and classification before implementation starts, or convert the plan to a triggered retrofit.
```

---

## Insufficient-context / truncated plan document

A plan file is cut off partway through, leaving several sections absent from the visible content.

**Document as received:**

```markdown
## Goal
Add a CSV parser to `src/weather/parser.py`.

## Non-goals
- Will not support JSON.
- Will not add async I/O.
- Will not change the public API.

## Current Context
We have a legacy ingestion script at `src/legacy/ingest.py` that is hard to maintain.

## Requirements
- The parser must accept a `Path` and return `list[WeatherRecord]`.

[Document truncated at line 48]
```

**Correct review behavior**
- return `insufficient-context`
- do not attempt quality checks on the visible sections
- do not infer what the missing sections might contain

**Verdict:**

```yaml
verdict: insufficient-context
blocking_issues:
  - section: (document)
    issue: Plan is truncated at line 48; multiple required sections are absent from the visible content.
    fix: Provide the complete *.plan.md file and re-run the review.
```
