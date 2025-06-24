"""Confluence API client module.

This module contains the ConfluenceClient class for interacting with the
Confluence REST API.
"""

from atlassian import Confluence

from markdown_maker.utils.config import load_config


class ConfluenceClient:
    """Client for interacting with the Confluence REST API using
    atlassian-python-api.
    """

    def __init__(self) -> None:
        """Initializes the ConfluenceClient with config credentials.

        Loads the base URL and authentication credentials from the config.
        Raises an error if required configuration is missing.
        """
        config = load_config()
        self.client = Confluence(
            url=config["confluence_base_url"].rstrip("/"),
            username=config["confluence_username"],
            password=config["confluence_api_token"],
            cloud=True,
        )

    def get_page_content(self, page_id: str) -> dict:
        """Fetches a page's content from the Confluence REST API.

        Args:
            page_id: The ID of the Confluence page to fetch.

        Returns:
            The JSON response from the API as a dictionary.

        Raises:
            Exception: If the API request fails.
        """
        page = self.client.get_page_by_id(
            page_id, expand="body.storage,version,ancestors"
        )
        if not page:
            raise ValueError(f"Page with id {page_id} not found.")
        return page

    def get_child_pages(self, page_id: str) -> list:
        """Fetches the direct child pages of a given Confluence page.

        Args:
            page_id: The ID of the parent Confluence page.

        Returns:
            A list of dictionaries, each representing a child page.

        Raises:
            Exception: If the API request fails.
        """
        try:
            children = self.client.get_child_pages(page_id)
        except Exception as exc:
            raise RuntimeError(f"Failed to fetch child pages: {exc}") from exc
        return list(children) if children is not None else []
