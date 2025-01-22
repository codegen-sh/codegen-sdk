from unittest.mock import MagicMock, patch

import pytest

from codegen_git.schemas.repo_config import RepoConfig


@pytest.fixture(autouse=True)
def mock_config():
    """Mock Config instance to prevent actual environment variable access during tests."""
    mock_config = MagicMock()
    mock_config.ENV = "test"
    mock_config.GITHUB_ENTERPRISE_URL = "https://github.test"
    mock_config.LOWSIDE_TOKEN = "test-lowside-token"
    mock_config.HIGHSIDE_TOKEN = "test-highside-token"

    yield mock_config


@pytest.fixture(autouse=True)
def repo_config() -> RepoConfig:
    with patch("codegen_git.utils.clone.get_authenticated_clone_url_for_repo_config") as mock_clone_url:
        mock_clone_url.return_value = "https://github.com/codegen-sh/Kevin-s-Adventure-Game.git"
        repo_config = RepoConfig(id=321, name="Kevin-s-Adventure-Game", full_name="codegen-sh/Kevin-s-Adventure-Game", organization_id="123", organization_name="codegen-sh")
        yield repo_config
