# Logging and observability best practices

## Level discipline

| Level | Use when |
|---|---|
| `DEBUG` | Detailed diagnostic info useful only during development or debugging; never needed by operators in production |
| `INFO` | Routine lifecycle events operators may want to audit (user created, job started, request processed) |
| `WARNING` | Something unexpected happened but the system recovered; deserves attention |
| `ERROR` | An operation failed; the system cannot recover from this specific call; action may be required |
| `CRITICAL` | System-level failure; application may not be able to continue |

## Structured logging

Prefer `logger.info("message", extra={"key": value})` over formatted string interpolation.
Structured logs are machine-parseable and support log aggregation tools.

```python
# Preferred
logger.info("Payment processed", extra={"order_id": order_id, "amount": amount})

# Avoid
logger.info(f"Payment processed for order {order_id} amount {amount}")
```

## What to flag

| Issue | Severity |
|---|---|
| `print()` used where structured logging is expected | `warning` |
| `logging.debug()` used for information operators need in production | `warning` |
| Sensitive data (passwords, tokens, PII) logged at any level | `blocking` |
| Exception caught and silently swallowed with no log | `blocking` |
| Log message with no context for dynamic state | `info` |
| Log message uses f-string interpolation instead of `extra={}` in a structured-logging project | `info` |
