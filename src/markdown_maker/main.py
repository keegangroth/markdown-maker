"""Main entry point for the Markdown Maker CLI."""

import click

from markdown_maker.clients.confluence_client import ConfluenceClient
from markdown_maker.clients.confluence_tree_traverser import ConfluenceTreeTraverser
from markdown_maker.converters.html_to_markdown import convert_html_to_markdown
from markdown_maker.utils.handlers import make_handle_page_multi, make_handle_page_single
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


def traverse_and_write(
    page_id: str,
    url: str,
    output_dir: str | None = None,
    max_depth: int = 3,
    single_file: bool = False,
    output_path: str | None = None,
    parent_context: str = "",
    skip_strikethrough_links: bool = False,
) -> None:
    """Unified recursive traversal for both single-file and multi-file output modes.

    Args:
        page_id: The root page ID.
        url: The root page URL.
        output_dir: Output directory for multi-file mode.
        max_depth: Maximum recursion depth.
        single_file: Whether to concatenate all pages into a single file.
        output_path: Output file path for single-file mode.
        parent_context: Context for error messages.
        skip_strikethrough_links: If True, skip recursion into struck-through links.
    """
    if single_file:
        if not output_path:
            raise ValueError("output_path must be provided for single_file mode.")
        # Truncate file before writing
        with open(output_path, "w", encoding="utf-8"):
            pass
        handler = make_handle_page_single(output_path)
    else:
        if not output_dir:
            raise ValueError("output_dir must be provided for multi-file mode.")
        handler = make_handle_page_multi(output_dir)
    traverser = ConfluenceTreeTraverser(
        client=ConfluenceClient(),
        max_depth=max_depth,
        handle_page=handler,
        parent_context=parent_context,
        parent_dir=None,
        skip_strikethrough_links=skip_strikethrough_links,
    )
    traverser.traverse(
        pid=page_id,
        page_url=url if single_file else f"https://company.atlassian.net/wiki/pages/viewpage.action?pageId={page_id}",
        current_depth=1,
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
@click.option(
    "--skip-strikethrough-links",
    is_flag=True,
    help="Do not recurse into links that are struck through in the HTML.",
)
def convert(
    url: str,
    output_dir: str,
    recursive: bool,
    max_depth: int,
    single_file: bool,
    skip_strikethrough_links: bool,
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

    if single_file or recursive:
        if single_file and os.path.exists(output_path):
            click.echo(f"Warning: {output_path} already exists.", err=True)
            if not click.confirm(f"Overwrite {output_path}?", default=False):
                click.echo("Aborted by user.", err=True)
                return
        traverse_and_write(
            page_id=page_id,
            url=url,
            output_dir=output_dir,
            max_depth=max_depth,
            single_file=single_file,
            output_path=output_path if single_file else None,
            skip_strikethrough_links=skip_strikethrough_links,
        )
        if single_file:
            click.echo(f"Saved: {output_path}")
        click.echo(f"URL: {url}")
        click.echo(f"Output Directory: {output_dir}")
        click.echo(f"Recursive: {recursive}")
        click.echo(f"Max Depth: {max_depth}")
        return

    # Default: single page, not recursive, not single-file
    html = page.get("body", {}).get("storage", {}).get("value", "")
    markdown = convert_html_to_markdown(html)
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
