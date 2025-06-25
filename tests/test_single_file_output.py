"""Unit tests for the --single-file CLI option (task 8.1).

These tests verify that when the --single-file option is used, all discovered pages (single or recursive)
are concatenated into a single Markdown file with correct page breaks, headings, and ordering.
"""

from pathlib import Path

import pytest
from click.testing import CliRunner

from markdown_maker.main import cli


@pytest.fixture
def dummy_single_page():
    return {
        "title": "Single Page",
        "body": {"storage": {"value": "<h1>Single</h1>"}},
    }


@pytest.fixture
def dummy_recursive_pages():
    return [
        {
            "id": "1",
            "title": "Parent Page",
            "body": {"storage": {"value": "<h1>Parent</h1>"}},
        },
        {
            "id": "2",
            "title": "Child Page",
            "body": {"storage": {"value": "<h2>Child</h2>"}},
        },
    ]


def test_single_file_output_single_page(tmp_path: Path, mocker, dummy_single_page):
    """Test --single-file outputs a single Markdown file for a single page."""
    valid_url = "https://company.atlassian.net/wiki/pages/viewpage.action?pageId=123456789"
    mocker.patch(
        "markdown_maker.clients.confluence_client.ConfluenceClient.get_page_content",
        return_value=dummy_single_page,
    )
    mocker.patch(
        "markdown_maker.converters.html_to_markdown.convert_html_to_markdown",
        return_value="# Single\n",
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
            "--single-file",
        ],
    )
    assert result.exit_code == 0
    # The filename should be sanitized from the page title
    expected_filename = tmp_path / "single_page.md"
    assert expected_filename.exists()
    content = expected_filename.read_text()
    assert "# Single" in content
    assert "Single Page" in content  # Heading or break
    assert f"Source: [{valid_url}]({valid_url})" in content


def test_single_file_output_recursive(tmp_path: Path, mocker, dummy_recursive_pages):
    """Test --single-file outputs a single Markdown file for recursive conversion."""
    valid_url = "https://company.atlassian.net/wiki/pages/viewpage.action?pageId=1"
    # Patch recursive handler to simulate discovered pages in order
    mocker.patch(
        "markdown_maker.main.handle_recursive_conversion",
        return_value=None,
    )
    # Patch ConfluenceClient.get_page_content to return parent/child by id
    def get_page_content_side_effect(page_id):
        for page in dummy_recursive_pages:
            if page["id"] == page_id:
                return page
        raise ValueError("Unknown page_id")

    mocker.patch(
        "markdown_maker.clients.confluence_client.ConfluenceClient.get_page_content",
        side_effect=get_page_content_side_effect,
    )
    mocker.patch(
        "markdown_maker.converters.html_to_markdown.convert_html_to_markdown",
        side_effect=lambda html: html.replace("<h1>", "# ")
        .replace("</h1>", "")
        .replace("<h2>", "## ")
        .replace("</h2>", ""),
    )
    # Patch get_child_pages to simulate parent->child relationship
    def get_child_pages_side_effect(page_id):
        if page_id == "1":
            return [dummy_recursive_pages[1]]
        return []

    mocker.patch(
        "markdown_maker.clients.confluence_client.ConfluenceClient.get_child_pages",
        side_effect=get_child_pages_side_effect,
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
            "--recursive",
            "--single-file",
        ],
    )
    assert result.exit_code == 0
    expected_filename = tmp_path / "parent_page.md"
    assert expected_filename.exists()
    content = expected_filename.read_text()
    # Check both pages' content and headings
    assert "# Parent" in content
    assert "## Child" in content
    assert "Parent Page" in content
    assert "Child Page" in content
    assert f"Source: [{valid_url}]({valid_url})" in content
    assert "pageId=2" in content
    # Check that parent comes before child
    assert content.index("Parent Page") < content.index("Child Page")
    # Check for clear page break (e.g., --- or similar)
    assert "---" in content or "====" in content


def test_single_file_embedded_link_error_context(tmp_path: Path, mocker, dummy_single_page):
    """Test error log for inaccessible embedded link includes the link URL."""
    valid_url = "https://company.atlassian.net/wiki/pages/viewpage.action?pageId=123456789"
    inaccessible_url = "https://company.atlassian.net/wiki/pages/viewpage.action?pageId=99999999"
    # Page contains an embedded link to inaccessible_url
    dummy_page_with_link = {
        "title": "Page With Link",
        "body": {"storage": {"value": f'<a href="{inaccessible_url}">link</a>'}},
    }

    def get_page_content_side_effect(page_id):
        if page_id == "123456789":
            return dummy_page_with_link
        # Simulate an API error for inaccessible page
        from atlassian.errors import ApiError
        raise ApiError("No access")

    mocker.patch(
        "markdown_maker.clients.confluence_client.ConfluenceClient.get_page_content",
        side_effect=get_page_content_side_effect,
    )
    mocker.patch(
        "markdown_maker.converters.html_to_markdown.convert_html_to_markdown",
        return_value="# Page With Link\n",
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
            "--single-file",
        ],
    )
    assert result.exit_code == 0
    # Should mention the embedded link URL in the error output
    assert inaccessible_url in result.output
    assert "embedded link" in result.output or "Could not access" in result.output
