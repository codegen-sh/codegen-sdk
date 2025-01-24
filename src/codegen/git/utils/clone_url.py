from urllib.parse import urlparse

from codegen.git.configs.token import get_token_for_repo_config
from codegen.git.schemas.github import GithubType
from codegen.git.schemas.repo_config import RepoConfig


def url_to_github(url: str, branch: str) -> str:
    clone_url = url.removesuffix(".git").replace("git@github.com:", "github.com/")
    return f"{clone_url}/blob/{branch}"


def get_clone_url_for_repo_config(repo_config: RepoConfig, github_type: GithubType = GithubType.GithubEnterprise) -> str:
    github_url = f"github.com/{repo_config.full_name}.git"
    ghe_url = f"github.codegen.app/{repo_config.full_name}.git"
    if github_type is GithubType.GithubEnterprise:
        return ghe_url
    elif github_type is GithubType.Github:
        return github_url


def get_authenticated_clone_url_for_repo_config(
    repo: RepoConfig,
    github_type: GithubType = GithubType.GithubEnterprise,
) -> str:
    git_url = get_clone_url_for_repo_config(repo, github_type)
    token = get_token_for_repo_config(repo_config=repo, github_type=github_type)
    return f"https://x-access-token:{token}@{git_url}"


def add_token_to_clone_url(clone_url: str, token: str) -> str:
    parsed_clone_url = urlparse(clone_url)
    return f"{parsed_clone_url.scheme}://x-access-token:{token}@{parsed_clone_url.netloc}{parsed_clone_url.path}"
