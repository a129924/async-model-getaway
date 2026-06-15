# python-code-review examples

Full worked examples for all branching paths described in `SKILL.md`.

---

## Example 1 — Approved: clean implementation

### Context

`pyproject.toml` contains `[tool.ruff]` and `[tool.pyright]` with `strict = false`.
No `Makefile`. Implementation file: `src/users/service.py`. Test file: `tests/test_service.py`.

### Code under review

```python
# src/users/service.py
from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

WELCOME_EMAIL_SUBJECT = "Welcome!"


@dataclass
class User:
    name: str
    email: str
    is_active: bool = True


class UserService:
    def __init__(self, repo: UserRepository, notifier: Notifier) -> None:
        self._repo = repo
        self._notifier = notifier

    def create_user(self, name: str, email: str) -> User:
        """Create a new active user and send a welcome notification."""
        user = User(name=name, email=email)
        self._repo.save(user)
        logger.info("User created", extra={"email": email})
        try:
            self._notifier.send_welcome(email, subject=WELCOME_EMAIL_SUBJECT)
        except NotificationError as exc:
            logger.warning("Welcome notification failed", extra={"email": email, "error": str(exc)})
        return user
```

```python
# tests/test_service.py
from unittest.mock import Mock

from users.service import User, UserService


def test_create_user_returns_active_user() -> None:
    repo = Mock()
    notifier = Mock()
    service = UserService(repo=repo, notifier=notifier)

    result = service.create_user(name="Alice", email="alice@example.com")

    assert result == User(name="Alice", email="alice@example.com", is_active=True)
    repo.save.assert_called_once_with(result)


def test_create_user_logs_warning_when_notification_fails() -> None:
    repo = Mock()
    notifier = Mock()
    notifier.send_welcome.side_effect = NotificationError("SMTP timeout")
    service = UserService(repo=repo, notifier=notifier)

    result = service.create_user(name="Bob", email="bob@example.com")

    assert result.name == "Bob"
```

### Output

```
verdict: approved
tooling_detected: pyproject.toml → [tool.ruff], [tool.pyright] (strict = false)

findings:
  typing: []
  lint: []
  readability: []
  error_handling: []
  anti_patterns: []
  test_quality: []
  observability: []
```

---

## Example 2 — needs-rework: bare except

### Context

No `pyproject.toml`, no `Makefile`. Fallback to generic best-practice judgment.

### Code under review

```python
# processor.py
def process_record(record):
    try:
        result = transform(record)
        save(result)
    except:
        pass
```

### Output

```
verdict: needs-rework
tooling_detected: generic fallback (no pyproject.toml or Makefile found)

findings:
  typing:
    - severity: warning
      location: processor.py:2
      issue: "Missing type annotations on public function process_record (parameter 'record', return type)"
      fix: "Add annotations, e.g. def process_record(record: Record) -> None:"
  lint: []
  readability: []
  error_handling:
    - severity: blocking
      location: processor.py:3
      issue: "Bare except: catches all exceptions including KeyboardInterrupt and SystemExit"
      fix: "Replace with a specific exception type (e.g. except TransformError as exc:) and either log the error or re-raise"
  anti_patterns:
    - severity: blocking
      location: processor.py:4
      issue: "Bare pass in except handler silently swallows the error with no log and no re-raise"
      fix: "Add logger.error('Failed to process record', exc_info=True) or re-raise the exception"
  test_quality: []
  observability:
    - severity: blocking
      location: processor.py:4
      issue: "Exception caught and silently swallowed — operators have no visibility into failures"
      fix: "Log the exception at WARNING or ERROR level before suppressing, or propagate it"
```

---

## Example 3 — needs-rework: missing type hints in strict-mode project

### Context

`pyproject.toml` contains:

```toml
[tool.pyright]
strict = true
```

### Code under review

```python
# pipeline.py
def process(data):
    return [item for item in data if item is not None]
```

### Output

```
verdict: needs-rework
tooling_detected: pyproject.toml → [tool.pyright] (strict = true)

findings:
  typing:
    - severity: blocking
      location: pipeline.py:2
      issue: "Missing type annotations on public function process — project uses pyright strict mode"
      fix: "Add explicit parameter and return annotations, e.g. def process(data: Iterable[T | None]) -> list[T]:"
    - severity: blocking
      location: pipeline.py:2
      issue: "Return type is implicitly Any — strict mode disallows implicit Any"
      fix: "Annotate the return type explicitly"
  lint: []
  readability: []
  error_handling: []
  anti_patterns: []
  test_quality: []
  observability: []
```

---

## Example 4 — needs-rework: mutable default argument

### Context

`pyproject.toml` contains `[tool.ruff]`. No pyright or mypy section.

### Code under review

```python
# cart.py
def add_item(items=[], label="item"):
    items.append(label)
    return items
```

### Output

```
verdict: needs-rework
tooling_detected: pyproject.toml → [tool.ruff]

findings:
  typing:
    - severity: warning
      location: cart.py:2
      issue: "Missing type annotations on public function add_item"
      fix: "Add annotations: def add_item(items: list[str] | None = None, label: str = 'item') -> list[str]:"
  lint: []
  readability: []
  error_handling: []
  anti_patterns:
    - severity: blocking
      location: cart.py:2
      issue: "Mutable default argument: items=[] is a single list object shared across all calls"
      fix: "Use None as sentinel and initialize inside the function body:\n  def add_item(items: list[str] | None = None, label: str = 'item') -> list[str]:\n      if items is None:\n          items = []\n      items.append(label)\n      return items"
  test_quality: []
  observability: []
```

---

## Example 5 — Tooling fallback

### Context

The repository has no `pyproject.toml`, no `Makefile`, no `README.md`, and no `CONTRIBUTING.md`.
The skill falls back to generic Python best-practice judgment.

### Code under review

```python
# helpers.py
def format_name(first, last):
    return first + " " + last
```

### Output

```
verdict: approved
tooling_detected: generic fallback (no pyproject.toml or Makefile found)

findings:
  typing:
    - severity: warning
      location: helpers.py:2
      issue: "Missing type annotations on public function format_name"
      fix: "Add annotations: def format_name(first: str, last: str) -> str:"
  lint: []
  readability: []
  error_handling: []
  anti_patterns: []
  test_quality: []
  observability: []
```

> **Note**: Generic fallback does not fail the review. Severity levels follow standard
> Python best-practice defaults: missing annotations on public functions are `warning`,
> not `blocking`, unless the project has strict mode enabled.

---

## Example 6 — Sequencing gate refusal

### Context

The user asks for a code-quality review, but there is no record or confirmation that
`python-implementation-review` has already run on this implementation.

### User request

> "Please review the code quality of my new authentication module."

### Output

```
Sequencing gate triggered: python-implementation-review must approve the implementation
before python-code-review runs.

Action required: Run python-implementation-review on this implementation first.
Once it returns approved, return here for the code-quality review.

python-code-review has not started.
```

### Why

`python-code-review` only judges code quality. Reviewing quality on an implementation
that hasn't been verified against the plan risks approving good-quality code that
implements the wrong thing. The sequencing gate prevents this false confidence.

---

## Anti-pattern quick-reference

| Anti-pattern | Severity | Acceptable when |
|---|---|---|
| `except:` bare | blocking | Never |
| `except Exception:` with `pass` | blocking | Never |
| Mutable default `def f(x=[])` | blocking | Never |
| `eval()` / `exec()` | blocking | Only with explicit sandboxing comment |
| Implicit `Optional` `def f(x: str = None)` | blocking | Never |
| `__getattr__` for general routing | blocking | Only as proxy/adapter (see `python-descriptors-attribute-access`) |
| `# type: ignore` without comment | warning | Only when unavoidable and explained inline |
| `Any` in strict-mode project | blocking | Only with explicit justification comment |
| `Any` in non-strict project | warning | When type is genuinely dynamic |
| Bare `pass` in except | blocking | Never (use `...` with a comment at minimum) |
| Nested comprehension >2 levels | warning | When clarity is preserved and performance demands it |
| Function >50 lines | warning | When further split would harm cohesion |
