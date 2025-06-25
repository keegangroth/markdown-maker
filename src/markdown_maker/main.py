"""Main entry point for the Markdown Maker CLI."""

import click
from bs4 import BeautifulSoup, Tag

from markdown_maker.clients.confluence_client import ConfluenceClient
from markdown_maker.converters.html_to_markdown import convert_html_to_markdown
from markdown_maker.utils.helpers import extract_page_id_from_url


@click.group()
def cli() -> None:
    """A CLI tool to convert Confluence pages to Markdown."""
    pass


def sanitize_filename(title: str) -> str:
    """Sanitize a page title to create a valid Markdown filename."""
    import re

    name = title.lower()
    name = re.sub(r"[^a-z0-9]+", "_", name)
    name = re.sub(r"_+", "_", name).strip("_")
    return f"{name}.md"


def sanitize_dirname(title: str) -> str:
    """Sanitize a page title to create a valid directory name."""
    import re

    name = title.lower()
    name = re.sub(r"[^a-z0-9]+", "_", name)
    name = re.sub(r"_+", "_", name).strip("_")
    return name


def handle_recursive_conversion(
    page_id: str, output_dir: str, max_depth: int, current_depth: int = 1,
    visited: set | None = None,
    parent_context: str = "",
) -> None:
    """Recursively fetch, convert, and save a page, its child pages, and embedded links.

    Recursion stops when current_depth > max_depth.
    Each page is saved as index.md in a directory named after the sanitized title.
    Embedded Confluence links are also recursively converted,
    mirroring the directory structure.
    """
    if visited is None:
        visited = set()
    if current_depth > max_depth or page_id in visited:
        return
    visited.add(page_id)
    import os
    from atlassian.errors import ApiError

    context = parent_context or f"page id {page_id} at depth {current_depth}"
    try:
        client = ConfluenceClient()
        page = client.get_page_content(page_id)
        html = page.get("body", {}).get("storage", {}).get("value", "")
        markdown = convert_html_to_markdown(html)
        title = page.get("title", "confluence_page")
        dir_name = sanitize_dirname(title)
        page_dir = os.path.join(output_dir, dir_name)
        os.makedirs(page_dir, exist_ok=True)
        output_path = os.path.join(page_dir, "index.md")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown)
        # Fetch and recurse into child pages
        try:
            child_pages = client.get_child_pages(page_id)
        except ApiError as exc:
            raise RuntimeError(
                f"Failed to fetch child pages for {context}: {exc}"
            ) from exc
        for child in child_pages:
            child_id = child.get("id")
            child_title = child.get("title", "unknown")
            try:
                handle_recursive_conversion(
                    child_id, page_dir, max_depth, current_depth + 1, visited,
                    parent_context=f"child page '{child_title}' (id {child_id}) of parent '{title}' (id {page_id}) at depth {current_depth + 1}"
                )
            except ApiError as exc:
                raise RuntimeError(
                    f"Failed to recursively convert child page '{child_title}' (id {child_id}) "
                    f"of parent '{title}' (id {page_id}) at depth {current_depth + 1}: {exc}"
                ) from exc
        # Find embedded Confluence links in the HTML
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
                try:
                    handle_recursive_conversion(
                        embedded_page_id, page_dir, max_depth, current_depth + 1, visited,
                        parent_context=f"embedded link '{href}' (extracted id {embedded_page_id}) in page '{title}' (id {page_id}) at depth {current_depth + 1}"
                    )
                except ApiError as exc:
                    raise RuntimeError(
                        f"Failed to recursively convert embedded link '{href}' (extracted id {embedded_page_id}) "
                        f"in page '{title}' (id {page_id}) at depth {current_depth + 1}: {exc}"
                    ) from exc
    except ApiError as exc:
        raise RuntimeError(f"Failed to fetch {context}: {exc}") from exc


@cli.command()
@click.option("--url", required=True, help="The URL of the Confluence page to convert.")
@click.option(
    "--output-dir",
    default=".",
    help="The directory to save the Markdown file.",
    type=click.Path(file_okay=False, dir_okay=True, writable=True, resolve_path=True),
)
@click.option("--recursive", is_flag=True, help="Recursively convert child pages.")
@click.option(
    "--max-depth",
    default=3,
    show_default=True,
    type=int,
    help="Maximum recursion depth for child/embedded pages.",
)
def convert(url: str, output_dir: str, recursive: bool, max_depth: int) -> None:
    """Converts a Confluence page to a Markdown file."""
    page_id = extract_page_id_from_url(url)
    if recursive:
        handle_recursive_conversion(page_id, output_dir, max_depth)
        click.echo(f"Recursive: {recursive}")
        click.echo(f"Max Depth: {max_depth}")
        click.echo(f"URL: {url}")
        click.echo(f"Output Directory: {output_dir}")
        return
    client = ConfluenceClient()
    page = client.get_page_content(page_id)
    html = page.get("body", {}).get("storage", {}).get("value", "")
    markdown = convert_html_to_markdown(html)
    title = page.get("title", "confluence_page")
    filename = sanitize_filename(title)
    import os

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown)
    click.echo(f"Saved: {output_path}")
    click.echo(f"URL: {url}")
    click.echo(f"Output Directory: {output_dir}")
    click.echo(f"Recursive: {recursive}")
    if recursive:
        click.echo(f"Max Depth: {max_depth}")


if __name__ == "__main__":
    cli()
