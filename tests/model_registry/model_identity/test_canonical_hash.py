"""RED coverage for complete model-identity hashing."""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from hashlib import sha256
import inspect
from typing import get_type_hints

import pytest
from async_model_gateway.model_registry.entry import ModelSourceKind, RegistryEntry
import async_model_gateway.model_registry.model_identity as model_identity_module
from async_model_gateway.model_registry.model_identity import ModelIdentityHasher


def _expected_digest(
    *,
    model_name: str,
    model_source_kind: ModelSourceKind,
    model_payload_hash: str,
) -> str:
    """Construct the independently specified literal framed digest."""
    frames = (
        ("model_name", model_name),
        ("model_source_kind", model_source_kind.value),
        ("model_payload_hash", model_payload_hash),
    )
    material = b"".join(
        label.encode("ascii")
        + b"\0"
        + len(value.encode("utf-8")).to_bytes(8, "big")
        + value.encode("utf-8")
        for label, value in frames
    )
    return sha256(material).hexdigest()


def test_model_identity_hasher_is_exposed_only_from_its_submodule() -> None:
    """The class-first identity owner belongs to the identity package surface."""
    assert model_identity_module.__all__ == ["ModelIdentityHasher"]
    assert model_identity_module.ModelIdentityHasher is ModelIdentityHasher


def test_model_identity_hasher_has_the_locked_static_keyword_only_api() -> None:
    """The new public hasher API remains stateless and explicitly keyword-only."""
    signature = inspect.signature(ModelIdentityHasher.hash_model_identity)

    assert isinstance(ModelIdentityHasher.__dict__["hash_model_identity"], staticmethod)
    assert tuple(signature.parameters) == (
        "model_name",
        "model_source_kind",
        "model_payload_hash",
    )
    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY
        for parameter in signature.parameters.values()
    )
    assert get_type_hints(ModelIdentityHasher.hash_model_identity)["return"] is str


def test_model_identity_hasher_matches_locked_golden_digest() -> None:
    """The locked three-field model identity must stay cross-process stable."""
    digest = ModelIdentityHasher.hash_model_identity(
        model_name="demo",
        model_source_kind=ModelSourceKind.LOCAL,
        model_payload_hash="a" * 64,
    )

    assert digest == "177653000e2e441856c1d22e3b2b0d02a1ba7c384f1029fb5b5c3464663b72b4"


def test_model_identity_hasher_uses_literal_utf8_length_framing() -> None:
    """Labels, UTF-8 byte lengths, and values are all digest-significant."""
    model_name = "café"
    model_payload_hash = "payload\0with-separator"

    digest = ModelIdentityHasher.hash_model_identity(
        model_name=model_name,
        model_source_kind=ModelSourceKind.REMOTE,
        model_payload_hash=model_payload_hash,
    )

    assert digest == _expected_digest(
        model_name=model_name,
        model_source_kind=ModelSourceKind.REMOTE,
        model_payload_hash=model_payload_hash,
    )


def test_model_identity_hasher_does_not_normalize_unicode() -> None:
    """Unicode-equivalent values with distinct literal bytes remain distinct."""
    composed = ModelIdentityHasher.hash_model_identity(
        model_name="café",
        model_source_kind=ModelSourceKind.LOCAL,
        model_payload_hash="a" * 64,
    )
    decomposed = ModelIdentityHasher.hash_model_identity(
        model_name="cafe\u0301",
        model_source_kind=ModelSourceKind.LOCAL,
        model_payload_hash="a" * 64,
    )

    assert composed != decomposed


@pytest.mark.parametrize(
    ("model_name", "model_source_kind", "model_payload_hash"),
    [
        ("other", ModelSourceKind.LOCAL, "a" * 64),
        ("demo", ModelSourceKind.REMOTE, "a" * 64),
        ("demo", ModelSourceKind.LOCAL, "b" * 64),
    ],
)
def test_model_identity_hasher_changes_when_any_identity_field_changes(
    model_name: str,
    model_source_kind: ModelSourceKind,
    model_payload_hash: str,
) -> None:
    """Every identity field contributes to the digest."""
    baseline = ModelIdentityHasher.hash_model_identity(
        model_name="demo",
        model_source_kind=ModelSourceKind.LOCAL,
        model_payload_hash="a" * 64,
    )

    digest = ModelIdentityHasher.hash_model_identity(
        model_name=model_name,
        model_source_kind=model_source_kind,
        model_payload_hash=model_payload_hash,
    )

    assert digest != baseline


@pytest.mark.parametrize(
    ("model_name", "model_source_kind", "model_payload_hash", "error_type"),
    [
        (None, ModelSourceKind.LOCAL, "a" * 64, TypeError),
        ("", ModelSourceKind.LOCAL, "a" * 64, ValueError),
        ("demo", ModelSourceKind.LOCAL, None, TypeError),
        ("demo", ModelSourceKind.LOCAL, "", ValueError),
        ("demo", "local", "a" * 64, TypeError),
        ("demo", object(), "a" * 64, TypeError),
    ],
)
def test_model_identity_hasher_rejects_invalid_material_without_coercion(
    model_name: object,
    model_source_kind: object,
    model_payload_hash: object,
    error_type: type[Exception],
) -> None:
    """Only explicitly valid identity material may cross the public boundary."""
    with pytest.raises(error_type):
        ModelIdentityHasher.hash_model_identity(
            model_name=model_name,  # type: ignore[arg-type]
            model_source_kind=model_source_kind,  # type: ignore[arg-type]
            model_payload_hash=model_payload_hash,  # type: ignore[arg-type]
        )


def test_registry_entry_identity_hash_is_derived_read_only_and_not_state() -> None:
    """The entry exposes a calculated property without widening dataclass state."""
    entry = RegistryEntry(
        model_name="demo",
        model_source_kind=ModelSourceKind.LOCAL,
        payload_hash="a" * 64,
    )

    assert is_dataclass(RegistryEntry)
    assert [field.name for field in fields(RegistryEntry)] == [
        "model_name",
        "model_source_kind",
        "payload_hash",
    ]
    assert list(inspect.signature(RegistryEntry).parameters) == [
        "model_name",
        "model_source_kind",
        "payload_hash",
    ]
    assert entry.model_identity_hash == (
        "177653000e2e441856c1d22e3b2b0d02a1ba7c384f1029fb5b5c3464663b72b4"
    )

    with pytest.raises((AttributeError, TypeError)):
        entry.model_identity_hash = "replacement"  # type: ignore[misc]


def test_registry_entry_identity_hash_is_recomputed_per_access(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Each property read uses the stateless hasher rather than stored state."""
    observed_calls: list[tuple[str, ModelSourceKind, str]] = []

    def fake_hash_model_identity(
        *,
        model_name: str,
        model_source_kind: ModelSourceKind,
        model_payload_hash: str,
    ) -> str:
        observed_calls.append((model_name, model_source_kind, model_payload_hash))
        return "identity"

    monkeypatch.setattr(
        ModelIdentityHasher,
        "hash_model_identity",
        staticmethod(fake_hash_model_identity),
    )
    entry = RegistryEntry(
        model_name="demo",
        model_source_kind=ModelSourceKind.REMOTE,
        payload_hash="a" * 64,
    )

    assert entry.model_identity_hash == "identity"
    assert entry.model_identity_hash == "identity"
    assert observed_calls == [
        ("demo", ModelSourceKind.REMOTE, "a" * 64),
        ("demo", ModelSourceKind.REMOTE, "a" * 64),
    ]
