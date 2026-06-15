---
name: python-async-await
description: Choose and design general Python async/await code with explicit async boundaries, structured concurrency, and clear cancellation and async-protocol behavior.
complexity: medium
risk_profile: [ambiguity_sensitive]
inputs:
  - whether the underlying work is actually async I/O, streaming, or async resource lifetime
  - whether concurrency is required or a direct `await` is enough
  - who owns spawned task lifetime, cancellation, and joining
  - whether async protocols such as `async with` or `async for` are needed
  - the Python runtime baseline and whether business code must stay 3.10-compatible
  - the project's semantic error family, such as `BaseAppError`
outputs:
  - a decision on whether code should stay synchronous or become `async`
  - a clear ownership model for direct awaits versus spawned tasks
  - structured-concurrency guidance for Python 3.10-compatible async code
  - boundary guidance for cancellation, grouped failures, and async protocols
  - supplementary AnyIO notes only when they do not replace the stdlib-first mainline
use_when:
  - deciding whether a function should remain synchronous or become `async def`
  - writing or reviewing coroutine code that awaits other async work
  - deciding whether work should be directly awaited or run concurrently under an explicit owner
  - designing `async with`, `async for`, async iterators, or async generators
  - reviewing cancellation, timeout, or grouped task-failure behavior
do_not_use_when:
  - the main task is framework-specific async runtime policy or server bootstrap
  - the main task is deep async testing guidance; use `python-testing-pytest`
  - the main task is synchronous `with` design; use `python-context-management`
  - the main task is general exception hierarchy design outside async-specific failure semantics; use `python-error-handling`
---

# Purpose
Choose when Python code should stay synchronous versus become `async`, and
design async code so task ownership, cancellation, and async protocols stay
explicit and reviewable.

# Trigger / When to use
Use this skill when:
- deciding whether a function should remain synchronous or become `async def`
- writing or reviewing coroutine code that awaits other async work
- deciding whether work should be directly awaited or run concurrently under an
  explicit owner
- designing `async with`, `async for`, async iterators, or async generators
- reviewing cancellation, timeout, or grouped task-failure behavior

Do not use this skill when:
- the main task is framework-specific async runtime policy or server bootstrap
- the main task is deep async testing guidance; use `python-testing-pytest`
- the main task is synchronous `with` design; use `python-context-management`
- the main task is general exception hierarchy design outside async-specific
  failure semantics; use `python-error-handling`

# Inputs
- whether the underlying work is actually async I/O, streaming, or async
  resource lifetime
- whether concurrency is required or a direct `await` is enough
- who owns spawned task lifetime, cancellation, and joining
- whether async protocols such as `async with` or `async for` are needed
- the Python runtime baseline and whether business code must stay 3.10-compatible
- the project's semantic error family, such as `BaseAppError`

# Process
1. **Choose sync versus async honestly** — Keep a function synchronous unless it
   truly needs async I/O, async protocols, or explicit async orchestration. Do
   not make code `async` just to look modern or to forward one synchronous call.
2. **Keep coroutine boundaries explicit** — An async call remains part of the
   caller's control flow until it is awaited. Prefer direct `await` when the
   caller owns the result and there is no real concurrency need.
3. **Create tasks only with an owner** — Spawn concurrent work only when some
   scope owns task lifetime, joining, cancellation, and failure handling. Treat
   scattered fire-and-forget `create_task` as a boundary or anti-pattern.
4. **Prefer structured concurrency** — On Python 3.10, use a wrapper or
   coordinator pattern that gives tasks one owner and a deterministic shutdown
   path. Keep the shape easy to migrate to native `TaskGroup` later. AnyIO may
   appear as a supplementary note, not as the required mainline.
5. **Treat cancellation as a contract** — Use cleanup in `finally`, but do not
   swallow `asyncio.CancelledError` and continue as if nothing happened.
6. **Make grouped failures explicit** — If concurrent tasks can fail together,
   preserve the semantic error family and surface the failure boundary
   intentionally instead of collapsing everything to one arbitrary error or
   silent background loss.
7. **Use async protocols only when they fit** — Use `async with` for async
   acquisition and cleanup, `async for` for async streams, and async generators
   when lazy async production really helps. Prefer simpler sync or non-generator
   shapes when they are clearer.

# Examples
- Positive: Keep a pure CPU helper synchronous, but use `async def` plus direct
  `await` for real async I/O and a coordinator-owned task group for concurrent
  child work.
- Positive: Use `async with` for an async client session and `async for` for a
  streamed result source whose lifetime and iteration are both asynchronous.
- Negative: Wrap synchronous code in `async def`, scatter `create_task` calls
  with no join path, and catch `CancelledError` only to return a sentinel value.

# Outputs
- a decision on whether code should stay synchronous or become `async`
- a clear ownership model for direct awaits versus spawned tasks
- structured-concurrency guidance for Python 3.10-compatible async code
- boundary guidance for cancellation, grouped failures, and async protocols
- supplementary AnyIO notes only when they do not replace the stdlib-first
  mainline

# Validation

Before proceeding, confirm:
- **Async boundary justified**: is the underlying work truly async I/O, streaming, or async resource lifetime — not just style?
- **Task ownership defined**: for any spawned tasks, is there an explicit owner, join path, and cancellation or failure policy?
- **Protocol semantics clear**: is `async with`, `async for`, or an async generator genuinely needed, or would a direct `await` suffice?

**SOFT FAIL** — ask and wait before continuing:
- Async boundary justification is unclear → cannot determine whether code should stay synchronous or become `async def`; ask before proceeding
- Task cancellation or failure policy is undefined → cannot safely design structured concurrency; ask before recommending `create_task` or task groups

**BLOCKED** — stop and redirect:
- The main task is framework-specific async runtime, server bootstrap, or worker lifecycle → out of scope; do not proceed
- The main task is deep async testing or pytest-asyncio plugin policy → redirect to `python-testing-pytest`

# Failure Handling

## Missing Context
- If async boundary justification, task ownership, or protocol requirements cannot be determined, mark output as INCOMPLETE and list the missing inputs.

## Ambiguous Requirement
- If blocking: stop and ask whether the work is truly async before recommending `async def`.
- If non-blocking: proceed with the synchronous default and document the assumption explicitly.

## Execution Limitation
- State the limitation explicitly.
- Do not fabricate an async pattern that cannot be justified by a real async boundary.

# Red Flags
- `create_task` calls that outlive the scope with no explicit owner
- `except asyncio.CancelledError:` followed by a normal success-shaped return
- `async def` wrappers around fully synchronous helpers with no async boundary
- framework event-loop, server, or worker bootstrap guidance drifting into the
  main decision path
- async generators used where one awaited result or a collected list is clearer

# Common Rationalizations
- "Making everything async now will save time later."
- "A background task is fine even if nobody waits for it."
- "Catching `CancelledError` and returning early is harmless cleanup."
- "AnyIO is close enough to the default, so we can make it the mainline."
- "`async for` is always better than collecting results first."

# Boundaries
- Do not define framework-specific async runtime, server, or worker policy.
- Do not define deep async testing patterns, pytest plugins, or test-client
  policy; use `python-testing-pytest`.
- Do not redefine general exception hierarchy or translation rules outside
  async-specific cancellation and grouped-failure semantics; use
  `python-error-handling`.
- Do not redefine synchronous context-manager design; use
  `python-context-management`.
- Do not normalize scattered fire-and-forget task spawning as an ordinary
  default.

# Local references
- `reference.md`: overview for the async reference layer and navigation to split
  topics
- `references/structured-concurrency.md`: sync-versus-async choice, direct
  `await` versus spawned-task ownership, Python 3.10-compatible structured
  concurrency, and the supplementary AnyIO note
- `references/cancellation-and-failure.md`: cancellation, timeout boundaries,
  grouped task failure, and preserving semantic async error meaning
- `references/async-protocols.md`: `async with`, `async for`, async iterators,
  async generators, and protocol-boundary anti-patterns
- `examples.md`: detailed positive and negative examples for async boundaries,
  structured concurrency, cancellation, grouped failure, and async protocols
