"""Tests for the package entrypoint."""

from async_model_gateway import main


def test_main_prints_foundation_scaffold(capsys) -> None:
    """The package entrypoint should keep the scaffold output stable."""
    main()

    captured = capsys.readouterr()

    assert captured.out == "async-model-gateway foundation scaffold\n"
    assert captured.err == ""
