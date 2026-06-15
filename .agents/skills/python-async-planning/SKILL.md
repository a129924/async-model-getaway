---
name: python-async-planning
description: Freeze Python async planning decisions before implementation when a topic introduces async boundary, lifecycle, concurrency, failure, or cancellation risk.
complexity: high
risk_profile:
  - ambiguity_sensitive
  - multi_agent_handoff
inputs:
  - the Python planning request or existing plan draft
  - repo-visible async-capable evidence and any exemption evidence
  - current sync or async boundaries, resource owners, and external I/O surfaces
  - failure, timeout, cancellation, retry, or backpressure expectations
  - whether async risk was discovered during initial planning or as a late retrofit
outputs:
  - a justified trigger or exemption decision for async planning
  - the required named async-planning subsections for the plan baseline
  - contradiction-log requirements when sources disagree
  - retrofit-required guidance for late-discovered async risk
  - implementer handoff notes that keep async ownership explicit
use_when:
  - a Python planning task introduces async-capable architecture or execution-safety decisions
  - a reviewer or author needs a frozen async baseline before implementation proceeds
  - an existing Python plan must be retrofitted after async risk is discovered late
do_not_use_when:
  - the task is syntax-only async teaching or a local missing-await bug with no planning impact
  - the task is implementation, code review, or framework bootstrap rather than planning
  - the topic is pure CPU work with no async resource lifetime, concurrency, or cancellation risk
---

# Purpose
Freeze the async decision baseline for Python implementation plans before coding begins so executors do not guess about async boundary, resource lifetime, concurrency, failure behavior, or cancellation.

# Trigger / When to use
Use this skill when:
- a Python plan request includes async-capable evidence that can change architecture or execution safety
- the topic introduces or revisits async I/O boundaries, pooled resources, task ownership, worker ownership, or timeout / cancellation policy
- a reviewer finds async risk late and the plan needs a controlled retrofit instead of silent continuation

Async-capable trigger evidence includes one or more of:
- `async def`, `await`, `asyncio`, or AnyIO usage with planning impact
- FastAPI async endpoints
- `httpx.AsyncClient`, `aiohttp`, `AsyncSession`, or async engine ownership
- async repository or async Unit of Work design
- background tasks, queues, schedulers, or workers whose ownership matters
- connection pools, session pools, semaphores, rate limits, retries, timeouts, cancellation, or backpressure policy
- multiple external I/O calls that need a choice between sequential, concurrent, batch, or streaming execution
- sync-to-async conversion of an existing pipeline or boundary

Do not use this skill when:
- the task is syntax-only async teaching, a single missing `await`, or a local coroutine bug with no planning impact
- the task is lint, formatting, typing-only, or other non-architectural cleanup
- the work is pure CPU-bound logic with no offload, worker, process-pool, or async resource design
- a complete async baseline already exists and the current change does not alter async boundary, resource lifecycle, concurrency model, or failure model
- the main task is framework-specific runtime bootstrap or worker-server policy rather than plan authoring

# Inputs
- the Python topic request or drafted `*.plan.md`
- the specific async-capable evidence, if any
- exemption evidence when the topic should stay outside the async-planning gate
- the current and proposed async boundaries, including sync-to-async seams
- resource ownership details for clients, sessions, pools, workers, streams, or semaphores
- the expected concurrency, failure, timeout, retry, cancellation, and backpressure behavior
- any contradictions between request, plan, review notes, or existing baseline
- whether the async risk was discovered during authoring or as a late retrofit

# Process
1. Decide whether the topic is actually async-capable.
   - Cite the trigger evidence explicitly.
   - If the topic is exempt, cite the exemption explicitly.
   - Write or update the first repo-visible line under `## Decisions` as exactly one of:
     - `- Async-planning status: triggered — cite trigger evidence: ...`
     - `- Async-planning status: exempt — cite exemption evidence: ...`
   - Keep this status line at the start of `## Decisions` even when the topic is exempt.
   - Do not route on style alone.
2. If async planning is triggered, place the async baseline inside `## Decisions` of the plan using these exact named subsections and this exact order:
   - `### Async boundary decision`
   - `### Resource lifecycle decision`
   - `### Concurrency model`
   - `### Failure model`
   - `### Cancellation / timeout policy`
   - `### Validation plan`
   - `### Handoff notes for the implementer`
3. Fill each subsection with concrete, repo-visible decisions.
   - `Async boundary decision`: what stays synchronous, what becomes async, and why.
   - `Resource lifecycle decision`: who creates, owns, shares, and closes async resources.
   - `Concurrency model`: direct await, bounded fan-out, batching, streaming, worker ownership, or explicit sequential execution.
   - `Failure model`: which failures propagate, which are translated, and where grouped failures surface.
   - `Cancellation / timeout policy`: cancellation owner, timeout boundary, retry boundary, and cleanup expectations.
   - `Validation plan`: how the async decisions will be tested or validated before implementation is considered complete.
   - `Handoff notes for the implementer`: concise execution notes so implementation does not rediscover async assumptions from chat.
4. When sources disagree, require a contradiction log instead of silently choosing one version.
   - Add `### Async contradiction log` under `## Decisions` when request, plan, review, or existing baseline conflict.
   - Record each contradiction with: contradiction, source A, source B, risk impact, decision owner / next action, and blocking or non-blocking classification.
5. If async risk is discovered after a plan already exists, mark the case as `retrofit required`.
   - Add the async-planning subsections as a focused retrofit.
   - Keep unrelated plan sections stable unless the contradiction resolution forces a targeted edit.
   - Do not demand a full re-plan when a concise retrofit can safely freeze the missing async decisions.
6. Keep the guidance portable.
   - FastAPI, SQLAlchemy, httpx, queues, and DDD layering may appear in examples, not as prerequisites.
   - Do not force domain layers to depend directly on `asyncio`, FastAPI runtime objects, HTTP clients, or ORM session objects.
7. Stop at a review-ready async baseline. Do not approve the plan and do not write implementation code.

# Examples
- Positive: A plan for a FastAPI endpoint that uses `AsyncSession`, `httpx.AsyncClient`, and bounded concurrent upstream calls adds all seven async-planning subsections before implementation.
- Positive: A drafted plan for a queue worker is updated with `retrofit required` after review notices missing timeout and cancellation ownership.
- Negative: A request to explain why one coroutine is missing `await` is routed into async planning even though no boundary, lifecycle, or concurrency decision exists.
- Negative: A reviewer notices async evidence, rewrites the plan decision mentally, and approves without requiring async sections or a contradiction log.

# Outputs
- a justified repo-visible `- Async-planning status: triggered|exempt — cite ...` line at the start of `## Decisions`
- the seven required named async-planning subsections inside `## Decisions` when triggered
- `retrofit required` guidance for late-discovered async risk
- a contradiction-log requirement when sources disagree
- implementer handoff notes that preserve async ownership, lifecycle, and failure assumptions

# Validation

## Required Checks
- the topic is confirmed to be a Python planning task, not implementation or code review
- trigger evidence or exemption evidence is cited explicitly
- `## Decisions` begins with the repo-visible `- Async-planning status: triggered|exempt — cite ...` line
- async-capable topics include all seven required named async-planning subsections under `## Decisions`
- contradiction handling uses `### Async contradiction log` instead of silent override when sources disagree
- late-discovered async risk is labeled `retrofit required` rather than passed through silently
- examples and wording stay portable across general Python async I/O planning

## Quality Checks (best effort)
- resource ownership is explicit for every async client, session, pool, worker, or stream
- the concurrency model names why work is sequential, concurrent, bounded, batched, or streamed
- the failure model and cancellation / timeout policy align with the chosen concurrency model
- handoff notes are short but sufficient for an implementer to follow without rediscovering assumptions from chat

## PASS
- async planning is either triggered with cited evidence and all required subsections, or explicitly exempted with cited evidence
- contradictions are logged rather than overwritten
- portability boundaries remain intact

## SOFT FAIL
- mark output as INCOMPLETE
- continue with the best async baseline that can be justified from visible evidence
- list every missing async input, ownership detail, or ambiguity explicitly

## BLOCKED
- stop when the task is not Python planning work or is really implementation / runtime bootstrap work
- stop when the evidence cannot distinguish a real async-planning problem from a syntax-only issue and proceeding would materially change the workflow path
- stop when two conflicting async baselines exist and no decision owner or next action can be named

# Failure Handling

## Missing Context
- mark output as INCOMPLETE when trigger evidence exists but resource ownership, failure semantics, or cancellation ownership is missing
- list the missing inputs explicitly so the plan author or reviewer can resolve them without guessing

## Ambiguous Requirement
- if blocking: stop and ask whether the topic changes async boundary, lifecycle, concurrency, failure model, or cancellation policy
- if non-blocking: proceed with the narrowest safe interpretation and record the assumption plus any needed contradiction-log entry

## Execution Limitation
- state the limitation explicitly
- do not fabricate async boundaries, timeout policy, or resource ownership that are not supported by visible evidence

# Workflow State Contract
When participating in a multi-agent planning workflow, include:
- current_step: trigger-check | async-baseline | contradiction-log | retrofit | DONE
- next_step: async-baseline | contradiction-log | retrofit | plan-review | DONE
- status: IN_PROGRESS | COMPLETE | INCOMPLETE | BLOCKED

# Verification
- confirm the topic is Python-specific and planning-stage only
- confirm the trigger or exemption decision can be explained from repo-visible evidence
- confirm `## Decisions` starts with the repo-visible `- Async-planning status: triggered|exempt — cite ...` line
- confirm the async-planning subsections use the exact required names when triggered
- confirm contradictions are logged instead of silently resolved
- confirm retrofit cases ask for the minimum safe backfill rather than a silent pass or uncontrolled full rewrite

# Red Flags
- treating `async def` as automatic proof of planning-stage async risk without checking the actual boundary decision
- approving a plan with pooled clients, async DB sessions, or cancellation policy but no async-planning subsections
- forcing FastAPI, SQLAlchemy, or any specific framework into the core rule set
- letting implementation or review silently override the frozen async baseline
- calling for a full re-plan when a focused retrofit would safely freeze the missing async decisions

# Common Rationalizations
- "It only mentions `AsyncClient`, so the implementer can decide the rest later."
- "Timeouts and cancellation are implementation details, not planning inputs."
- "The reviewer can just fix the async wording during review."
- "Because this uses FastAPI, the planning rules can assume FastAPI everywhere."
- "A late async discovery means we should keep going and skip the paperwork."

# Boundaries
- Do not use this skill for non-Python topics.
- Do not use this skill for syntax-only async help, local bug repair, or framework bootstrap policy.
- Do not broaden this skill into a general async implementation or runtime-design skill.
- Do not silently override contradictions between request, plan, review, or implementation.
- Do not force domain layers to become async by default.
- Do not approve the resulting plan.

# Local references
- `reference.md`: trigger evidence, exemption rules, contradiction-log format, retrofit expectations, and portability boundaries
- `examples.md`: positive, negative, contradiction, and retrofit scenarios for async planning
