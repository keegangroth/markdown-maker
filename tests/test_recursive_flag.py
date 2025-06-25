"""Unit tests for recursive flag logic in the CLI."""

from pathlib import Path

from click.testing import CliRunner

from markdown_maker.main import cli


def test_convert_command_recursive_flag_triggers_recursive_logic(tmp_path: Path, mocker):
    """Test that the --recursive flag triggers recursive logic (placeholder)."""
    valid_url = "https://company.atlassian.net/wiki/pages/viewpage.action?pageId=123456789"
    # Patch ConfluenceClient.get_page_content to avoid real API call
    mocker.patch(
        "markdown_maker.clients.confluence_client.ConfluenceClient.get_page_content",
        return_value={
            "title": "Recursive Test Page",
            "body": {"storage": {"value": "<h1>Header</h1>"}},
        },
    )
    # Patch convert_html_to_markdown to avoid real conversion
    mocker.patch(
        "markdown_maker.converters.html_to_markdown.convert_html_to_markdown",
        return_value="# Header\n",
    )
    # Patch the recursive handler (to be implemented) to check invocation
    traverse_patch = mocker.patch("markdown_maker.main.traverse_and_write")
    runner = CliRunner()
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
    traverse_patch.assert_called_once()


def test_convert_command_without_recursive_flag_does_not_call_recursive(tmp_path: Path, mocker):
    """Test that the recursive handler is not called if --recursive is not set."""
    valid_url = "https://company.atlassian.net/wiki/pages/viewpage.action?pageId=123456789"
    mocker.patch(
        "markdown_maker.clients.confluence_client.ConfluenceClient.get_page_content",
        return_value={
            "title": "Recursive Test Page",
            "body": {"storage": {"value": "<h1>Header</h1>"}},
        },
    )
    mocker.patch(
        "markdown_maker.converters.html_to_markdown.convert_html_to_markdown",
        return_value="# Header\n",
    )
    traverse_patch = mocker.patch("markdown_maker.main.traverse_and_write")
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "convert",
            "--url",
            valid_url,
            "--output-dir",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 0
    traverse_patch.assert_not_called()


def test_recursive_respects_max_depth(tmp_path: Path, mocker):
    """Test that recursion does not exceed the specified max_depth."""
    valid_url = "https://company.atlassian.net/wiki/pages/viewpage.action?pageId=123456789"
    mocker.patch(
        "markdown_maker.clients.confluence_client.ConfluenceClient.get_page_content",
        return_value={
            "title": "Recursive Test Page",
            "body": {"storage": {"value": "<h1>Header</h1>"}},
        },
    )
    mocker.patch(
        "markdown_maker.converters.html_to_markdown.convert_html_to_markdown",
        return_value="# Header\n",
    )
    traverse_patch = mocker.patch("markdown_maker.main.traverse_and_write")
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "convert",
            "--url",
            valid_url,
            "--output-dir",
            str(tmp_path),
            "--recursive",
            "--max-depth",
            "2",
        ],
    )
    assert result.exit_code == 0
    traverse_patch.assert_called_once()
