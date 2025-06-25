"""HTML to Markdown conversion utilities.

This module provides a function to convert HTML content to Markdown using
BeautifulSoup and markdownify.

Functions:
    convert_html_to_markdown(html: str) -> str: Convert HTML to Markdown.
    write_markdown_page(f, title: str, page_url: str, markdown: str, is_first: bool = True) -> None:
        Write a Markdown page to a file-like object.
"""

from bs4 import BeautifulSoup
from markdownify import markdownify as md


def convert_html_to_markdown(html: str) -> str:
    """Convert HTML content to Markdown format.

    Args:
        html: The HTML string to convert.

    Returns:
        The converted Markdown string.
    """
    soup = BeautifulSoup(html, "html.parser")
    # Use only supported markdownify options for bold/italic
    markdown = md(
        str(soup),
        heading_style="ATX",  # Use # for headings
        bullets="-*",  # Use - or * for unordered lists
        code_language_detection=True,  # Try to detect code block language
        strip=["style", "script"],  # Remove style/script tags
        escape_underscores=False,  # Allow underscores in text
        wrap=True,  # Enable line wrapping
        wrap_width=120,  # Set wrap width to 120
    )
    return markdown


def write_markdown_page(
    f,
    title: str,
    page_url: str,
    markdown: str,
    is_first: bool = True,
) -> None:
    """Write a Markdown page to a file-like object, with heading and source link.

    Args:
        f: File-like object to write to.
        title: The page title.
        page_url: The source URL.
        markdown: The Markdown content.
        is_first: If True, do not prepend a separator.
    """
    if not is_first:
        f.write("\n\n---\n\n")
    f.write(f"# {title}\n\n")
    f.write(f"Source: [{page_url}]({page_url})\n\n")
    f.write(markdown.strip())
    f.write("\n")
