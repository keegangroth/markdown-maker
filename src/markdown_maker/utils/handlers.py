import os
from collections.abc import Callable

from markdown_maker.converters.html_to_markdown import write_markdown_page
from markdown_maker.utils.helpers import sanitize_dirname


def make_handle_page_single(output_path: str) -> Callable:
    """Return a handler for single-file markdown output."""
    first_page = [True]

    def handle_page(title: str, page_url: str, markdown: str, depth: int, parent_dir: str | None) -> str:
        with open(output_path, "a", encoding="utf-8") as f:
            write_markdown_page(f, title, page_url, markdown, is_first=first_page[0])
        first_page[0] = False
        return ""

    return handle_page


def make_handle_page_multi(output_dir: str) -> Callable:
    """Return a handler for multi-file markdown output."""

    def handle_page(title: str, page_url: str, markdown: str, depth: int, parent_dir: str | None) -> str:
        dir_name = sanitize_dirname(title)
        page_dir = os.path.join(parent_dir, dir_name) if parent_dir else os.path.join(output_dir, dir_name)
        os.makedirs(page_dir, exist_ok=True)
        out_path = os.path.join(page_dir, "index.md")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(markdown)
        return page_dir

    return handle_page
