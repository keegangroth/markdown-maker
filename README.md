# Markdown Maker

Project to make markdown files out of confluence pages or google docs
to make them easier to provide to AI as context.

### Development

Used copilot to generate all the code and nearly all the commits.

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
