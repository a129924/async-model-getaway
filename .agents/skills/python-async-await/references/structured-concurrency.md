# Structured Concurrency

Use this file when the main question is whether work should stay synchronous,
be directly awaited, or run concurrently under one explicit owner.

## Mainline rule

- Keep code synchronous unless it has a real async boundary.
- Prefer direct `await` when the caller owns the result and there is no
  concurrency need.
- Use spawned tasks only when one scope owns task lifetime, cancellation, and
  failure collection.
- On Python 3.10, prefer a stdlib-first coordinator pattern that preserves the
  same ownership model you would want from `TaskGroup` later.

## Sync versus async

```py
def normalize_name(raw: str) -> str:
    return raw.strip().title()


async def fetch_user(user_id: str) -> User:
    payload = await client.get_json(f"/users/{user_id}")
    return User.from_payload(payload)
```

Why this is the mainline:
- the pure transformation stays synchronous
- the network boundary becomes `async`
- async is used for a real async wait, not for style

## Direct `await`

```py
async def load_dashboard(user_id: str) -> Dashboard:
    profile = await load_profile(user_id)
    permissions = await load_permissions(user_id)
    return Dashboard(profile=profile, permissions=permissions)
```

Prefer direct `await` when:
- each result is immediately needed
- there is no independent concurrent owner
- sequencing is part of the business logic

## Python 3.10-compatible structured owner

```py
import asyncio
from collections.abc import Coroutine
from typing import Any


async def gather_owned(*coroutines: Coroutine[Any, Any, object]) -> list[object]:
    tasks = [asyncio.create_task(coro) for coro in coroutines]
    try:
        return await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        raise
    except Exception:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        raise
```

Why this is the mainline for 3.10:
- one scope owns task creation
- failure triggers coordinated cancellation
- shutdown is explicit and deterministic
- the shape upgrades cleanly to native `TaskGroup`

## AnyIO note

- AnyIO task-group patterns are acceptable as a supplementary note when the
  project already depends on AnyIO.
- Do not make AnyIO the required first-draft runtime or the only mental model.
- The portable rule is still one owner, explicit cancellation, and explicit
  failure collection.

## Anti-patterns

### Anti-pattern: scattered fire-and-forget tasks

```py
async def process_batch(items: list[Item]) -> None:
    for item in items:
        asyncio.create_task(process_item(item))
```

Why this is wrong for the mainline:
- no explicit owner joins the tasks
- failures can disappear into background logging or silence
- caller-visible completion no longer means the work is actually done

### Anti-pattern: async wrapper with no async boundary

```py
async def slugify(raw: str) -> str:
    return raw.strip().lower().replace(" ", "-")
```

Why this is wrong:
- adds coroutine overhead for a synchronous transformation
- makes callers `await` code that has no async lifetime or I/O reason
