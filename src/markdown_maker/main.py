"""Main entry point for the Markdown Maker CLI."""

from collections.abc import Callable

import click
from atlassian.errors import ApiError
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


def write_markdown_page(f, title: str, page_url: str, markdown: str, is_first: bool = True) -> None:
    """Write a Markdown page to a file-like object, with heading and source link."""
    if not is_first:
        f.write("\n\n---\n\n")
    f.write(f"# {title}\n\n")
    f.write(f"Source: [{page_url}]({page_url})\n\n")
    f.write(markdown.strip())
    f.write("\n")


def recurse_children(
    get_child_pages_fn,
    parent_id: str,
    parent_dir: str,
    max_depth: int,
    current_depth: int,
    visited: set,
    parent_title: str,
    parent_context: str,
    recurse_fn,
) -> None:
    """Recurse into child pages, calling recurse_fn for each."""
    try:
        child_pages = get_child_pages_fn(parent_id)
    except ApiError as exc:
        click.echo(f"Could not access child pages for {parent_context}: {exc}", err=True)
        child_pages = []
    for child in child_pages:
        child_id = child.get("id")
        child_title = child.get("title", "unknown")
        try:
            recurse_fn(
                child_id,
                parent_dir,
                max_depth,
                current_depth + 1,
                visited,
                parent_context=(
                    f"child page '{child_title}' (id {child_id}) of parent "
                    f"'{parent_title}' (id {parent_id}) at depth {current_depth + 1}"
                ),
            )
        except ApiError as exc:
            msg = (
                f"Could not access child page '{child_title}' (id {child_id}) "
                f"of parent '{parent_title}' (id {parent_id}) at depth {current_depth + 1}:\n"
                f"{exc}"
            )
            click.echo(msg, err=True)
        except Exception as exc:
            msg = f"Unexpected error for child page '{child_title}' (id {child_id}):\n{exc}"
            click.echo(msg, err=True)


def recurse_embedded_links(
    html: str,
    parent_dir: str,
    max_depth: int,
    current_depth: int,
    visited: set,
    parent_title: str,
    parent_id: str,
    recurse_fn,
) -> None:
    """Recurse into embedded Confluence links in the HTML, calling recurse_fn for each."""
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
                recurse_fn(
                    embedded_page_id,
                    parent_dir,
                    max_depth,
                    current_depth + 1,
                    visited,
                    parent_context=(
                        f"embedded link '{href}' (extracted id {embedded_page_id}) "
                        f"in page '{parent_title}' (id {parent_id}) at depth {current_depth + 1}"
                    ),
                )
            except ApiError as exc:
                msg = (
                    f"Could not access embedded link '{href}' (extracted id {embedded_page_id}) "
                    f"in page '{parent_title}' (id {parent_id}) at depth {current_depth + 1}:\n"
                    f"{exc}"
                )
                click.echo(msg, err=True)
            except Exception as exc:
                msg = f"Unexpected error for embedded link '{href}' (extracted id {embedded_page_id}):\n{exc}"
                click.echo(msg, err=True)


def handle_recursive_conversion(
    page_id: str,
    output_dir: str,
    max_depth: int,
    current_depth: int = 1,
    visited: set | None = None,
    parent_context: str = "",
) -> None:
    if visited is None:
        visited = set()
    client = ConfluenceClient()
    def handle_page(title: str, page_url: str, markdown: str, depth: int, parent_dir: str | None) -> str:
        import os
        dir_name = sanitize_dirname(title)
        page_dir = os.path.join(parent_dir, dir_name) if parent_dir else os.path.join(output_dir, dir_name)
        os.makedirs(page_dir, exist_ok=True)
        output_path = os.path.join(page_dir, "index.md")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown)
        return page_dir
    traverse_confluence_tree(
        pid=page_id,
        page_url=f"https://company.atlassian.net/wiki/pages/viewpage.action?pageId={page_id}",
        max_depth=max_depth,
        current_depth=current_depth,
        visited=visited,
        client=client,
        handle_page=handle_page,
        parent_context=parent_context,
        parent_dir=None,
        link_type="root",
    )


def collect_discovered_pages_single(page_id: str, url: str) -> list[tuple[str, str, str]]:
    """Collect a single page for single-file output."""
    client = ConfluenceClient()
    try:
        page = client.get_page_content(page_id)
    except ApiError as exc:
        click.echo(f"Could not access page id {page_id}: {exc}", err=True)
        return []
    html = page.get("body", {}).get("storage", {}).get("value", "")
    markdown = convert_html_to_markdown(html)
    title = page.get("title", "confluence_page")
    return [(title, url, markdown)]


def collect_discovered_pages_recursive(page_id: str, url: str, max_depth: int) -> list[tuple[str, str, str]]:
    """Collect all discovered pages recursively for single-file output."""
    client = ConfluenceClient()
    discovered = []
    visited = set()
    def handle_page(title: str, page_url: str, markdown: str, depth: int, parent_dir: str | None) -> str:
        discovered.append((title, page_url, markdown))
        return ""
    traverse_confluence_tree(
        pid=page_id,
        page_url=url,
        max_depth=max_depth,
        current_depth=1,
        visited=visited,
        client=client,
        handle_page=handle_page,
        link_type="root",
        parent_dir=None,
    )
    return discovered


def single_file_recursive(
    pid: str,
    page_url: str,
    f,
    max_depth: int,
    current_depth: int = 1,
    visited: set | None = None,
    is_first: bool = False,
    parent_context: str = "",
) -> None:
    """Recursively write discovered pages to a single file as they are found (progressive write)."""
    if visited is None:
        visited = set()
    client = ConfluenceClient()
    first_page = True if is_first else False
    def handle_page(title: str, url: str, markdown: str, depth: int, parent_dir: str | None) -> str:
        nonlocal first_page
        write_markdown_page(f, title, url, markdown, is_first=first_page)
        first_page = False
        return ""
    traverse_confluence_tree(
        pid=pid,
        page_url=page_url,
        max_depth=max_depth,
        current_depth=current_depth,
        visited=visited,
        client=client,
        handle_page=handle_page,
        parent_context=parent_context,
        parent_dir=None,
        link_type="root",
    )


def traverse_confluence_tree(
    pid: str,
    page_url: str,
    max_depth: int,
    current_depth: int,
    visited: set,
    client: ConfluenceClient,
    handle_page: Callable[[str, str, str, int, str | None], str],
    parent_context: str = "",
    parent_dir: str | None = None,
    link_type: str = "root",
    child_title: str | None = None,
    parent_title: str | None = None,
    parent_id: str | None = None,
) -> None:
    """Unified recursive traversal for Confluence page trees.

    Args:
        pid: The page ID to start from.
        page_url: The URL of the current page.
        max_depth: Maximum recursion depth.
        current_depth: Current recursion depth.
        visited: Set of visited page IDs.
        client: ConfluenceClient instance.
        handle_page: Callback to handle each discovered page. Returns the directory for children.
        parent_context: Context string for error reporting.
        parent_dir: Directory in which to create this page's directory (for multi-file output).
    """
    if current_depth > max_depth or pid in visited:
        return
    visited.add(pid)
    try:
        page = client.get_page_content(pid)
    except ApiError as exc:
        if link_type == "child":
            context = (
                f"child page '{child_title}' (id {pid}) of parent '{parent_title}' (id {parent_id}) at depth {current_depth}"  # noqa: E501
            )
            click.echo(f"Could not access {context}: {exc}", err=True)
        elif link_type == "embedded":
            # Try to extract the id for error context
            try:
                extracted_id = extract_page_id_from_url(page_url)
                click.echo(
                    f"Could not access embedded link '{page_url}' (extracted id {extracted_id}): {exc}",
                    err=True,
                )
            except Exception:
                click.echo(f"Could not access embedded link '{page_url}': {exc}", err=True)
        else:
            context = parent_context or f"page id {pid}"
            click.echo(f"Could not access {context}: {exc}", err=True)
        return
    html = page.get("body", {}).get("storage", {}).get("value", "")
    markdown = convert_html_to_markdown(html)
    title = page.get("title", "confluence_page")
    page_dir = handle_page(title, page_url, markdown, current_depth, parent_dir)
    # Recurse children
    try:
        children = client.get_child_pages(pid)
    except Exception:
        children = []
    for child in children:
        child_id = child.get("id")
        child_title = child.get("title", "unknown")
        child_url = f"https://company.atlassian.net/wiki/pages/viewpage.action?pageId={child_id}"
        traverse_confluence_tree(
            child_id,
            child_url,
            max_depth,
            current_depth + 1,
            visited,
            client,
            handle_page,
            parent_context=parent_context,
            parent_dir=page_dir,
            link_type="child",
            child_title=child_title,
            parent_title=title,
            parent_id=pid,
        )
    # Recurse embedded links
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
            traverse_confluence_tree(
                embedded_page_id,
                href,
                max_depth,
                current_depth + 1,
                visited,
                client,
                handle_page,
                parent_context=parent_context,
                parent_dir=page_dir,
                link_type="embedded",
            )


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
@click.option(
    "--single-file",
    is_flag=True,
    help="Concatenate all discovered pages into a single Markdown file (named after the page title).",
)
def convert(
    url: str,
    output_dir: str,
    recursive: bool,
    max_depth: int,
    single_file: bool,
) -> None:
    """Converts a Confluence page to a Markdown file."""
    import os

    page_id = extract_page_id_from_url(url)
    os.makedirs(output_dir, exist_ok=True)

    client = ConfluenceClient()
    page = client.get_page_content(page_id)
    title = page.get("title", "confluence_page")
    output_filename = sanitize_filename(title)
    output_path = os.path.join(output_dir, output_filename)

    if single_file:
        if os.path.exists(output_path):
            click.echo(f"Warning: {output_path} already exists.", err=True)
            if not click.confirm(f"Overwrite {output_path}?", default=False):
                click.echo("Aborted by user.", err=True)
                return
        with open(output_path, "w", encoding="utf-8") as f:
            single_file_recursive(
                page_id,
                url,
                f,
                max_depth,
                current_depth=1,
                visited=None,
                is_first=True,
            )
        click.echo(f"Saved: {output_path}")
        click.echo(f"URL: {url}")
        click.echo(f"Output Directory: {output_dir}")
        click.echo(f"Recursive: {recursive}")
        click.echo(f"Max Depth: {max_depth}")
        return
    if recursive:
        handle_recursive_conversion(page_id, output_dir, max_depth)
        click.echo(f"Recursive: {recursive}")
        click.echo(f"Max Depth: {max_depth}")
        click.echo(f"URL: {url}")
        click.echo(f"Output Directory: {output_dir}")
        return
    html = page.get("body", {}).get("storage", {}).get("value", "")
    markdown = convert_html_to_markdown(html)
    title = page.get("title", "confluence_page")
    filename = sanitize_filename(title)
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
