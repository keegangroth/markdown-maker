"""Unit tests for the HTML to Markdown converter."""

import pytest

from markdown_maker.converters.html_to_markdown import convert_html_to_markdown


@pytest.mark.parametrize(
    "html,expected_md",
    [
        ("<h1>Title</h1>", "# Title\n"),
        ("<h2>Subtitle</h2>", "## Subtitle\n"),
        ("<ul><li>Item 1</li><li>Item 2</li></ul>", "- Item 1\n- Item 2\n"),
        ("<ol><li>First</li><li>Second</li></ol>", "1. First\n2. Second\n"),
        ("<strong>Bold</strong> and <b>also bold</b>", "**Bold** and **also bold**\n"),
        ("<em>Italic</em> and <i>also italic</i>", "_Italic_ and _also italic_\n"),
        ("<pre><code>print('hi')</code></pre>", "```\nprint('hi')\n```\n"),
        ("<p>Paragraph</p>", "Paragraph\n"),
        (
            "<p>Mix <strong>bold</strong> and <em>italic</em></p>",
            "Mix **bold** and _italic_\n",
        ),
    ],
)
def test_convert_html_to_markdown(html, expected_md):
    """Test HTML to Markdown conversion for various elements."""
    result = convert_html_to_markdown(html)
    # Accept both * and _ for italics, and both ** and __ for bold.
    normalized = result.strip().replace("*", "_").replace("__", "**")
    expected_normalized = expected_md.strip().replace("*", "_").replace("__", "**")
    assert normalized == expected_normalized
