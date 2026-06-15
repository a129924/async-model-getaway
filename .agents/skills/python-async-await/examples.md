# Python Async/Await Examples

This file provides detailed positive and negative examples for choosing and
designing general Python async/await code. The examples assume the first-draft
mainline: explicit async boundaries, structured concurrency, explicit
cancellation semantics, and async protocols only when their ownership model is
real.

## Positive Scenarios

### Scenario A: Keep Pure Transformation Synchronous

```py
def build_slug(raw: str) -> str:
    return raw.strip().lower().replace(" ", "-")
```

Why this is correct:
- the work is pure and immediate
- there is no async protocol or async wait
- callers should not pay coroutine overhead for style only

---

### Scenario B: Direct `await` for an Owned Result

```py
async def load_user_profile(user_id: str) -> Profile:
    payload = await profile_client.get_json(f"/profiles/{user_id}")
    return Profile.from_payload(payload)
```

Why this is correct:
- the caller directly owns the awaited result
- no spawned task is needed
- the async boundary matches real async I/O

---

### Scenario C: Python 3.10-Compatible Structured Concurrency

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


async def load_dashboard(user_id: str) -> Dashboard:
    profile, permissions = await gather_owned(
        load_profile(user_id),
        load_permissions(user_id),
    )
    return Dashboard(profile=profile, permissions=permissions)
```

Why this is correct:
- one scope owns all spawned tasks
- failure triggers coordinated cancellation and join
- the orchestration shape can later migrate to native `TaskGroup`

---

### Scenario D: Cancellation Cleanup That Still Propagates

```py
import asyncio


async def forward_events() -> None:
    connection = await open_connection()
    try:
        await connection.forward_forever()
    except asyncio.CancelledError:
        await connection.flush()
        raise
    finally:
        await connection.aclose()
```

Why this is correct:
- cleanup runs on cancellation
- cancellation is not turned into a success-shaped result
- the caller still sees the cancellation boundary

---

### Scenario E: Grouped Failure with Semantic Error Family

```py
class BaseAppError(Exception):
    pass


class RefreshFanoutError(BaseAppError):
    pass


async def refresh_everything() -> None:
    try:
        await gather_owned(refresh_users(), refresh_projects())
    except BaseAppError:
        raise
    except Exception as exc:
        raise RefreshFanoutError("refresh fan-out failed") from exc
```

Why this is correct:
- grouped task failure is translated once at the orchestration boundary
- semantic project-level meaning is preserved
- 3.10-compatible code still keeps failure ownership explicit

---

### Scenario F: `async with` for Async Resource Lifetime

```py
async def fetch_order(order_id: str) -> dict[str, object]:
    async with order_client.session() as session:
        return await session.get_json(f"/orders/{order_id}")
```

Why this is correct:
- entry and exit are asynchronous
- lifetime fits one async block
- resource cleanup stays explicit and owned by the block

---

### Scenario G: `async for` over an Async Stream

```py
async def collect_ids(stream: EventStream) -> list[str]:
    ids: list[str] = []
    async for event in stream:
        ids.append(event.id)
    return ids
```

Why this is correct:
- values arrive through an async iteration protocol
- the stream boundary is explicit
- `async for` matches the source semantics

---

### Scenario H: Async Generator for Lazy Async Production

```py
async def iter_pages(api: APIClient):
    cursor: str | None = None
    while True:
        page = await api.fetch_page(cursor)
        for item in page.items:
            yield item
        if page.next_cursor is None:
            return
        cursor = page.next_cursor
```

Why this is correct:
- items are produced lazily over time
- fetching the next page is asynchronous
- the stream contract is real, not decorative

---

### Scenario I: Supplementary AnyIO Note

```py
import anyio


async def sync_pair() -> tuple[User, Project]:
    async with anyio.create_task_group() as tg:
        user_box: list[User] = []
        project_box: list[Project] = []
        tg.start_soon(load_user_into, user_box)
        tg.start_soon(load_project_into, project_box)
    return user_box[0], project_box[0]
```

Why this is acceptable only as a note:
- it follows the same structured-concurrency ownership model
- it is valid when the project already depends on AnyIO
- it must not replace the stdlib-first mainline of this skill

## Negative Scenarios

### Anti-pattern J: Scattered Fire-and-Forget Tasks

```py
import asyncio


async def refresh_batch(user_ids: list[str]) -> None:
    for user_id in user_ids:
        asyncio.create_task(refresh_user(user_id))
```

Why this is wrong:
- tasks have no explicit owner
- caller-visible completion does not mean the work finished
- failures can disappear into background noise

---

### Anti-pattern K: Swallowing `CancelledError`

```py
import asyncio


async def refresh_cache() -> bool:
    try:
        await cache.reload()
    except asyncio.CancelledError:
        return False
    return True
```

Why this is wrong:
- cancellation is hidden as a normal boolean result
- shutdown semantics become unclear
- callers cannot distinguish real completion from cancellation

---

### Anti-pattern L: Async Wrapper Around Sync Code

```py
async def slugify(raw: str) -> str:
    return raw.strip().lower().replace(" ", "-")
```

Why this is wrong:
- there is no real async boundary
- callers must `await` purely synchronous work
- the function shape suggests lifetime or orchestration that does not exist
