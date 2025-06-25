"""Main entry point for the Markdown Maker CLI."""

import click

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


def handle_recursive_conversion(
    page_id: str, output_dir: str, max_depth: int, current_depth: int = 1
) -> None:
    """Recursively fetch, convert, and save a page and its child pages.

    Recursion stops when current_depth > max_depth.
    """
    if current_depth > max_depth:
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
    # Fetch and recurse into child pages
    child_pages = client.get_child_pages(page_id)
    for child in child_pages:
        child_id = child.get("id")
        child_title = child.get("title", "child_page")
        child_dir = os.path.join(
            output_dir, sanitize_filename(child_title).replace(".md", "")
        )
        handle_recursive_conversion(child_id, child_dir, max_depth, current_depth + 1)


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
