GitHub Copilot Instructions for This Python Project

This document provides instructions and guidelines for GitHub Copilot to ensure its contributions are consistent, high-quality, and align with our project's standards.
Core Principles

    Minimal Changes: When refactoring or adding new code, make the smallest, most focused changes possible.
    Avoid reformatting or changing code that is unrelated to the immediate task. Make code precise, modular, and testable.
    Don’t break existing functionality.

    Ask Coder: If I need to do anything (e.g. Supabase/AWS config), tell me clearly. If anything is unclear, ask for clarification before starting.

    Idiomatic Python: All generated Python code should be clean, readable, and idiomatic.

    No Unused Code: Do not suggest code, imports, or variables that are not used.

    Added libraries: Do not suggest adding new libraries unless absolutely necessary. If a library is needed, explain why it is required and how it will be used. Add it to the `pyproject.toml` file and use that to install it.

1. Code Style and Formatting

    PEP 8 Compliance: All Python code MUST strictly follow the PEP 8 style guide. Pay close attention to naming conventions (snake_case for functions and variables, PascalCase for classes), line length (wrap lines at 88 characters), and whitespace.

    Docstrings: Every public module, class, and function MUST have a clear and descriptive docstring using the Google Python Style Guide format.

        Example:

        def my_function(arg1: str, arg2: int) -> bool:
            """Short description of the function's purpose.

            Args:
                arg1: Description of the first argument.
                arg2: Description of the second argument.

            Returns:
                A boolean indicating success or failure.
            """
            # function body

    Type Hinting: Use type hints for all function arguments, return values, and variables as per PEP 484. This is mandatory.

    F-strings: Use f-strings for all string formatting. Avoid using + concatenation or .format().

    Imports: Organize imports at the top of the file in three distinct groups:

        Standard library imports (e.g., os, sys).

        Third-party library imports (e.g., requests, pandas).

        Local application/library specific imports.
        Within each group, imports should be sorted alphabetically.

2. Linting and Static Analysis

    Linter: We use ruff for high-performance linting. All code should be free of ruff errors before being committed.

    Auto-formatting: Code should be formatted using ruff format. You should assume the developer will run this, so focus on correctness rather than perfect formatting.

    Configuration: The linter is configured in the pyproject.toml file. Adhere to the rules defined there.

3. Unit Testing

    Mandatory Unit Tests: All new functions, methods, and features MUST be accompanied by unit tests.

    Testing Framework: We use the pytest framework for testing. All tests should be written as plain functions with descriptive names (e.g., test_user_can_be_created_successfully).

    Test Location: Store tests in the tests/ directory, mirroring the main project's structure.

    Assertion Style: Use simple assert statements. Do not use unittest.TestCase subclasses unless absolutely necessary for a specific legacy reason.

    Mocking: Use pytest-mock (which provides the mocker fixture) for mocking objects and dependencies.

    Coverage: Aim for high test coverage for any new code you write. Test edge cases, happy paths, and expected failures.

4. Error Handling and Logic

    Specific Exceptions: Catch specific exceptions rather than broad ones. For example, use except ValueError: instead of a bare except:.

    Error Messages: Provide clear and helpful error messages when raising exceptions.

    Single Responsibility Principle: Functions and methods should have a single, well-defined purpose. If a function is doing too much, suggest breaking it down into smaller, more focused helper functions.

    Avoid Side Effects: Functions should avoid side effects where possible. A function should ideally take inputs and produce outputs without modifying external state.

5. Security

    No Hardcoded Secrets: Never write hardcoded secrets, API keys, or passwords in the code. Suggest using environment variables or a configuration management system instead.

    Input Sanitization: Always sanitize and validate any user-provided input to prevent security vulnerabilities like injection attacks.

Summary for Copilot

Before providing a suggestion, review these rules:

    Is it a minimal, focused change?

    Is the code free of linting errors?

    Does it have a corresponding unit test?

    Does it follow PEP 8 and our project's docstring/type-hinting standards?

    Is it secure and does it handle errors gracefully?