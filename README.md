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

## Running Tests

To run the unit tests, use `pytest`:

```bash
pytest
```

## Linting

This project uses `ruff` for linting and formatting. To check for linting errors, run:

```bash
ruff check .
```

To automatically fix formatting issues, run:

```bash
ruff format .
```


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
