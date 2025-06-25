"""Unit tests for the main CLI entry point."""

from pathlib import Path

from click.testing import CliRunner

from markdown_maker.main import cli


def test_convert_command_prints_options(tmp_path: Path, mocker) -> None:
    """Tests that the convert command prints the options it receives."""
    runner = CliRunner()
    valid_url = (
        "https://company.atlassian.net/wiki/pages/viewpage.action?pageId=123456789"
    )
    # Patch ConfluenceClient.get_page_content to avoid real API call
    mocker.patch(
        "markdown_maker.clients.confluence_client.ConfluenceClient.get_page_content",
        return_value={
            "body": {"storage": {"value": "<h1>Test</h1>"}},
            "title": "Test Page",
        },
    )
    mocker.patch(
        "markdown_maker.main.handle_recursive_conversion",
        autospec=True,
    )
    result = runner.invoke(
        cli,
        [
            "convert",
            "--url",
            valid_url,
            "--output-dir",
            str(tmp_path),
            "--recursive",
        ],
    )
    assert result.exit_code == 0
    assert f"URL: {valid_url}" in result.output
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
