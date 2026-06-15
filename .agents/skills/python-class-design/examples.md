# Python class-design examples

Use these examples after `SKILL.md` narrows the task to ordinary behavior-oriented classes.

## Public surface vs internal helpers

### Keep the public surface semantic and small
```py
class BankAccount:
    def __init__(self, account_id: str, opening_balance: int) -> None:
        if opening_balance < 0:
            raise ValueError("opening balance must be non-negative")
        self._account_id = account_id
        self._balance = opening_balance

    @property
    def balance(self) -> int:
        return self._balance

    def deposit(self, amount: int) -> None:
        """Add funds to the account."""
        self._ensure_positive_amount(amount)
        self._balance += amount

    def withdraw(self, amount: int) -> None:
        """Remove funds from the account when funds are available."""
        self._ensure_positive_amount(amount)
        if amount > self._balance:
            raise ValueError("insufficient funds")
        self._balance -= amount

    def _ensure_positive_amount(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("amount must be positive")
```

- `deposit()` and `withdraw()` are the stable public commands.
- Validation helpers stay internal.
- The public property is cheap and read-only.

### Avoid exposing implementation steps as public methods
```py
class BankAccount:
    def validate_amount(self, amount: int) -> None:
        ...

    def apply_delta(self, amount: int) -> None:
        ...

    def check_overdraft(self, amount: int) -> None:
        ...
```

- Public methods should not read like a bag of internal steps.
- Keep the public surface focused on caller intent, not implementation choreography.

## Thin `__init__` and named factories

### Use a factory when creation needs translation or named intent
```py
from datetime import datetime, timezone


class Session:
    def __init__(self, user_id: str, expires_at: datetime) -> None:
        if expires_at.tzinfo is None:
            raise ValueError("expires_at must be timezone-aware")
        self._user_id = user_id
        self._expires_at = expires_at

    @classmethod
    def from_api_payload(cls, payload: dict[str, str]) -> "Session":
        expires_at = datetime.fromisoformat(payload["expires_at"])
        return cls(
            user_id=payload["user_id"],
            expires_at=expires_at.astimezone(timezone.utc),
        )
```

- Parsing and normalization happen in `from_api_payload()`.
- `__init__` stays narrow and receives already-normalized values.
- The factory name explains the creation path.

### Avoid stretching `__init__` into a parser
```py
from datetime import datetime, timezone


class Session:
    def __init__(self, payload: dict[str, str]) -> None:
        raw_expires_at = payload["expires_at"]
        parsed = datetime.fromisoformat(raw_expires_at)
        expires_at = parsed.astimezone(timezone.utc)
        if expires_at.tzinfo is None:
            raise ValueError("expires_at must be timezone-aware")
        self._user_id = payload["user_id"]
        self._expires_at = expires_at
```

- The constructor now mixes parsing, translation, validation, and assignment.
- Callers lose a clean typed constructor shape.

## Properties and setters

### Use properties sparingly for read-only or cheap derived access
```py
class Invoice:
    def __init__(self, subtotal: int, tax: int) -> None:
        self._subtotal = subtotal
        self._tax = tax

    @property
    def total(self) -> int:
        return self._subtotal + self._tax
```

- `total` is a cheap derived view.
- The property does not hide expensive work or state mutation.

### Prefer semantic methods over open-ended setters
```py
class Thermostat:
    def __init__(self, target_celsius: int) -> None:
        self._target_celsius = target_celsius

    @property
    def target_celsius(self) -> int:
        return self._target_celsius

    def set_target(self, value: int) -> None:
        if value < 10 or value > 30:
            raise ValueError("target out of range")
        self._target_celsius = value
```

- A semantic write path makes validation and future rules easier to keep coherent.
- The method name tells reviewers that this is state-changing behavior.

### Avoid using `@property.setter` as the default write path
```py
class Thermostat:
    def __init__(self, target_celsius: int) -> None:
        self._target_celsius = target_celsius

    @property
    def target_celsius(self) -> int:
        return self._target_celsius

    @target_celsius.setter
    def target_celsius(self, value: int) -> None:
        if value < 10 or value > 30:
            raise ValueError("target out of range")
        self._target_celsius = value
```

- This style can make meaningful state transitions look like plain field assignment.
- Use it only for narrow compatibility or very simple delegation cases.

## Attribute lifecycle

### Define object shape up front
```py
class Job:
    def __init__(self, job_id: str, status: str) -> None:
        self._job_id = job_id
        self._status = status
        self._result: str | None = None
```

- The expected instance shape is visible at construction time.
- Optional later values can still be represented explicitly.

### Allow delayed attributes only for explicit lazy cache cases
```py
class Report:
    def __init__(self, rows: list[int]) -> None:
        self._rows = rows
        self._average_cache: float | None = None

    @property
    def average(self) -> float:
        if self._average_cache is None:
            self._average_cache = sum(self._rows) / len(self._rows)
        return self._average_cache
```

- The lazy path is explicit and local.
- The delayed value is still declared in `__init__`.

### Avoid ad hoc dynamic attributes
```py
class Job:
    def __init__(self, job_id: str) -> None:
        self._job_id = job_id

    def attach_result(self, result: str) -> None:
        self._result = result

    def mark_failed(self, reason: str) -> None:
        self._failure_reason = reason
```

- The instance shape now depends on which methods were called.
- This makes the object harder to reason about, type, test, and review.

## Single underscore vs double underscore

### Default to `_single_leading_underscore`
```py
class TokenCache:
    def __init__(self) -> None:
        self._token_by_key: dict[str, str] = {}

    def _normalize_key(self, key: str) -> str:
        return key.strip().lower()
```

- This is the normal Python signal for internal implementation details.
- It stays friendly to testing, debugging, and ordinary maintenance.

### Use `__double_leading_underscore` only for real collision avoidance
```py
class BaseParser:
    def __init__(self) -> None:
        self.__state = "ready"


class CustomParser(BaseParser):
    def __init__(self) -> None:
        super().__init__()
        self.__state = "custom"
```

- Name mangling can protect a base-class internal slot from accidental subclass collision.
- This is a narrow inheritance-focused exception, not the default privacy tool.

### Avoid fake hard privacy
```py
class TokenCache:
    def __init__(self) -> None:
        self.__token_by_key: dict[str, str] = {}

    def __normalize_key(self, key: str) -> str:
        return key.strip().lower()
```

- Using `__double_leading_underscore` everywhere increases friction without adding much value.
- It is not a substitute for good class boundaries.

## Class attributes and shared state

### Keep constants and metadata on the class
```py
class RetryPolicy:
    DEFAULT_TIMEOUT = 30
    MAX_ATTEMPTS = 5

    def __init__(self, timeout: int | None = None) -> None:
        self._timeout = timeout if timeout is not None else self.DEFAULT_TIMEOUT
```

- Class attributes work well for stable constants and metadata.
- Per-instance state still lives on the instance.

### Avoid mutable shared class state for ordinary object data
```py
class ShoppingCart:
    _items: list[str] = []

    def add_item(self, item: str) -> None:
        self._items.append(item)
```

- Every instance now shares the same list.
- This is usually surprising and unsafe for ordinary class state.

## Method ordering is guidance, not a gate

### A readable default order
```py
class EmailDraft:
    DEFAULT_SUBJECT = "Hello"

    def __init__(self, recipient: str, subject: str | None = None) -> None:
        self._recipient = recipient
        self._subject = subject or self.DEFAULT_SUBJECT

    @classmethod
    def create_welcome(cls, recipient: str) -> "EmailDraft":
        return cls(recipient=recipient, subject="Welcome")

    @property
    def subject(self) -> str:
        return self._subject

    def rename_subject(self, subject: str) -> None:
        self._subject = self._normalize_subject(subject)

    def _normalize_subject(self, subject: str) -> str:
        return subject.strip()
```

- Constants first, then construction, then properties, then public methods, then helpers.
- This is a readability aid, not a hard acceptance criterion.

## Split signals

Stop and hand off to another skill when the main question becomes:

- whether the type should be a `dataclass`, `Enum`, `ABC`, or `Protocol`
- naming consistency or visibility naming conventions across modules
- strict typing rules for cached attributes, factories, or protocols
- DDD entity/value-object boundaries or framework-specific base classes
