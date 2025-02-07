import socket
from collections.abc import Generator
from contextlib import closing
from unittest.mock import Mock

import pytest

from codegen.git.clients.git_repo_client import GitRepoClient
from codegen.git.configs.config import config
from codegen.git.repo_operator.remote_repo_operator import RemoteRepoOperator
from codegen.git.schemas.repo_config import RepoConfig
from codegen.runner.clients.sandbox_client import SandboxClient


@pytest.fixture
def get_free_port():
    """Find and return a free port on localhost"""
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        s.listen(1)
        port = s.getsockname()[1]
        return port


@pytest.fixture(autouse=True)
def repo_config() -> RepoConfig:
    yield RepoConfig(
        id=321,
        name="Kevin-s-Adventure-Game",
        full_name="codegen-sh/Kevin-s-Adventure-Game",
        organization_id=123,
        organization_name="codegen-sh",
        language="PYTHON",
    )


@pytest.fixture(autouse=True)
def op(repo_config: RepoConfig) -> Generator[RemoteRepoOperator, None, None]:
    yield RemoteRepoOperator(repo_config=repo_config, access_token=config.GITHUB_TOKEN)


@pytest.fixture(autouse=True)
def git_repo_client(repo_config: RepoConfig) -> GitRepoClient:
    yield GitRepoClient(repo_config=repo_config, access_token=config.GITHUB_TOKEN)


@pytest.fixture(autouse=True)
def sandbox_client(repo_config: RepoConfig, get_free_port, tmpdir) -> Generator[SandboxClient, None, None]:
    # Use the pre-determined free port and a temporary directory
    repo_config.base_dir = str(tmpdir)
    sb_client = SandboxClient(repo_config=repo_config, port=get_free_port, git_access_token=config.GITHUB_TOKEN)
    sb_client.runner = Mock()
    yield sb_client
