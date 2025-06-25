"""Unit tests for recursive output structure: nested directories by page title."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from markdown_maker.main import cli


@pytest.fixture
def dummy_page_with_children():
    return {
        "title": "Parent Page",
        "body": {"storage": {"value": "<h1>Parent</h1>"}},
        "_children": [
            {
                "id": "1234",
                "title": "Child One",
                "body": {"storage": {"value": "<h2>Child 1</h2>"}},
                "_children": [],
            },
            {
                "id": "5678",
                "title": "Child Two",
                "body": {"storage": {"value": "<h2>Child 2</h2>"}},
                "_children": [],
            },
        ],
    }


def test_recursive_creates_nested_directories(
    tmp_path: Path, mocker, dummy_page_with_children
):
    """Test that recursive conversion creates nested directories and index.md files."""
    valid_url = (
        "https://company.atlassian.net/wiki/pages/viewpage.action?pageId=42"
    )
    # Patch ConfluenceClient.get_page_content to return dummy page or children
    def get_page_content_side_effect(page_id):
        if page_id == "42":
            return dummy_page_with_children
        for child in dummy_page_with_children["_children"]:
            if child["id"] == page_id:
                return child
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
    mocker.patch(
        "markdown_maker.clients.confluence_client.ConfluenceClient.get_child_pages",
        side_effect=lambda page_id: dummy_page_with_children["_children"]
        if page_id == "42"
        else [],
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
    child1_dir = parent_dir / "child_one"
    child2_dir = parent_dir / "child_two"
    for child_dir, child_title in zip(
        [child1_dir, child2_dir], ["Child 1", "Child 2"]
    ):
        assert child_dir.exists() and child_dir.is_dir()
        child_index = child_dir / "index.md"
        assert child_index.exists()
        assert f"## {child_title}" in child_index.read_text()
