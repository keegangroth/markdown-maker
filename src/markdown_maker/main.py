"""Main entry point for the Markdown Maker CLI."""

import click


@click.group()
def cli() -> None:
    """A CLI tool to convert Confluence pages to Markdown."""
    pass


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
    click.echo(f"URL: {url}")
    click.echo(f"Output Directory: {output_dir}")
    click.echo(f"Recursive: {recursive}")


if __name__ == "__main__":
    cli()
