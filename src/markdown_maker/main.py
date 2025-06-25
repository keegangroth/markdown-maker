"""Main entry point for the Markdown Maker CLI."""

import click
from bs4 import BeautifulSoup, Tag
from atlassian.errors import ApiError

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
    page_id: str,
    output_dir: str,
    max_depth: int,
    current_depth: int = 1,
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
            click.echo(f"Could not access child pages for {context}: {exc}", err=True)
            child_pages = []
        for child in child_pages:
            child_id = child.get("id")
            child_title = child.get("title", "unknown")
            try:
                handle_recursive_conversion(
                    child_id,
                    page_dir,
                    max_depth,
                    current_depth + 1,
                    visited,
                    parent_context=(
                        f"child page '{child_title}' (id {child_id}) of parent "
                        f"'{title}' (id {page_id}) at depth {current_depth + 1}"
                    ),
                )
            except ApiError as exc:
                msg = (
                    f"Could not access child page '{child_title}' (id {child_id}) "
                    f"of parent '{title}' (id {page_id}) at depth {current_depth + 1}:\n"
                    f"{exc}"
                )
                click.echo(msg, err=True)
            except Exception as exc:
                msg = f"Unexpected error for child page '{child_title}' (id {child_id}):\n{exc}"
                click.echo(msg, err=True)
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
                        embedded_page_id,
                        page_dir,
                        max_depth,
                        current_depth + 1,
                        visited,
                        parent_context=(
                            f"embedded link '{href}' (extracted id {embedded_page_id}) "
                            f"in page '{title}' (id {page_id}) at depth {current_depth + 1}"
                        ),
                    )
                except ApiError as exc:
                    msg = (
                        f"Could not access embedded link '{href}' (extracted id {embedded_page_id}) "
                        f"in page '{title}' (id {page_id}) at depth {current_depth + 1}:\n"
                        f"{exc}"
                    )
                    click.echo(msg, err=True)
                except Exception as exc:
                    msg = f"Unexpected error for embedded link '{href}' (extracted id {embedded_page_id}):\n{exc}"
                    click.echo(msg, err=True)
    except ApiError as exc:
        click.echo(f"Could not access {context}: {exc}", err=True)
    except Exception as exc:
        click.echo(f"Unexpected error for {context}: {exc}", err=True)


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

    def recurse(pid, current_url, depth):
        if depth > max_depth or pid in visited:
            return
        visited.add(pid)
        try:
            page = client.get_page_content(pid)
        except ApiError as exc:
            click.echo(f"Could not access page id {pid}: {exc}", err=True)
            return
        html = page.get("body", {}).get("storage", {}).get("value", "")
        markdown = convert_html_to_markdown(html)
        title = page.get("title", "confluence_page")
        discovered.append((title, current_url, markdown))
        # Child pages
        try:
            children = client.get_child_pages(pid)
        except Exception:
            children = []
        for child in children:
            child_id = child.get("id")
            child_url = f"https://company.atlassian.net/wiki/pages/viewpage.action?pageId={child_id}"
            recurse(child_id, child_url, depth + 1)
        # Embedded links
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
                recurse(embedded_page_id, href, depth + 1)

    recurse(page_id, url, 1)
    return discovered


def _single_file_option(ctx, param, value):
    # If --single-file is passed with no value, value is None but param is present in args
    # If --single-file is passed with a value, value is the string
    # If not passed, value is None
    import sys
    args = sys.argv
    if '--single-file' in args:
        idx = args.index('--single-file')
        # If next arg exists and does not start with '-', treat as filename
        if idx + 1 < len(args) and not args[idx + 1].startswith('-'):
            return args[idx + 1]
        return ''  # Flag present, no value
    return None


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

    def write_page_to_file(f, title, page_url, markdown, is_first):
        if not is_first:
            f.write("\n\n---\n\n")
        f.write(f"# {title}\n\n")
        f.write(f"Source: [{page_url}]({page_url})\n\n")
        f.write(markdown.strip())
        f.write("\n")

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
        if visited is None:
            visited = set()
        if current_depth > max_depth or pid in visited:
            return
        visited.add(pid)
        try:
            page = client.get_page_content(pid)
        except ApiError as exc:
            context = parent_context or f"page id {pid}"
            click.echo(f"Could not access {context}: {exc}", err=True)
            return
        html = page.get("body", {}).get("storage", {}).get("value", "")
        markdown = convert_html_to_markdown(html)
        title = page.get("title", "confluence_page")
        write_page_to_file(f, title, page_url, markdown, is_first)
        # Child pages
        try:
            children = client.get_child_pages(pid)
        except Exception:
            children = []
        for child in children:
            child_id = child.get("id")
            child_title = child.get("title", "unknown")
            child_url = f"https://company.atlassian.net/wiki/pages/viewpage.action?pageId={child_id}"
            single_file_recursive(
                child_id,
                child_url,
                f,
                max_depth,
                current_depth + 1,
                visited,
                is_first=False,
                parent_context=(
                    f"child page '{child_title}' (id {child_id}) of parent "
                    f"'{title}' (id {pid}) at depth {current_depth + 1}"
                ),
            )
        # Embedded links
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
                single_file_recursive(
                    embedded_page_id,
                    href,
                    f,
                    max_depth,
                    current_depth + 1,
                    visited,
                    is_first=False,
                    parent_context=(
                        f"embedded link '{href}' (extracted id {embedded_page_id}) "
                        f"in page '{title}' (id {pid}) at depth {current_depth + 1}"
                    ),
                )

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
        if recursive:
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
