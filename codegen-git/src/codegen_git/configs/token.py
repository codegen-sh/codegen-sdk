import logging

from codegen_git.configs.config import config
from codegen_git.schemas.github import GithubType
from codegen_git.schemas.repo_config import RepoConfig

logger = logging.getLogger(__name__)


def get_token_for_repo_config(repo_config: RepoConfig, github_type: GithubType = GithubType.GithubEnterprise) -> str:
    if github_type == GithubType.GithubEnterprise:
        return config.LOWSIDE_TOKEN
    elif github_type == GithubType.Github:
        return config.HIGHSIDE_TOKEN
