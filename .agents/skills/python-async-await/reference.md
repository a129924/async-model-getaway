# Reference Overview

This skill uses a split reference layer because general Python async guidance
spans several distinct topics: structured concurrency, cancellation and grouped
failure semantics, and async protocols.

## Reference Files

| File | Role |
| --- | --- |
| `references/structured-concurrency.md` | Sync-versus-async choice, direct `await` versus spawned-task ownership, Python 3.10-compatible structured concurrency, and the supplementary AnyIO note |
| `references/cancellation-and-failure.md` | Cancellation, timeout boundaries, grouped task failure, and preserving semantic async error-family intent |
| `references/async-protocols.md` | `async with`, `async for`, async iterators, async generators, and protocol-boundary warnings |

## Navigation

- Start with `SKILL.md` for the main decision path.
- Use `references/structured-concurrency.md` when the main question is whether
  code should stay synchronous, be directly awaited, or run under an explicit
  concurrent owner.
- Use `references/cancellation-and-failure.md` when cancellation, timeout, or
  grouped task failure is the main review concern.
- Use `references/async-protocols.md` when code needs `async with`, `async for`,
  async iterators, or async generators.
- Use `examples.md` for the multi-path worked examples and anti-patterns.
