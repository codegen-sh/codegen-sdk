from unittest.mock import patch

import pytest

from tests.shared.configs.sample_config import SAMPLE_CONFIG_DICT, SAMPLE_TOML


@pytest.fixture
def sample_toml():
    """Return sample TOML configuration string."""
    return SAMPLE_TOML


@pytest.fixture
def sample_config_dict():
    """Return sample configuration dictionary."""
    return SAMPLE_CONFIG_DICT


@pytest.fixture
def temp_config_file(tmp_path):
    """Create a temporary config file with sample TOML content."""
    config_file = tmp_path / "config.toml"
    config_file.write_text(SAMPLE_TOML)
    return config_file


@pytest.fixture
def invalid_toml_file(tmp_path):
    """Create a temporary file with invalid TOML content."""
    invalid_toml = tmp_path / "invalid.toml"
    invalid_toml.write_text("invalid = toml [ content")
    return invalid_toml


@pytest.fixture
def clean_env():
    """Temporarily clear environment variables and override env file path."""
    with patch.dict("os.environ", {}, clear=True):
        with patch("codegen.shared.configs.models.Config.model_config", {"env_file": "nonexistent.env"}):
            with patch("codegen.shared.configs.models.SecretsConfig.model_config", {"env_file": "nonexistent.env"}):
                yield
