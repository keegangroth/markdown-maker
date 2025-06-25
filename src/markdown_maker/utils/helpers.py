"""Helpers for Markdown Maker utilities.

This module provides utility functions for the Markdown Maker project.
"""

import re


def extract_page_id_from_url(url: str) -> str:
    """Extract the Confluence page_id from a given Confluence URL.

    Supports both canonical and viewpage.action URL formats.

    Args:
        url: The Confluence page URL.

    Returns:
        The extracted page_id as a string.

    Raises:
        ValueError: If the page_id cannot be found in the URL.
    """
    # Try canonical URL: .../pages/<page_id>/
    match = re.search(r"/pages/(\d+)(/|$)", url)
    if match:
        return match.group(1)
    # Try viewpage.action URL: ...pageId=<page_id>
    match = re.search(r"[?&]pageId=(\d+)", url)
    if match:
        return match.group(1)
    raise ValueError(f"Could not extract page_id from URL: {url}")


def sanitize_dirname(title: str) -> str:
    """Sanitize a page title to create a valid directory name."""
    import re

    name = title.lower()
    name = re.sub(r"[^a-z0-9]+", "_", name)
    name = re.sub(r"_+", "_", name).strip("_")
    return name
