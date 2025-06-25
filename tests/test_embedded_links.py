"""Unit tests for recursion into embedded Confluence links."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from markdown_maker.main import cli


@pytest.fixture
def dummy_page_with_embedded_links():
    return {
        "title": "Parent Page",
        "body": {
            "storage": {
                "value": (
                    '<h1>Parent</h1>'
                    '<a href="https://company.atlassian.net/wiki/pages/viewpage.action?pageId=1111">'
                    'Embedded 1</a>'
                    '<a href="https://company.atlassian.net/wiki/pages/viewpage.action?pageId=2222">'
                    'Embedded 2</a>'
                )
            }
        },
        "_children": [],
    }


@pytest.fixture
def embedded_page():
    def _page(page_id, title, header):
        return {
            "title": title,
            "body": {"storage": {"value": f"<h2>{header}</h2>"}},
            "_children": [],
        }

    return _page


def test_embedded_links_are_recursively_converted(
    tmp_path: Path, mocker, dummy_page_with_embedded_links, embedded_page
):
    """Test that embedded Confluence links are detected and recursively converted."""
    valid_url = (
        "https://company.atlassian.net/wiki/pages/viewpage.action?pageId=42"
    )
    # Map page_id to page data
    page_map = {
        "42": dummy_page_with_embedded_links,
        "1111": embedded_page("1111", "Embedded One", "Embedded 1"),
        "2222": embedded_page("2222", "Embedded Two", "Embedded 2"),
    }

    def get_page_content_side_effect(page_id):
        return page_map[page_id]

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
    mocker.patch(
        "markdown_maker.clients.confluence_client.ConfluenceClient.get_child_pages",
        return_value=[],
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
    assert parent_dir.exists() and parent_dir.is_dir()
    parent_index = parent_dir / "index.md"
    assert parent_index.exists()
    assert "# Parent" in parent_index.read_text()
    embedded1_dir = parent_dir / "embedded_one"
    embedded2_dir = parent_dir / "embedded_two"
    for emb_dir, emb_title in zip(
        [embedded1_dir, embedded2_dir], ["Embedded 1", "Embedded 2"]
    ):
        assert emb_dir.exists() and emb_dir.is_dir()
        emb_index = emb_dir / "index.md"
        assert emb_index.exists()
        assert f"## {emb_title}" in emb_index.read_text()


def test_embedded_links_respect_max_depth(
    tmp_path: Path, mocker, dummy_page_with_embedded_links, embedded_page
):
    """Test that recursion into embedded links respects the max_depth limit."""
    valid_url = (
        "https://company.atlassian.net/wiki/pages/viewpage.action?pageId=42"
    )
    page_map = {
        "42": dummy_page_with_embedded_links,
        "1111": embedded_page("1111", "Embedded One", "Embedded 1"),
        "2222": embedded_page("2222", "Embedded Two", "Embedded 2"),
    }

    def get_page_content_side_effect(page_id):
        return page_map[page_id]

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
    mocker.patch(
        "markdown_maker.clients.confluence_client.ConfluenceClient.get_child_pages",
        return_value=[],
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
            "1",
        ],
    )
    assert result.exit_code == 0
    parent_dir = tmp_path / "parent_page"
    assert parent_dir.exists() and parent_dir.is_dir()
    parent_index = parent_dir / "index.md"
    assert parent_index.exists()
    assert "# Parent" in parent_index.read_text()
    # Embedded pages should NOT be created due to max_depth=1
    assert not (parent_dir / "embedded_one").exists()
    assert not (parent_dir / "embedded_two").exists()
