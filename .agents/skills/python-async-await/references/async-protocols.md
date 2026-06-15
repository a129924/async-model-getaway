# Async Protocols

Use this file when the main question is whether code needs `async with`,
`async for`, async iterators, or async generators.

## Mainline rule

- Use `async with` when acquisition or cleanup is asynchronous.
- Use `async for` when values arrive through an async iteration protocol.
- Use async generators when lazy async production materially improves the API.
- Prefer a plain awaited result or collected list when the stream shape is not
  buying clarity.

## `async with`

```py
async def fetch_profile(user_id: str) -> dict[str, object]:
    async with client_session() as session:
        return await session.get_json(f"/users/{user_id}")
```

Use `async with` when:
- entry or exit requires `await`
- resource cleanup must happen on both normal and error exit
- the lifetime really fits one async block

## `async for`

```py
async def collect_ids(stream: EventStream) -> list[str]:
    ids: list[str] = []
    async for event in stream:
        ids.append(event.id)
    return ids
```

Use `async for` when values are produced asynchronously over time, not merely
because the result happens to be a collection.

## Async generators

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

Async generators fit when:
- the caller benefits from lazy async production
- yielding items over time is part of the contract
- collecting everything first would blur lifetime or memory behavior

## Anti-patterns

### Anti-pattern: using `async with` for synchronous cleanup only

```py
async def export_report(path: str) -> None:
    async with open(path, "w") as f:
        f.write("done")
```

Why this is wrong:
- plain file objects are synchronous context managers
- the async protocol adds the wrong ownership model
- this belongs with synchronous `with`

### Anti-pattern: async generator when one awaited result is clearer

```py
async def iter_user(user_id: str):
    user = await load_user(user_id)
    yield user
```

Why this is wrong for the mainline:
- the protocol promises a stream but delivers one item
- a plain awaited `load_user()` return is clearer

### Anti-pattern: `async for` over pre-collected sync data

```py
async def emit_names(users: list[User]) -> None:
    async for user in users:
        print(user.name)
```

Why this is wrong:
- the collection is already synchronous
- the async protocol does not match the data source
