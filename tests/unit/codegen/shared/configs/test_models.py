import json
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest
import toml

from codegen.shared.configs.models.feature_flags import CodebaseFeatureFlags, Config, FeatureFlagsConfig, RepositoryConfig


@pytest.fixture
def sample_config():
    codebase_flags = CodebaseFeatureFlags(debug=True, verify_graph=False)
    return Config(repository=RepositoryConfig(organization_name="test-org", repo_name="test-repo"), feature_flags=FeatureFlagsConfig(codebase=codebase_flags))


def test_config_initialization():
    config = Config()
    assert config.repository is not None
    assert config.feature_flags is not None
    assert config.secrets is not None


def test_config_with_values():
    config = Config(repository={"organization_name": "test-org", "repo_name": "test-repo"})
    assert config.repository.organization_name == "test-org"
    assert config.repository.repo_name == "test-repo"


@patch("builtins.open", new_callable=mock_open)
@patch("pathlib.Path.mkdir")
def test_save_config(mock_mkdir, mock_file, sample_config):
    sample_config.save(Path("test_config.toml"))

    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
    mock_file.assert_called_once_with(Path("test_config.toml"), "w")

    # Verify the content being written
    written_data = mock_file().write.call_args[0][0]
    parsed_data = toml.loads(written_data)
    assert parsed_data["repository"]["organization_name"] == "test-org"


def test_get_config_value(sample_config):
    # Test getting a simple value
    assert json.loads(sample_config.get("repository.organization_name")) == "test-org"

    # Test getting a nested value
    assert json.loads(sample_config.get("feature_flags.codebase.debug")) is True

    # Test getting non-existent value
    assert sample_config.get("invalid.path") is None


def test_set_config_value(sample_config):
    # Instead of mocking save, we'll mock the open function used within save
    with patch("builtins.open", new_callable=mock_open) as mock_file:
        # Test setting a simple string value
        sample_config.set("repository.organization_name", "new-org")
        assert sample_config.repository.organization_name == "new-org"

        # Test setting a boolean value
        sample_config.set("feature_flags.codebase.debug", "false")
        assert not sample_config.feature_flags.codebase.debug

        # Verify save was called by checking if open was called
        assert mock_file.called


def test_set_config_invalid_path(sample_config):
    with pytest.raises(KeyError, match="Invalid configuration path: invalid.path"):
        sample_config.set("invalid.path", "value")


def test_set_config_invalid_json(sample_config):
    with pytest.raises(ValueError, match="Value must be a valid JSON object"):
        sample_config.set("repository", "invalid json {")


def test_config_str_representation(sample_config):
    config_str = str(sample_config)
    assert isinstance(config_str, str)
    # Verify it's valid JSON
    parsed = json.loads(config_str)
    assert parsed["repository"]["organization_name"] == "test-org"


def test_set_config_new_override_key(sample_config):
    with patch("builtins.open", new_callable=mock_open) as mock_file:
        # Test setting a new import resolution override
        sample_config.set("feature_flags.codebase.import_resolution_overrides", '{"new_key": "new_value"}')

        # Verify the new key was added
        assert sample_config.feature_flags.codebase.import_resolution_overrides["new_key"] == "new_value"

        # Verify save was called
        assert mock_file.called

        # Test adding another key to the existing overrides
        sample_config.set("feature_flags.codebase.import_resolution_overrides", '{"new_key": "new_value", "another_key": "another_value"}')

        # Verify both keys exist
        overrides = sample_config.feature_flags.codebase.import_resolution_overrides
        assert overrides["new_key"] == "new_value"
        assert overrides["another_key"] == "another_value"
