from pathlib import Path
from unittest.mock import patch

import pytest
import tomllib

from codegen.shared.configs.constants import CONFIG_PATH
from codegen.shared.configs.models.feature_flags import CodebaseFeatureFlags, FeatureFlagsConfig
from codegen.shared.configs.models.secrets import SecretsConfig
from codegen.shared.configs.models.session import SessionConfig
from codegen.shared.configs.session_configs import _load_from_env, _load_from_toml, _merge_configs, load_session_config


# Test _merge_configs
def test_merge_configs_basic():
    base = {"a": 1, "b": 2}
    override = {"b": 3, "c": 4}
    result = _merge_configs(base, override)
    assert result == {"a": 1, "b": 3, "c": 4}


def test_merge_configs_nested():
    base = {"feature_flags": {"codebase": {"debug": False, "typescript": {"ts_dependency_manager": False}}}}
    override = {"feature_flags": {"codebase": {"debug": True, "typescript": {"ts_language_engine": True}}}}
    result = _merge_configs(base, override)
    assert result == {"feature_flags": {"codebase": {"debug": True, "typescript": {"ts_dependency_manager": False, "ts_language_engine": True}}}}


def test_merge_configs_none_values():
    base = {"secrets": {"github_token": "token1"}}
    override = {"secrets": {"github_token": None}}
    result = _merge_configs(base, override)
    assert result == {"secrets": {"github_token": "token1"}}


def test_merge_configs_empty_string():
    base = {"repository": {"full_name": "org1/test-repo"}}
    override = {"repository": {"full_name": ""}}
    result = _merge_configs(base, override)
    assert result == {"repository": {"full_name": "org1/test-repo"}}


# Test _load_from_toml
def test_load_from_toml_existing_file(temp_config_file):
    config = _load_from_toml(temp_config_file)
    assert isinstance(config, SessionConfig)
    assert config.secrets.github_token == "gh_token123"
    assert config.repository.repo_name == "test-repo"
    assert config.feature_flags.codebase.debug is True
    assert config.feature_flags.codebase.typescript.ts_dependency_manager is True
    assert config.feature_flags.codebase.import_resolution_overrides == {"@org/pkg": "./local/path"}


@patch.dict("os.environ", {})
@patch("codegen.shared.configs.models.SecretsConfig.model_config", {"env_file": "nonexistent.env"})
def test_load_from_toml_nonexistent_file():
    config = _load_from_toml(Path("nonexistent.toml"))
    assert isinstance(config, SessionConfig)
    assert config.secrets.github_token is None
    assert config.repository.full_name is None
    assert config.feature_flags.codebase.debug is None


# Test _load_from_env
@patch.dict("os.environ", {"CODEGEN_SECRETS__GITHUB_TOKEN": "env_token", "CODEGEN_SECRETS__OPENAI_API_KEY": "env_key"})
def test_load_from_env():
    config = _load_from_env(CONFIG_PATH)
    assert isinstance(config, SessionConfig)
    assert config.secrets.github_token == "env_token"
    assert config.secrets.openai_api_key == "env_key"


# Test load function
@patch.dict("os.environ", {}, clear=True)  # Clear all env vars for this test
@patch("codegen.shared.configs.config._load_from_env")
@patch("codegen.shared.configs.config._load_from_toml")
@patch("codegen.shared.configs.models.SecretsConfig.model_config", {"env_file": None, "env_prefix": "CODEGEN_SECRETS__"})
def test_load_with_both_configs(mock_toml, mock_env):
    # Setup mock returns
    mock_env.return_value = Config(secrets=SecretsConfig(github_token="env_token"), feature_flags=FeatureFlagsConfig(codebase=CodebaseFeatureFlags(debug=True)))
    mock_toml.return_value = Config(secrets={"openai_api_key": "openai_key"}, repository={"full_name": "codegen-org/test-repo"})

    config = load_session_config(CONFIG_PATH)

    assert isinstance(config, SessionConfig)
    assert config.secrets.github_token == "env_token"
    assert config.secrets.openai_api_key == "openai_key"
    assert config.repository.full_name == "codegen-org/test-repo"
    assert config.feature_flags.codebase.debug is True


@patch("codegen.shared.configs.config._load_from_env")
@patch("codegen.shared.configs.config._load_from_toml")
def test_load_with_custom_path(mock_toml, mock_env):
    custom_path = Path("custom/config.toml")
    load_session_config(config_path=custom_path)

    mock_toml.assert_called_once_with(custom_path)
    mock_env.assert_called_once()


# Error cases
def test_load_from_toml_invalid_file(invalid_toml_file):
    with pytest.raises(tomllib.TOMLDecodeError):
        _load_from_toml(invalid_toml_file)
