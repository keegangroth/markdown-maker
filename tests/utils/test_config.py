"""Unit tests for the configuration loader."""

import os
from unittest.mock import mock_open, patch

import pytest

from markdown_maker.utils.config import load_config

# Sample valid config.yml content
SAMPLE_CONFIG_YAML = """
confluence_base_url: "https://example.atlassian.net/wiki"
project_key: "TEST"
"""

# Sample valid .secrets.yml content
SAMPLE_SECRETS_YAML = """
confluence_username: "user@example.com"
confluence_api_token: "your_api_token"
"""

# Sample secrets file missing a required key
SAMPLE_INCOMPLETE_SECRETS_YAML = """
confluence_username: "user@example.com"
"""


@patch("pathlib.Path.exists")
@patch("builtins.open")
def test_load_config_success(mock_open_func, mock_exists):
    """Tests successful loading of both config and secrets files."""
    # Both files exist
    mock_exists.return_value = True

    # Mock the content of the two files
    mock_open_func.side_effect = [
        mock_open(read_data=SAMPLE_CONFIG_YAML).return_value,
        mock_open(read_data=SAMPLE_SECRETS_YAML).return_value,
    ]

    config = load_config()

    assert config["confluence_base_url"] == "https://example.atlassian.net/wiki"
    assert config["confluence_username"] == "user@example.com"
    assert config["confluence_api_token"] == "your_api_token"
    assert mock_open_func.call_count == 2


@patch("pathlib.Path.exists")
@patch("builtins.open")
def test_load_config_missing_secrets_file_raises_error(mock_open_func, mock_exists):
    """Tests that a FileNotFoundError is raised if .secrets.yml is missing."""
    # Simulate config.yml existing, but .secrets.yml missing
    mock_exists.side_effect = [True, False]
    mock_open_func.return_value = mock_open(read_data=SAMPLE_CONFIG_YAML).return_value

    with pytest.raises(FileNotFoundError) as excinfo:
        load_config()
    assert "Secrets file not found" in str(excinfo.value)


@patch("pathlib.Path.exists")
@patch("builtins.open")
def test_load_config_missing_config_file_success(mock_open_func, mock_exists):
    """Tests that loading succeeds if only .secrets.yml exists."""
    # Simulate .secrets.yml existing, but config.yml missing
    mock_exists.side_effect = [False, True]

    # Mock the content of the secrets file
    mock_open_func.return_value = mock_open(read_data=SAMPLE_SECRETS_YAML).return_value

    config = load_config()

    assert "confluence_base_url" not in config  # It was in the other file
    assert config["confluence_username"] == "user@example.com"
    assert config["confluence_api_token"] == "your_api_token"


@patch("pathlib.Path.exists")
@patch("builtins.open")
def test_load_config_missing_required_secret_raises_error(mock_open_func, mock_exists):
    """Tests that a ValueError is raised if a required secret is missing."""
    # Both files exist
    mock_exists.return_value = True

    # Mock the content of the two files, but secrets is incomplete
    mock_open_func.side_effect = [
        mock_open(read_data=SAMPLE_CONFIG_YAML).return_value,
        mock_open(read_data=SAMPLE_INCOMPLETE_SECRETS_YAML).return_value,
    ]

    with pytest.raises(ValueError) as excinfo:
        load_config()

    # The implementation hardcodes the required secrets, so we check for one of them
    assert "Missing required secrets: confluence_api_token" in str(excinfo.value)


@patch("pathlib.Path.exists")
@patch("builtins.open")
def test_load_config_honors_environment_variable(mock_open_func, mock_exists):
    """Tests that the config path can be overridden by an environment variable."""
    mock_exists.return_value = True
    mock_open_func.side_effect = [
        mock_open(read_data=SAMPLE_CONFIG_YAML).return_value,
        mock_open(read_data=SAMPLE_SECRETS_YAML).return_value,
    ]

    custom_path = "/test/config/dir"

    with patch.dict(os.environ, {"MARKDOWN_MAKER_CONFIG_DIR": custom_path}):
        config = load_config()

    assert config["confluence_username"] == "user@example.com"

    # Verify that the correct paths were used for opening files
    call_args = mock_open_func.call_args_list
    assert len(call_args) == 2
    assert str(call_args[0].args[0]) == os.path.join(custom_path, "config.yml")
    assert str(call_args[1].args[0]) == os.path.join(custom_path, ".secrets.yml")
