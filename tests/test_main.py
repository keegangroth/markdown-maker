"""Unit tests for the main CLI entry point."""

from pathlib import Path

from click.testing import CliRunner

from markdown_maker.main import cli


def test_convert_command_prints_options(tmp_path: Path) -> None:
    """Tests that the convert command prints the options it receives."""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "convert",
            "--url",
            "http://example.com",
            "--output-dir",
            str(tmp_path),
            "--recursive",
        ],
    )

    assert result.exit_code == 0
    assert "URL: http://example.com" in result.output
    assert f"Output Directory: {tmp_path}" in result.output
    assert "Recursive: True" in result.output


def test_cli_help_menu() -> None:
    """Tests that the main --help menu displays correctly."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Usage: cli [OPTIONS] COMMAND [ARGS]..." in result.output
    assert "A CLI tool to convert Confluence pages to Markdown." in result.output
    assert "convert" in result.output


def test_convert_help_menu() -> None:
    """Tests that the convert --help menu displays correctly."""
    runner = CliRunner()
    result = runner.invoke(cli, ["convert", "--help"])
    assert result.exit_code == 0
    assert "Usage: cli convert [OPTIONS]" in result.output
    assert "Converts a Confluence page to a Markdown file." in result.output
    assert "--url" in result.output
    assert "--output-dir" in result.output
    assert "--recursive" in result.output
