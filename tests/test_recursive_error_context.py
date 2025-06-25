"""Unit tests for error context in recursive conversion error handling."""

from atlassian.errors import ApiError
from click.testing import CliRunner

from markdown_maker.main import cli


def test_error_context_for_child_page(mocker, tmp_path):
    """Test that error message for child page fetch failure is logged and
    parent is still converted.
    """
    parent_id = "42"
    child_id = "1234"
    parent_title = "Parent Page"
    child_title = "Child One"
    valid_url = (
        f"https://company.atlassian.net/wiki/pages/viewpage.action?pageId={parent_id}"
    )
    parent_page = {
        "title": parent_title,
        "body": {"storage": {"value": "<h1>Parent</h1>"}},
    }

    def get_page_content_side_effect(page_id):
        if page_id == parent_id:
            return parent_page
        raise ApiError(f"Page with id {page_id} not found.")

    mocker.patch(
        "markdown_maker.clients.confluence_client.ConfluenceClient.get_page_content",
        side_effect=get_page_content_side_effect,
    )
    mocker.patch(
        "markdown_maker.clients.confluence_client.ConfluenceClient.get_child_pages",
        return_value=[{"id": child_id, "title": child_title}],
    )
    mocker.patch(
        "markdown_maker.converters.html_to_markdown.convert_html_to_markdown",
        side_effect=lambda html: html,
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
            "--max-depth",
            "2",
        ],
    )
    assert result.exit_code == 0
    assert (
        f"Could not access child page '{child_title}' (id {child_id})" in result.stderr
    )
    assert f"Page with id {child_id} not found." in result.stderr
    parent_dir = tmp_path / "parent_page"
    assert parent_dir.exists()
    parent_index = parent_dir / "index.md"
    assert parent_index.exists()
    assert "Parent" in parent_index.read_text()


def test_error_context_for_embedded_link(mocker, tmp_path):
    """Test that error message for embedded link fetch failure is logged and
    parent is still converted.
    """
    parent_id = "42"
    embedded_id = "9999"
    parent_title = "Parent Page"
    valid_url = (
        f"https://company.atlassian.net/wiki/pages/viewpage.action?pageId={parent_id}"
    )
    parent_page = {
        "title": parent_title,
        "body": {
            "storage": {
                "value": f'<a href="https://company.atlassian.net/wiki/pages/viewpage.action?pageId={embedded_id}">Embedded</a>'
            }
        },
    }

    def get_page_content_side_effect(page_id):
        if page_id == parent_id:
            return parent_page
        raise ApiError(f"Page with id {page_id} not found.")

    mocker.patch(
        "markdown_maker.clients.confluence_client.ConfluenceClient.get_page_content",
        side_effect=get_page_content_side_effect,
    )
    mocker.patch(
        "markdown_maker.clients.confluence_client.ConfluenceClient.get_child_pages",
        return_value=[],
    )
    mocker.patch(
        "markdown_maker.converters.html_to_markdown.convert_html_to_markdown",
        side_effect=lambda html: html,
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
            "--max-depth",
            "2",
        ],
    )
    assert result.exit_code == 0
    assert (
        f"Could not access embedded link 'https://company.atlassian.net/wiki/pages/viewpage.action?pageId={embedded_id}'"
        in result.stderr
    )
    assert f"extracted id {embedded_id}" in result.stderr
    assert f"Page with id {embedded_id} not found." in result.stderr
    parent_dir = tmp_path / "parent_page"
    assert parent_dir.exists()
    parent_index = parent_dir / "index.md"
    assert parent_index.exists()
    assert parent_index.read_text().strip() != ""


def test_child_page_error_logs_and_continues(mocker, tmp_path):
    """Test that error for child page is logged and parent is still converted."""
    parent_id = "42"
    child_id = "1234"
    parent_title = "Parent Page"
    child_title = "Child One"
    valid_url = (
        f"https://company.atlassian.net/wiki/pages/viewpage.action?pageId={parent_id}"
    )
    parent_page = {
        "title": parent_title,
        "body": {"storage": {"value": "<h1>Parent</h1>"}},
    }

    def get_page_content_side_effect(page_id):
        if page_id == parent_id:
            return parent_page
        raise ApiError(f"Page with id {page_id} not found.")

    mocker.patch(
        "markdown_maker.clients.confluence_client.ConfluenceClient.get_page_content",
        side_effect=get_page_content_side_effect,
    )
    mocker.patch(
        "markdown_maker.clients.confluence_client.ConfluenceClient.get_child_pages",
        return_value=[{"id": child_id, "title": child_title}],
    )
    mocker.patch(
        "markdown_maker.converters.html_to_markdown.convert_html_to_markdown",
        side_effect=lambda html: html,
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
            "--max-depth",
            "2",
        ],
    )
    assert result.exit_code == 0
    parent_dir = tmp_path / "parent_page"
    assert parent_dir.exists()
    parent_index = parent_dir / "index.md"
    assert parent_index.exists()
    assert (
        f"Could not access child page '{child_title}' (id {child_id})" in result.stderr
    )
    assert "Parent" in parent_index.read_text()


def test_embedded_link_error_logs_and_continues(mocker, tmp_path):
    """Test that error for embedded link is logged and parent is still converted."""
    parent_id = "42"
    embedded_id = "9999"
    parent_title = "Parent Page"
    valid_url = (
        f"https://company.atlassian.net/wiki/pages/viewpage.action?pageId={parent_id}"
    )
    parent_page = {
        "title": parent_title,
        "body": {
            "storage": {
                "value": f'<a href="https://company.atlassian.net/wiki/pages/viewpage.action?pageId={embedded_id}">Embedded</a>'
            }
        },
    }

    def get_page_content_side_effect(page_id):
        if page_id == parent_id:
            return parent_page
        raise ApiError(f"Page with id {page_id} not found.")

    mocker.patch(
        "markdown_maker.clients.confluence_client.ConfluenceClient.get_page_content",
        side_effect=get_page_content_side_effect,
    )
    mocker.patch(
        "markdown_maker.clients.confluence_client.ConfluenceClient.get_child_pages",
        return_value=[],
    )
    mocker.patch(
        "markdown_maker.converters.html_to_markdown.convert_html_to_markdown",
        side_effect=lambda html: html,
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
            "--max-depth",
            "2",
        ],
    )
    assert result.exit_code == 0
    parent_dir = tmp_path / "parent_page"
    assert parent_dir.exists()
    parent_index = parent_dir / "index.md"
    assert parent_index.exists()
    assert (
        f"Could not access embedded link 'https://company.atlassian.net/wiki/pages/viewpage.action?pageId={embedded_id}'"
        in result.stderr
    )
    assert parent_index.read_text().strip() != ""
