"""Minimal model-artifact package boundary."""

from .artifact import ModelArtifact
from .loader_family import LoaderFamily

__all__ = ["LoaderFamily", "ModelArtifact"]
