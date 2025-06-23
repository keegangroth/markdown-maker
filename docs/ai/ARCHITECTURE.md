# Architecture Specification

This document outlines the proposed architecture for the Markdown Maker project. The design emphasizes modularity, testability, and adherence to the project's coding standards.

## 1. File and Folder Structure

A standard source layout (`src`) will be used to separate the application code from project configuration files.

```
/
├── .gitignore
├── pyproject.toml
├── README.md
├── requirements.txt
├── config/
│   ├── config.yml.template
│   └── .secrets.yml.template
├── docs/
│   └── ai/
│       ├── ARCHITECTURE.md
│       └── SOFTWARE_REQUIREMENTS.md
├── src/
│   └── markdown_maker/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── config.py
│       ├── clients/
│       │   ├── __init__.py
│       │   └── confluence.py
│       └── converters/
│           ├── __init__.py
│           └── markdown.py
└── tests/
    ├── __init__.py
    ├── test_cli.py
    ├── clients/
    │   └── test_confluence.py
    └── converters/
        └── test_markdown.py
```

## 2. Component Breakdown

Each module and directory has a specific responsibility, promoting the Single Responsibility Principle.

*   **`pyproject.toml`**: Defines project metadata, dependencies, and tool configurations (like `ruff` and `pytest`). This is the modern standard for Python project configuration.
*   **`config/`**: This directory will hold templates for the configuration files. Users will copy these to the project root and fill them out.
    *   `config.yml.template`: A template for non-secret configuration, like default output directories or formatting options.
    *   `.secrets.yml.template`: A template for secret credentials.
*   **`src/markdown_maker/`**: The main application package.
    *   **`__main__.py`**: The main entry point for the application when run as a module (`python -m markdown_maker`). This keeps the top-level directory clean.
    *   **`cli.py`**: Defines the command-line interface using the `click` library. It will handle parsing arguments (`--url`, `--output-dir`, `--recursive`) and orchestrating the calls to the other components.
    *   **`config.py`**: Responsible for locating, loading, and validating the `config.yml` and `.secrets.yml` files. It will provide a unified, easy-to-use configuration object to the rest of the application.
    *   **`clients/confluence.py`**: Contains a `ConfluenceClient` class. This class encapsulates all interactions with the Confluence REST API: fetching a page, getting its children, and handling API-specific details like authentication and error codes.
    *   **`converters/markdown.py`**: Contains the core logic for converting Confluence's HTML export into clean Markdown. It will use libraries to parse the HTML, clean it, convert it to Markdown, and perform any required post-processing, like fixing internal links.
*   **`tests/`**: Contains all unit and integration tests. The structure mirrors the `src` directory to make tests easy to locate.

## 3. Python Libraries

The following third-party libraries are proposed to meet the project requirements efficiently. They will be listed in `requirements.txt` and `pyproject.toml`.

*   **`click`**: For building a clean, composable, and user-friendly command-line interface. It's generally preferred over the standard library's `argparse` for its ease of use and power.
*   **`requests`**: A robust and straightforward HTTP library for making API calls to the Confluence REST API.
*   **`PyYAML`**: For parsing the `config.yml` and `.secrets.yml` files.
*   **`beautifulsoup4`**: To parse the raw HTML content received from Confluence. This is essential for cleaning up the HTML before conversion and for finding child page links.
*   **`markdownify`**: A dedicated library for converting HTML into Markdown. This will handle the bulk of the conversion work for basic formatting.
*   **`pytest`**: The testing framework for writing and running our unit tests, as specified in the project instructions.
*   **`pytest-mock`**: Provides the `mocker` fixture for easily mocking objects and API calls during testing.
*   **`ruff`**: For high-performance linting and formatting, as specified in the project instructions.

This architecture provides a solid foundation for building the Markdown Maker. Before I proceed, do you have any questions or would you like to adjust any part of this plan?
