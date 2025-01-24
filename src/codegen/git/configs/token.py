import logging

from codegen.git.configs.config import config
from codegen.git.schemas.github import GithubType

logger = logging.getLogger(__name__)


def get_token_for_repo_config(github_type: GithubType = GithubType.GithubEnterprise) -> str:
    # TODO: implement config such that we can retrieve tokens for different repos
    if github_type == GithubType.GithubEnterprise:
        return config.LOWSIDE_TOKEN
    elif github_type == GithubType.Github:
        return config.HIGHSIDE_TOKEN
