"""Configuration loader for Markdown Maker.

This module provides a function to load configuration from YAML files.
It merges settings from a primary config file and a secrets file,
ensuring that the application has access to all necessary parameters.

Functions:
    load_config: Loads and merges configurations from specified files.
"""

from pathlib import Path
from typing import Any

import yaml


def load_config() -> dict[str, Any]:
    """Loads and merges configuration from YAML files.

    This function loads settings from `config.yml` and `.secrets.yml`
    located in the `config` directory at the project root. It merges
    them, with secrets taking precedence.

    It handles missing configuration files gracefully but will raise an
    error if the secrets file or essential keys within it are missing.

    Returns:
        A dictionary containing the merged configuration settings.

    Raises:
        FileNotFoundError: If `.secrets.yml` cannot be found.
        ValueError: If required secret keys are missing from the config.
    """
    # Assume the script is in src/markdown_maker/utils
    # Project root is four levels up
    # TODO: user should optionally be able to specify the config path
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    config_dir = project_root / "config"

    config_path = config_dir / "config.yml"
    secrets_path = config_dir / ".secrets.yml"

    config: dict[str, Any] = {}

    if config_path.exists():
        with open(config_path) as f:
            config.update(yaml.safe_load(f) or {})

    if not secrets_path.exists():
        raise FileNotFoundError(
            f"Secrets file not found at {secrets_path}. "
            "Please create it by copying `.secrets.yml.example`."
        )

    with open(secrets_path) as f:
        config.update(yaml.safe_load(f) or {})

    required_secrets = ["confluence_username", "confluence_api_token"]
    missing_secrets = [key for key in required_secrets if key not in config]

    if missing_secrets:
        raise ValueError(f"Missing required secrets: {', '.join(missing_secrets)}")

    return config
