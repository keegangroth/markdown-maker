"""Test output directory creation in single-page conversion."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from markdown_maker.main import cli


@pytest.fixture
def dummy_page():
    return {
        "title": "Test Page",
        "body": {"storage": {"value": "<h1>Header</h1>"}},
    }


def test_output_dir_created(tmp_path: Path, mocker, dummy_page):
    """Test that the output directory is created if it does not exist."""
    valid_url = "https://company.atlassian.net/wiki/pages/viewpage.action?pageId=123456789"
    mocker.patch(
        "markdown_maker.clients.confluence_client.ConfluenceClient.get_page_content",
        return_value=dummy_page,
    )
    mocker.patch(
        "markdown_maker.converters.html_to_markdown.convert_html_to_markdown",
        return_value="# Header\n",
    )
    runner = CliRunner()
    output_dir = tmp_path / "does_not_exist"
    assert not output_dir.exists()
    result = runner.invoke(
        cli,
        [
            "convert",
            "--url",
            valid_url,
            "--output-dir",
            str(output_dir),
        ],
    )
    assert result.exit_code == 0
    assert output_dir.exists()
    expected_file = output_dir / "test_page.md"
    assert expected_file.exists()
    assert expected_file.read_text().strip() == "# Header"
