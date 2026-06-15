# Cancellation and Failure

Use this file when the main question is how async code should react to
`CancelledError`, timeouts, and grouped task failure without losing semantic
meaning.

## Mainline rule

- Cancellation is not a normal success path.
- Cleanup belongs in `finally`, but cancellation should usually propagate after
  cleanup completes.
- Timeouts and grouped task failures should surface at explicit boundaries.
- When a project already uses a semantic root such as `BaseAppError`, preserve
  that family when translating known async failures instead of silently
  discarding task failures.

## Cancellation propagation

```py
import asyncio


async def stream_events() -> None:
    connection = await open_stream()
    try:
        await connection.consume_forever()
    except asyncio.CancelledError:
        await connection.flush()
        raise
    finally:
        await connection.aclose()
```

Why this is the mainline:
- cleanup still runs
- cancellation is not converted into a normal return
- caller-visible cancellation remains intact

## Timeout boundary

```py
import asyncio


async def load_snapshot() -> Snapshot:
    try:
        return await asyncio.wait_for(fetch_snapshot(), timeout=2.0)
    except asyncio.TimeoutError as exc:
        raise SnapshotLoadError("snapshot timed out") from exc
```

Timeouts belong at an explicit boundary that can add semantic meaning. Do not
scatter tiny timeout wrappers across every await.

## Grouped task failure in Python 3.10

```py
class BaseAppError(Exception):
    pass


class SyncFanoutError(BaseAppError):
    pass


async def run_fanout() -> None:
    try:
        await gather_owned(refresh_customers(), refresh_orders())
    except BaseAppError:
        raise
    except Exception as exc:
        raise SyncFanoutError("fan-out failed") from exc
```

Why this is the mainline:
- grouped failure is handled at one orchestration boundary
- semantic project-level meaning is preserved
- the first draft stays 3.10-compatible without pretending `ExceptionGroup`
  already exists

## Anti-patterns

### Anti-pattern: swallowing cancellation

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
- hides cancellation as a normal boolean result
- makes shutdown and caller intent harder to reason about

### Anti-pattern: letting one arbitrary task failure stand in for all grouped failures

```py
async def sync_all() -> None:
    await asyncio.gather(sync_users(), sync_projects(), sync_roles())
```

Why this is incomplete by itself:
- no explicit semantic boundary owns the combined failure story
- later translation and cancellation behavior are left implicit
- reviewer cannot tell how domain failures should surface
