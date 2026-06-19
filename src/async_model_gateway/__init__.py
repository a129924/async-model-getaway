"""Foundation package for the async-model-gateway project."""

from .__version__ import __version__

__all__ = ["__version__", "main"]


def main() -> None:
    """Run the minimal bootstrap entrypoint for the project scaffold."""
    print("async-model-gateway foundation scaffold")
