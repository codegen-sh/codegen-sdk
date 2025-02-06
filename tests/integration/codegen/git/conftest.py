from unittest.mock import MagicMock

import pytest

from codegen.git.schemas.repo_config import RepoConfig


@pytest.fixture(autouse=True)
def mock_config():
    """Mock Config instance to prevent actual environment variable access during tests."""
    mock_config = MagicMock()
    mock_config.GITHUB_TOKEN = "test-highside-token"

    yield mock_config


@pytest.fixture(autouse=True)
def repo_config():
    repo_config = RepoConfig(
        id=321,
        name="Kevin-s-Adventure-Game",
        full_name="codegen-sh/Kevin-s-Adventure-Game",
        organization_id=123,
        organization_name="codegen-sh",
    )
    yield repo_config
