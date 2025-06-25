"""Unit tests for error context in recursive conversion error handling."""

import pytest
from click.testing import CliRunner
from markdown_maker.main import cli
from atlassian.errors import ApiError


def test_error_context_for_child_page(mocker, tmp_path):
    """Test that error message for child page fetch failure includes context."""
    parent_id = "42"
    child_id = "1234"
    parent_title = "Parent Page"
    child_title = "Child One"
    valid_url = f"https://company.atlassian.net/wiki/pages/viewpage.action?pageId={parent_id}"
    parent_page = {
        "title": parent_title,
        "body": {"storage": {"value": "<h1>Parent</h1>"}},
    }
    # Simulate child page fetch raising HTTPError
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
    with pytest.raises(RuntimeError) as exc:
        runner.invoke(
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
            catch_exceptions=False,
        )
    msg = str(exc.value)
    assert f"Failed to fetch child page '{child_title}' (id {child_id})" in msg or f"Failed to fetch child page '{child_title}' (id {child_id})" in msg or f"Failed to fetch child page '{child_title}' (id {child_id})" in msg
    assert f"Page with id {child_id} not found." in msg


def test_error_context_for_embedded_link(mocker, tmp_path):
    """Test that error message for embedded link fetch failure includes context."""
    parent_id = "42"
    embedded_id = "9999"
    parent_title = "Parent Page"
    valid_url = f"https://company.atlassian.net/wiki/pages/viewpage.action?pageId={parent_id}"
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
    with pytest.raises(RuntimeError) as exc:
        runner.invoke(
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
            catch_exceptions=False,
        )
    msg = str(exc.value)
    assert f"Failed to fetch embedded link" in msg or f"Failed to recursively convert embedded link" in msg
    assert f"extracted id {embedded_id}" in msg
    assert f"Page with id {embedded_id} not found." in msg
