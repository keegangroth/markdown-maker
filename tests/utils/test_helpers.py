"""Unit tests for helpers.py: extract_page_id_from_url utility.

Tests cover typical, edge, and invalid Confluence URL cases.
"""

import pytest

from markdown_maker.utils.helpers import extract_page_id_from_url


@pytest.mark.parametrize(
    "url,expected",
    [
        (
            "https://company.atlassian.net/wiki/spaces/SPACE/pages/123456789/Page+Title",
            "123456789",
        ),
        (
            "https://company.atlassian.net/wiki/pages/viewpage.action?pageId=987654321",
            "987654321",
        ),
        (
            "https://company.atlassian.net/wiki/spaces/SPACE/pages/1122334455/",
            "1122334455",
        ),
        (
            "https://company.atlassian.net/wiki/pages/viewpage.action?pageId=1",
            "1",
        ),
    ],
)
def test_extract_page_id_from_url_valid(url: str, expected: str) -> None:
    """Test extraction of page_id from valid Confluence URLs."""
    assert extract_page_id_from_url(url) == expected


def test_extract_page_id_from_url_invalid() -> None:
    """Test extraction raises ValueError for invalid URLs."""
    with pytest.raises(ValueError):
        extract_page_id_from_url(
            "https://company.atlassian.net/wiki/spaces/SPACE/pages//Page+Title"
        )
    with pytest.raises(ValueError):
        extract_page_id_from_url(
            "https://company.atlassian.net/wiki/pages/viewpage.action"
        )
    with pytest.raises(ValueError):
        extract_page_id_from_url("not a url")
    with pytest.raises(ValueError):
        extract_page_id_from_url("")
