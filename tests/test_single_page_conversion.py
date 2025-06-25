"""Unit tests for single-page conversion logic in the CLI."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from markdown_maker.main import cli


@pytest.fixture
def dummy_page():
    return {
        "title": "My Page Title!",
        "body": {"storage": {"value": "<h1>Header</h1>"}},
    }


def test_convert_command_saves_markdown_file(tmp_path: Path, mocker, dummy_page):
    """Test that the convert command saves Markdown to a file with a sanitized title."""
    valid_url = (
        "https://company.atlassian.net/wiki/pages/viewpage.action?pageId=123456789"
    )
    # Patch ConfluenceClient.get_page_content to return dummy page
    mocker.patch(
        "markdown_maker.clients.confluence_client.ConfluenceClient.get_page_content",
        return_value=dummy_page,
    )
    # Patch convert_html_to_markdown to return predictable markdown
    mocker.patch(
        "markdown_maker.converters.html_to_markdown.convert_html_to_markdown",
        return_value="# Header\n",
    )
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
    # The filename should be sanitized from the page title
    expected_filename = tmp_path / "my_page_title.md"
    assert expected_filename.exists()
    content = expected_filename.read_text().strip()
    assert content == "# Header"
