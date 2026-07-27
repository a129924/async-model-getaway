# ONNX minimal executor invocation boundary specification

## Contract

1. `OnnxRuntimeSession` is an internal Protocol with `get_providers()` and fixed
   `run(None, dict[str, object], None) -> list[object]` capability; no package
   re-export exists.
2. `_OnnxModelExecutor` is private and implements
   `ModelExecutor[OnnxRuntimeSession, dict[str, object], list[object]]`.
3. Invocation validation rejects a non-dict or a dict with non-string keys before
   calling `run`; valid values pass through unchanged.
4. The executor offloads only the synchronous `run` call with direct
   `await asyncio.to_thread(...)`. It creates no task, shield, join, timeout,
   retry, cancellation handler, or exception translation.
5. Loader, binding and composition preserve the exact generic chain without
   `RuntimeBinding[object, object, object]` or new typing escape hatches.
6. The only provider import/typing boundary remains in `_onnx_model_loader.py`;
   no other touched source or test path introduces `Any`, `cast`, inline
   suppression, dynamic import or monkeypatch.

## Acceptance scenarios

### Valid invocation

A fake session records exactly `(None, invocation, None)` and returns a sentinel
`list[object]`; the executor returns that same list identity.

### Invalid invocation

An `object()` input or `{1: object()}` raises `TypeError`, makes no provider call,
and leaves the generic execution gate released.

### Failure and cancellation

A provider `RuntimeError` and caller `CancelledError` preserve identity. Cancellation
is direct: no executor-owned task or delayed worker-drain behavior is introduced.

### Integration and surface

The committed CPU-only identity fixture executes through the private executor.
Package initializers continue to expose no executor/session type; strict witnesses
prove the exact type chain and absence of outer erasure.
