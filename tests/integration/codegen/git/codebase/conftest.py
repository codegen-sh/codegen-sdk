import os

import pytest
from git import Repo as GitRepo

from codegen.git.repo_operator.local_repo_operator import LocalRepoOperator
from codegen.git.schemas.repo_config import RepoConfig
from codegen.git.utils.clone_url import get_authenticated_clone_url_for_repo_config
from codegen.sdk.codebase.config import ProjectConfig
from codegen.sdk.core.codebase import Codebase
from codegen.shared.configs.session_configs import config


@pytest.fixture
def repo_config(tmpdir):
    repo_config = RepoConfig(
        name="Kevin-s-Adventure-Game",
        full_name="codegen-sh/Kevin-s-Adventure-Game",
        base_dir=str(tmpdir),
    )
    yield repo_config


@pytest.fixture
def op(repo_config):
    os.chdir(repo_config.base_dir)
    GitRepo.clone_from(url=get_authenticated_clone_url_for_repo_config(repo_config, token=config.secrets.github_token), to_path=os.path.join(repo_config.base_dir, repo_config.name), depth=1)
    op = LocalRepoOperator(repo_config=repo_config)
    yield op


@pytest.fixture
def codebase(op: LocalRepoOperator):
    project_config = ProjectConfig(repo_operator=op)
    codebase = Codebase(projects=[project_config])
    yield codebase
