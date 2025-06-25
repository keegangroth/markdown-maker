from collections.abc import Callable

import click
from atlassian.errors import ApiError
from bs4 import BeautifulSoup, Tag

from markdown_maker.clients.confluence_client import ConfluenceClient
from markdown_maker.converters.html_to_markdown import convert_html_to_markdown
from markdown_maker.utils.helpers import extract_page_id_from_url


class ConfluenceTreeTraverser:
    """Encapsulates recursive traversal state and logic for Confluence page trees."""
    def __init__(
        self,
        client: ConfluenceClient,
        max_depth: int,
        handle_page: Callable[[str, str, str, int, str | None], str],
        parent_context: str = "",
        parent_dir: str | None = None,
    ):
        self.client = client
        self.max_depth = max_depth
        self.handle_page = handle_page
        self.parent_context = parent_context
        self.parent_dir = parent_dir
        self.visited: set[str] = set()

    def traverse(self,
        pid: str,
        page_url: str,
        current_depth: int = 1,
        link_type: str = "root",
        child_title: str | None = None,
        parent_title: str | None = None,
        parent_id: str | None = None,
        parent_dir: str | None = None,
    ) -> None:
        if current_depth > self.max_depth or pid in self.visited:
            return
        self.visited.add(pid)
        try:
            page = self.client.get_page_content(pid)
        except ApiError as exc:
            self._handle_error(exc, link_type, pid, page_url, current_depth, child_title, parent_title, parent_id)
            return
        html = page.get("body", {}).get("storage", {}).get("value", "")
        markdown = convert_html_to_markdown(html)
        title = page.get("title", "confluence_page")
        page_dir = self.handle_page(title, page_url, markdown, current_depth, parent_dir or self.parent_dir)
        self._traverse_children(pid, title, page_dir, current_depth)
        self._traverse_embedded_links(html, page_dir, current_depth)

    def _handle_error(self, exc, link_type, pid, page_url, current_depth, child_title, parent_title, parent_id):
        if link_type == "child":
            context = (
                f"child page '{child_title}' (id {pid}) of parent '{parent_title}' (id {parent_id}) at depth {current_depth}"  # noqa: E501
            )
            click.echo(f"Could not access {context}: {exc}", err=True)
        elif link_type == "embedded":
            try:
                extracted_id = extract_page_id_from_url(page_url)
                click.echo(
                    f"Could not access embedded link '{page_url}' (extracted id {extracted_id}): {exc}",
                    err=True,
                )
            except Exception:
                click.echo(f"Could not access embedded link '{page_url}': {exc}", err=True)
        else:
            context = self.parent_context or f"page id {pid}"
            click.echo(f"Could not access {context}: {exc}", err=True)

    def _traverse_children(self, pid, title, page_dir, current_depth):
        try:
            children = self.client.get_child_pages(pid)
        except Exception:
            children = []
        for child in children:
            child_id = child.get("id")
            child_title = child.get("title", "unknown")
            child_url = f"https://company.atlassian.net/wiki/pages/viewpage.action?pageId={child_id}"
            self.traverse(
                child_id,
                child_url,
                current_depth + 1,
                link_type="child",
                child_title=child_title,
                parent_title=title,
                parent_id=pid,
                parent_dir=page_dir,
            )

    def _traverse_embedded_links(self, html, page_dir, current_depth):
        soup = BeautifulSoup(html, "html.parser")
        for a in soup.find_all("a"):
            if isinstance(a, Tag):
                href = a.get("href")
                if not isinstance(href, str):
                    continue
                try:
                    embedded_page_id = extract_page_id_from_url(href)
                except ValueError:
                    continue
                self.traverse(
                    embedded_page_id,
                    href,
                    current_depth + 1,
                    link_type="embedded",
                    parent_dir=page_dir,
                )
