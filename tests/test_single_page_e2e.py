"""End-to-end test for single-page conversion CLI flow."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from markdown_maker.main import cli


@pytest.fixture
def dummy_page():
    return {
        "title": "End-to-End Test Page",
        "body": {"storage": {"value": "<h1>End-to-End Header</h1>"}},
    }


def test_single_page_e2e(tmp_path: Path, mocker, dummy_page):
    """End-to-end: CLI fetches, converts, and writes markdown for a single page."""
    valid_url = "https://company.atlassian.net/wiki/pages/viewpage.action?pageId=123456789"
    mocker.patch(
        "markdown_maker.clients.confluence_client.ConfluenceClient.get_page_content",
        return_value=dummy_page,
    )
    mocker.patch(
        "markdown_maker.converters.html_to_markdown.convert_html_to_markdown",
        return_value="# End-to-End Header\n",
    )
    runner = CliRunner()
    output_dir = tmp_path / "e2e_output"
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
    expected_file = output_dir / "end_to_end_test_page.md"
    assert expected_file.exists()
    content = expected_file.read_text().strip()
    assert content == "# End-to-End Header"
    assert f"Saved: {expected_file}" in result.output
