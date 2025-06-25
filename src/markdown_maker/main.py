"""Main entry point for the Markdown Maker CLI."""


import click

from markdown_maker.clients.confluence_client import ConfluenceClient
from markdown_maker.clients.confluence_tree_traverser import ConfluenceTreeTraverser
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

def handle_recursive_conversion(
    page_id: str,
    output_dir: str,
    max_depth: int,
    current_depth: int = 1,
    visited: set | None = None,
    parent_context: str = "",
) -> None:
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
    traverser = ConfluenceTreeTraverser(
        client=client,
        max_depth=max_depth,
        handle_page=handle_page,
        parent_context=parent_context,
        parent_dir=None,
    )
    traverser.traverse(
        pid=page_id,
        page_url=f"https://company.atlassian.net/wiki/pages/viewpage.action?pageId={page_id}",
        current_depth=current_depth,
    )

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
    client = ConfluenceClient()
    first_page = True if is_first else False
    def handle_page(title: str, url: str, markdown: str, depth: int, parent_dir: str | None) -> str:
        nonlocal first_page
        write_markdown_page(f, title, url, markdown, is_first=first_page)
        first_page = False
        return ""
    traverser = ConfluenceTreeTraverser(
        client=client,
        max_depth=max_depth,
        handle_page=handle_page,
        parent_context=parent_context,
    )
    traverser.traverse(
        pid=pid,
        page_url=page_url,
        current_depth=current_depth,
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
