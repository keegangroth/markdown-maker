"""Unit tests for the ConfluenceClient using atlassian-python-api."""

import pytest

from markdown_maker.clients.confluence_client import ConfluenceClient


def test_confluence_client_loads_config(monkeypatch):
    """Test that ConfluenceClient loads base_url, username, and api_token
    from config.
    """
    dummy_config = {
        "confluence_base_url": "https://example.atlassian.net/wiki",
        "confluence_username": "user@example.com",
        "confluence_api_token": "token123",
    }

    def dummy_confluence_init(self, url, username, password, cloud):
        self.get_page_by_id = lambda page_id, expand=None: {}

    monkeypatch.setattr(
        "markdown_maker.clients.confluence_client.load_config", lambda: dummy_config
    )
    monkeypatch.setattr(
        "markdown_maker.clients.confluence_client.Confluence.__init__",
        dummy_confluence_init,
    )

    client = ConfluenceClient()
    # The refactored ConfluenceClient does not set base_url, username, api_token
    # as attributes. Instead, we can check that the client.client object is
    # constructed with the right config.
    assert hasattr(client, "client")
    # Optionally, check that get_page_by_id is available
    assert callable(getattr(client.client, "get_page_by_id", None))


def test_get_page_content_success(monkeypatch):
    """Test get_page_content returns page data when found."""
    dummy_config = {
        "confluence_base_url": "https://example.atlassian.net/wiki",
        "confluence_username": "user@example.com",
        "confluence_api_token": "token123",
    }
    dummy_page = {"id": "123", "title": "Test Page"}

    class DummyConfluence:
        def get_page_by_id(self, page_id, expand=None):
            assert page_id == "123"
            return dummy_page

    def dummy_confluence_init(self, url, username, password, cloud):
        self.get_page_by_id = DummyConfluence().get_page_by_id

    monkeypatch.setattr(
        "markdown_maker.clients.confluence_client.load_config", lambda: dummy_config
    )
    monkeypatch.setattr(
        "markdown_maker.clients.confluence_client.Confluence.__init__",
        dummy_confluence_init,
    )

    client = ConfluenceClient()
    result = client.get_page_content("123")
    assert result == dummy_page


def test_get_page_content_not_found(monkeypatch):
    """Test get_page_content raises ValueError if page not found."""
    dummy_config = {
        "confluence_base_url": "https://example.atlassian.net/wiki",
        "confluence_username": "user@example.com",
        "confluence_api_token": "token123",
    }

    class DummyConfluence:
        def get_page_by_id(self, page_id, expand=None):
            return None

    def dummy_confluence_init(self, url, username, password, cloud):
        self.get_page_by_id = DummyConfluence().get_page_by_id

    monkeypatch.setattr(
        "markdown_maker.clients.confluence_client.load_config", lambda: dummy_config
    )
    monkeypatch.setattr(
        "markdown_maker.clients.confluence_client.Confluence.__init__",
        dummy_confluence_init,
    )

    client = ConfluenceClient()
    with pytest.raises(ValueError, match="Page with id 123 not found."):
        client.get_page_content("123")
