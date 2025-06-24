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
- [ ] 4.7. Add robust error handling for API requests (e.g., 404 Not Found, 401 Unauthorized).
- [ ] 4.8. Add unit tests for the `ConfluenceClient` using `pytest-mock` to mock `requests`.

## Phase 5: HTML to Markdown Conversion

- [ ] 5.1. Create `src/markdown_maker/converters/html_to_markdown.py`.
- [ ] 5.2. Implement a function `convert_html_to_markdown(html: str) -> str` that uses `markdownify` and `BeautifulSoup` to perform the conversion.
- [ ] 5.3. The function should be configured to handle basic formatting (headings, lists, bold, italics, code blocks).
- [ ] 5.4. Add unit tests for the conversion function with sample HTML snippets.

## Phase 6: Single-Page Conversion Logic

- [ ] 6.1. In `src/markdown_maker/main.py`, integrate the `ConfluenceClient` and `html_to_markdown` converter into the `convert` command.
- [ ] 6.2. When the command is run (without `--recursive`):
    - Extract `page_id` from the `--url`.
    - Use `ConfluenceClient` to fetch the page content (HTML).
    - Use the converter to transform the HTML to Markdown.
    - Sanitize the page title to create a valid filename (e.g., "My Page" -> `my_page.md`).
    - Save the Markdown content to a file in the specified `--output-dir`.
- [ ] 6.3. Implement logic to create the output directory if it doesn't exist.
- [ ] 6.4. Add end-to-end tests for the single-page conversion flow.

## Phase 7: Recursive Conversion Logic

- [ ] 7.1. In `src/markdown_maker/main.py`, add the logic to handle the `--recursive` flag.
- [ ] 7.2. Implement a recursive function that:
    - Takes a `page_id` and a base output path.
    - Fetches the page, converts it, and saves it.
    - Calls `get_child_pages` to find child pages.
    - For each child page, creates a subdirectory named after the parent page's title.
    - Recursively calls itself for each child page, passing the new output path.
- [ ] 7.3. Implement relative link rewriting. After all pages are converted, iterate through the generated Markdown files and replace Confluence URL links with relative links to the corresponding local files.
- [ ] 7.4. Add warning messages for pages that cannot be accessed due to permissions, without stopping the entire process.
- [ ] 7.5. Add end-to-end tests for the recursive conversion.

## Phase 8: Final Touches

- [ ] 8.1. Implement progress indication for conversions taking longer than 15 seconds (e.g., a simple "Converting page X...")
- [ ] 8.2. Review all error handling and ensure messages are user-friendly.
- [ ] 8.3. Update the `README.md` with final usage instructions and examples.
- [ ] 8.4. Manually test the CLI in a real-world scenario.
