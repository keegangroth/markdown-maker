# MVP Build Plan: Markdown Maker

This document outlines the step-by-step tasks required to build the MVP of the "Markdown Maker" CLI tool.

## Phase 1: Project Setup & Foundation

- [x] 1.1. Create the initial directory structure as defined in `ARCHITECTURE.md`.
    - `src/markdown_maker/`
    - `src/markdown_maker/clients/`
    - `src/markdown_maker/converters/`
    - `src/markdown_maker/utils/`
    - `tests/`
    - `config/`
- [x] 1.2. Create empty `__init__.py` files in all `src` subdirectories to make them Python packages.
- [x] 1.3. Create the main entry point file `src/markdown_maker/main.py`.
- [x] 1.4. Create a `pyproject.toml` file to define project metadata and dependencies (`click`, `requests`, `PyYAML`, `beautifulsoup4`, `markdownify`, `pytest`, `pytest-mock`, `ruff`).
- [x] 1.6. Create a `.gitignore` file and add `__pycache__/`, `.pytest_cache/`, `*.egg-info/`, `dist/`, `build/`, and importantly, `.secrets.yml`.
- [x] 1.7. Create a basic `README.md` with a project title and a brief description. Add a section for setup instructions.

## Phase 2: Configuration Management

- [x] 2.1. Create `config/config.yml.example` with placeholder non-secret configuration (e.g., `confluence_base_url`).
- [x] 2.2. Create `config/.secrets.yml.example` with placeholder secrets (e.g., `confluence_username`, `confluence_api_token`).
- [x] 2.3. Implement a configuration loader in `src/markdown_maker/utils/config.py`.
    - It should load settings from a `config.yml` and `.secrets.yml`.
    - It should handle missing files gracefully.
    - It should raise a clear error if required secrets are missing.
- [x] 2.4. Add unit tests for the configuration loader.

## Phase 3: Core CLI Implementation

- [x] 3.1. In `src/markdown_maker/main.py`, set up the main CLI group using `click`.
- [x] 3.2. Implement the `convert` command within `main.py`.
- [x] 3.3. Add the following options to the `convert` command:
    - `--url` (required, string)
    - `--output-dir` (optional, string, defaults to current directory)
    - `--recursive` (optional, boolean flag)
- [x] 3.4. Implement the basic logic for the `convert` command to print the received options.
- [x] 3.5. Add a `--help` menu and ensure it displays correctly.

## Phase 4: Confluence API Client

- [x] 4.1. Create `src/markdown_maker/clients/confluence_client.py`.
- [x] 4.2. Implement a `ConfluenceClient` class in this file using the `atlassian-python-api` package for all Confluence API interactions.
- [x] 4.3. The `ConfluenceClient` constructor should take the base URL and authentication credentials from the config, and initialize the `atlassian.Confluence` client.
- [x] 4.4. Implement a method `get_page_content(page_id: str) -> dict` that fetches a page's content from the Confluence REST API using the `atlassian-python-api` client.
- [x] 4.5. Implement a method `get_child_pages(page_id: str) -> list` that fetches the direct child pages of a given page.
- [x] 4.6. Implement a utility in `src/markdown_maker/utils/helpers.py` to extract the `page_id` from a Confluence URL.
- [x] 4.7. Check for robust error handling for API requests (e.g., 404 Not Found, 401 Unauthorized). `atlassian-python-api` raises HTTPError which do not need to be modified.
- [x] 4.8. Review unit tests to ensure they cover all scenarios

## Phase 5: HTML to Markdown Conversion

- [x] 5.1. Create `src/markdown_maker/converters/html_to_markdown.py` and implement a function `convert_html_to_markdown(html: str) -> str` that uses `markdownify` and `BeautifulSoup` to perform the conversion.
- [x] 5.2. The function should be configured to handle basic formatting (headings, lists, bold, italics, code blocks).
- [x] 5.3. Add unit tests for the conversion function with sample HTML snippets.

## Phase 6: Single-Page Conversion Logic

- [x] 6.1. In `src/markdown_maker/main.py`, integrate the `ConfluenceClient` and `html_to_markdown` converter into the `convert` command.
- [x] 6.2. When the command is run (without `--recursive`):
    - Extract `page_id` from the `--url`.
    - Use `ConfluenceClient` to fetch the page content (HTML).
    - Use the converter to transform the HTML to Markdown.
    - Sanitize the page title to create a valid filename (e.g., "My Page" -> `my_page.md`).
    - Save the Markdown content to a file in the specified `--output-dir`.
- [x] 6.3. Implement logic to create the output directory if it doesn't exist.
- [x] 6.4. Add end-to-end tests for the single-page conversion flow.

## Phase 7: Recursive Conversion Logic

- [x] 7.1. In `src/markdown_maker/main.py`, add the logic to handle the `--recursive` flag.
- [x] 7.2. Implement a recursive function that:
    - Takes a `page_id` and a base output path.
    - Fetches the page, converts it, and saves it.
    - Calls `get_child_pages` to find child pages.
    - For each child page, creates a subdirectory named after the parent page's title.
    - Recursively calls itself for each child page, passing the new output path.
    - When recursing to embedded Confluence links, mirror the directory structure of the page where the link was found (do not attempt to mirror the full Confluence hierarchy).
- [x] 7.3. Implement a `--max-depth` CLI option (default: 3):
    - Add a `--max-depth` option to the CLI to limit recursion depth during conversion.
    - Ensure the default value is 3.
    - Enforce this limit in both child page and embedded link recursion to prevent extremely large conversions.
    - Implemented: CLI now accepts --max-depth, default is 3, and recursion is limited accordingly. Tests added for option and enforcement.
- [x] 7.4. Change recursive output to nested directories by page title:
    - Each page should be saved as `index.md` inside a directory named after the sanitized page title.
    - Child pages should be subdirectories within their parent’s directory, each with their own `index.md`.
    - Ensure directory names are sanitized and unique.
    - Update tests to verify the new output structure.
- [x] 7.5. Implement recursion into embedded Confluence links:
    - For each page, find any embedded Confluence links within the page content (e.g., links to other Confluence pages embedded in the body).
    - Recursively convert and save those linked pages as well, using the same output structure as the page where the link was found.
    - Recursion into embedded links must respect the `--max-depth` limit.
    - Avoid redundant downloads and conversions: do not fetch or convert the same page more than once per run.
- [x] 7.6. Log error messages for any pages that cannot be accessed (due to any errors) instead of raising exceptions. The process should continue converting all accessible pages, skipping those with errors.

## Phase 8: Single File Output Option

- [ ] 8.1. Add a CLI option to download all discovered pages (from recursive or single-page conversion) into a single Markdown file instead of separate files.
    - When this option is enabled, concatenate the Markdown content of all pages in the order they are discovered.
    - Insert clear page breaks or headings between each page's content, including the page title and source URL.
    - Ensure this option works with both single-page and recursive conversions.
    - Add tests to verify correct concatenation, ordering, and formatting of the combined Markdown file.
- [ ] 8.2. Add an option to break the single Markdown file output into sections by recursive depth.
    - Each section should correspond to a depth level in the page hierarchy.
    - Insert a clear heading or divider for each depth level.
    - The least deep pages should be first in the document.
    - Ensure this works for both single-page and recursive conversions.
    - Add tests to verify correct sectioning and formatting by depth.
- [ ] 8.3. Add an option to output each depth level into a separate Markdown file instead of a single file.
    - Each file should contain all pages at a given depth in the hierarchy.
    - Name files clearly by depth (e.g., depth_1.md, depth_2.md, etc.).
    - Ensure this works for both single-page and recursive conversions.
    - Add tests to verify correct file creation and content by depth.

## Phase 9: Final Touches

- [ ] 9.1. Implement relative link rewriting. After all pages are converted, iterate through the generated Markdown files and replace Confluence URL links with relative links to the corresponding local files (for both child and embedded pages).
- [ ] 9.2. Add end-to-end tests for the recursive conversion.
- [ ] 9.3. Implement progress indication for conversions taking longer than 15 seconds (e.g., a simple "Converting page X...")
- [ ] 9.4. Review all error handling and ensure messages are user-friendly.
- [ ] 9.5. Update the `README.md` with final usage instructions and examples.
- [ ] 9.6. Manually test the CLI in a real-world scenario.
- [ ] 9.7. Add an option to automatically zip all produced Markdown files (single or multiple) into a single archive for easy sharing after conversion is complete.
    - The zip file should include all generated Markdown files and preserve directory structure.
    - Ensure this works for both single-file and multi-file output modes.
    - Add tests to verify correct zipping and archive contents.
