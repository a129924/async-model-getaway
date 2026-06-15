# Pytest unit-testing examples

Use these examples after `SKILL.md` narrows the task to pure unit tests, using mocks when needed.

## Inline arrange vs fixtures

### Prefer inline arrange
```py
def test_normalize_name_trims_whitespace() -> None:
    result = normalize_name("  Alice  ")
    assert result == "Alice"
```

- Inline arrange is the default when setup is short and local to one test.
- Keep the whole behavior readable without hopping through fixtures.

### Extract a fixture only when it removes real duplication
```py
import pytest

@pytest.fixture
def default_user() -> User:
    return User(name="Alice", is_active=True)

def test_deactivate_user_marks_user_inactive(default_user: User) -> None:
    deactivate_user(default_user)
    assert default_user.is_active is False
```

- Extract fixtures for shared preconditions or clear noise reduction.
- Do not move every arrange step into fixtures out of habit.

## Parametrization

### Use `pytest.mark.parametrize` for data-only variation
```py
import pytest

@pytest.mark.parametrize(
    ("raw", "expected"),
    [("  Alice  ", "Alice"), ("\tBob", "Bob"), ("Carol", "Carol")],
)
def test_normalize_name(raw: str, expected: str) -> None:
    assert normalize_name(raw) == expected
```

- Use it when one behavior stays the same and only the input or expected output changes.

### Split into separate tests when arrangement or narrative changes
```py
from unittest.mock import Mock
import pytest

@pytest.mark.parametrize("channel", ["email", "sms"])
def test_publish_alert(channel: str) -> None:
    sender = Mock()
    service = AlertPublisher(sender=sender)

    if channel == "email":
        service.publish_email("hello")
    else:
        service.publish_sms("hello")

    sender.send.assert_called_once()
```

- The test-side `if/else` is a split signal.
- Different patching, mock setup, or failure story should become separate tests.

## State assertions vs interaction assertions

### Prefer state or output assertions
```py
def test_choose_timeout_uses_default_when_none() -> None:
    assert choose_timeout(None) == 30
```

- Prefer validating the returned value or resulting state first.
- These tests usually survive refactors better than wiring-focused assertions.

### Use mock call assertions only for real side effects
```py
from unittest.mock import Mock

def test_register_user_sends_welcome_email() -> None:
    notifier = Mock()
    service = RegistrationService(notifier=notifier)

    service.register("alice@example.com")

    notifier.send_welcome.assert_called_once_with("alice@example.com")
```

- Use interaction assertions when the side effect itself is the contract.
- Do not assert every collaborator call if the behavior is already visible through state or output.

## Mocking baseline

### Prefer stdlib `unittest.mock`
```py
from unittest.mock import Mock

def test_retry_once_on_transient_error() -> None:
    client = Mock()
    client.fetch.side_effect = [TimeoutError(), "ok"]

    result = fetch_with_retry(client)

    assert result == "ok"
    assert client.fetch.call_count == 2
```

- Use `Mock`, `patch`, or `patch.object` from stdlib as the default baseline.
- Keep the mocking rule portable and independent of extra pytest plugins.

### `monkeypatch` is supplementary
```py
import pytest

def test_load_mode_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_MODE", "test")
    assert load_mode() == "test"
```

- `monkeypatch` is fine for small environment or attribute overrides.
- Keep it as examples-level detail, not the primary mocking contract of the skill.

## Coverage note

- Aim to cover the core decision branches of the unit under test.
- Treat 85%+ as a recommended quality baseline, not a hard gate inside this skill.
- Do not add shallow tests just to move the number.

## Do not trigger

These cases are outside this skill's first draft:

- tests that hit a real database
- tests that read or write the real filesystem
- tests that call a real network or external service
- browser, e2e, load, or full integration tests
- framework-specific test clients or app factories

## Split signals

Stop and hand off to another skill when the main question becomes:

- integration-test structure instead of pure unit testing
- framework-specific testing helpers
- CI, coverage tooling, or test-runner policy
- advanced plugin ecosystems rather than everyday pytest unit-testing rules
