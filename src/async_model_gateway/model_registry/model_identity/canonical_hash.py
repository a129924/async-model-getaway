"""Canonical hashing for complete model-identity material."""

from __future__ import annotations

from hashlib import sha256

from ..entry import ModelSourceKind

__all__ = ["ModelIdentityHasher"]


class ModelIdentityHasher:
    """Hash complete model identity through a stateless class-first owner."""

    @staticmethod
    def hash_model_identity(
        *,
        model_name: str,
        model_source_kind: ModelSourceKind,
        model_payload_hash: str,
    ) -> str:
        """Return the locked framed SHA-256 identity digest."""
        ModelIdentityHasher._validate_non_empty_string(
            value=model_name,
            field_name="model_name",
        )
        ModelIdentityHasher._validate_model_source_kind(model_source_kind)
        ModelIdentityHasher._validate_non_empty_string(
            value=model_payload_hash,
            field_name="model_payload_hash",
        )

        material = b"".join(
            ModelIdentityHasher._frame(label=label, value=value)
            for label, value in (
                ("model_name", model_name),
                ("model_source_kind", model_source_kind.value),
                ("model_payload_hash", model_payload_hash),
            )
        )
        return sha256(material).hexdigest()

    @staticmethod
    def _validate_non_empty_string(*, value: object, field_name: str) -> None:
        """Reject invalid string identity material without coercion."""
        if not isinstance(value, str):
            msg = f"{field_name} must be a str"
            raise TypeError(msg)
        if not value:
            msg = f"{field_name} must not be empty"
            raise ValueError(msg)

    @staticmethod
    def _validate_model_source_kind(value: object) -> None:
        """Reject source kinds outside the existing closed registry vocabulary."""
        if value is not ModelSourceKind.LOCAL and value is not ModelSourceKind.REMOTE:
            msg = "model_source_kind must be ModelSourceKind.LOCAL or ModelSourceKind.REMOTE"
            raise TypeError(msg)

    @staticmethod
    def _frame(*, label: str, value: str) -> bytes:
        """Encode one literal label/value frame using UTF-8 byte length."""
        value_bytes = value.encode("utf-8")
        return (
            label.encode("ascii")
            + b"\0"
            + len(value_bytes).to_bytes(8, byteorder="big")
            + value_bytes
        )
