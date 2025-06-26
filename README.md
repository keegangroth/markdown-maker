# Markdown Maker

Project to make markdown files out of confluence pages or google docs
to make them easier to provide to AI as context.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd markdown-maker
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install the project in editable mode:**
    ```bash
    pip install -e ".[dev]"
    ```

## Usage

### Basic Single Page Conversion

Convert a single Confluence page to Markdown:

```bash
python3 src/markdown_maker/main.py convert --url "https://company.atlassian.net/wiki/pages/viewpage.action?pageId=123456" --output-dir ./output
```

- `--url`: The Confluence page URL to convert (required).
- `--output-dir`: Directory to save the Markdown file (default: current directory).

### Recursive Conversion

Recursively convert a page and all its child pages (up to a depth of 3 by default):

```bash
python3 src/markdown_maker/main.py convert --url "https://company.atlassian.net/wiki/pages/viewpage.action?pageId=123456" --recursive --output-dir ./output
```

- `--recursive`: Recursively convert child pages.
- `--max-depth`: Maximum recursion depth (default: 3).

### Single File Output

Concatenate all discovered pages into a single Markdown file:

```bash
python3 src/markdown_maker/main.py convert --url "https://company.atlassian.net/wiki/pages/viewpage.action?pageId=123456" --recursive --single-file --output-dir ./output
```

- `--single-file`: Output all pages into a single Markdown file (named after the root page).

### Additional Options

- `--skip-strikethrough-links`: Do not recurse into links that are struck through in the HTML.


## Configuration

Before running the CLI, copy the example config files and fill in your Confluence details:

```bash
cp config/config.yml.example config/config.yml
cp config/.secrets.yml.example config/.secrets.yml
```

- Edit `config/config.yml` to set your Confluence base URL and other non-secret settings.
- Edit `config/.secrets.yml` to add your Confluence username (usually your email address) and API token.
    - You can generate a Confluence API token by visiting [https://id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens) while logged into your Atlassian account.

**Never commit your real secrets file to version control.**


## Development

Used copilot to generate all the code and nearly all the commits.

Copilot instructions can be found in the `.github` directory. The
`task`, `test`, and `commit` prompts were used for almost all
development. These prompts were also intially crafted by copilot, but
heavily manually modified to get the desired behaviors. Copilot still
ignored explicit instructions from them in many cases, although this
seemed to happen less in "new" chat windows.

The `commit` task was also intended to capture prompts from copilot
chat into commit messages for later reference, but this functionality
was extremely hit or miss. This command worked the best when
interactions were limited.

The `docs/ai/tasks.md` file captures the "tasks" to be done. This was
also primarily generated and modified by prompting copilot, either to
add new items or to rearrange items. The `task` prompt then worked
form this file. Only a few pieces of functionality were added by
other/custom prompts.

Implementation was left almost entirely up to copilot initially. No
meaningful manual review was done. This lead to a situation where the
code needed a fairly significant refactor after copilot became stuck
trying to implement something that wasn't from the original task
list. Copilot was somewhat helpful in refactoring things, but usually
needed fairly explicit direction.

### Running Tests

To run the unit tests, use `pytest`:

```bash
pytest
```

### Linting

This project uses `ruff` for linting and formatting. To check for linting errors, run:

```bash
ruff check .
```

To automatically fix formatting issues, run:

```bash
ruff format .
```
