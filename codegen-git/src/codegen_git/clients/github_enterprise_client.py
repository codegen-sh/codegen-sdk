from codegen_git.clients.github_client import GithubClient
from codegen_git.configs.config import config
from codegen_git.schemas.github import GithubType


class GithubEnterpriseClient(GithubClient):
    """Manages interaction with GitHub Enterprise"""

    type = GithubType.GithubEnterprise
    base_url = config.GITHUB_ENTERPRISE_URL
