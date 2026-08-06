"""Synchronous response-cache value codec port."""

from __future__ import annotations

from typing import Protocol

__all__ = ["CacheCodec"]


class CacheCodec(Protocol):
    """Encode and decode one response string representation."""

    codec_id: str

    def encode(self, *, value: str) -> bytes:
        """Encode a response value for storage."""
        ...

    def decode(self, *, payload: bytes) -> str:
        """Decode a stored response payload."""
        ...
