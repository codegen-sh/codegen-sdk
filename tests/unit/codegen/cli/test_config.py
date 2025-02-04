import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from codegen.cli.config import CLIUserConfigs


@pytest.fixture(autouse=True)
def mock_input():
    with patch("codegen.cli.config.input") as mock_input:
        yield mock_input


@pytest.fixture(autouse=True)
def mock_config_file():
    with tempfile.NamedTemporaryFile() as temp_file:
        path = Path(temp_file.name)
        with patch("codegen.cli.config.CONFIG_PATH", path):
            yield path


@pytest.fixture(autouse=True)
def mock_cli_user_configs():
    # Disables conftest config mock by replacing it
    CLIUserConfigs.load.cache_clear()
    yield


def test_default_anon_session_id():
    config = CLIUserConfigs()
    assert isinstance(config.anon_session_id, str)
    assert len(config.anon_session_id) > 0


def test_default_is_metrics_enabled(mock_input):
    mock_input.return_value = "y"
    config = CLIUserConfigs()
    assert config.is_metrics_enabled is True


def test_is_metrics_enabled_prompt(mock_input):
    mock_input.return_value = "n"
    config = CLIUserConfigs(is_metrics_enabled=None)
    assert config.is_metrics_enabled is False


def test_is_metrics_enabled_invalid_input(mock_input):
    mock_input.return_value = "invalid"
    config = CLIUserConfigs(is_metrics_enabled=None)
    assert config.is_metrics_enabled is False


def test_save_changes(mock_config_file):
    config = CLIUserConfigs()
    config.save()
    with mock_config_file.open("r") as f:
        contents = f.read()

    assert contents.strip()
    config_contents = json.loads(contents)
    assert config_contents["anon_session_id"] == config.anon_session_id
    assert config_contents["is_metrics_enabled"] == config.is_metrics_enabled


def test_load_config_file_does_not_exist(mock_config_file):
    mock_config_file.unlink()
    config = CLIUserConfigs.load()
    assert isinstance(config, CLIUserConfigs)


def test_load_config_file_exists(mock_config_file):
    with mock_config_file.open("w") as f:
        f.write('{"anon_session_id": "test-id", "is_metrics_enabled": true}')

    config = CLIUserConfigs.load()
    assert config.anon_session_id == "test-id"
    assert config.is_metrics_enabled is True
