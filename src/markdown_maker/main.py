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


@cli.command()
@click.option("--url", required=True, help="The URL of the Confluence page to convert.")
@click.option(
    "--output-dir",
    default=".",
    help="The directory to save the Markdown file.",
    type=click.Path(file_okay=False, dir_okay=True, writable=True, resolve_path=True),
)
@click.option("--recursive", is_flag=True, help="Recursively convert child pages.")
def convert(url: str, output_dir: str, recursive: bool) -> None:
    """Converts a Confluence page to a Markdown file."""
    page_id = extract_page_id_from_url(url)
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


if __name__ == "__main__":
    cli()
