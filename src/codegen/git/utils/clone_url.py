from urllib.parse import urlparse

from codegen.git.configs.token import get_token_for_repo_config
from codegen.git.schemas.github import GithubType
from codegen.git.schemas.repo_config import RepoConfig


# TODO: move out doesn't belong here
def url_to_github(url: str, branch: str) -> str:
    clone_url = url.removesuffix(".git").replace("git@github.com:", "github.com/")
    return f"{clone_url}/blob/{branch}"


def get_clone_url_for_repo_config(repo_config: RepoConfig, github_type: GithubType = GithubType.GithubEnterprise) -> str:
    if github_type is GithubType.GithubEnterprise:
        return f"https://github.codegen.app/{repo_config.full_name}.git"
    elif github_type is GithubType.Github:
        return f"https://github.com/{repo_config.full_name}.git"


def get_authenticated_clone_url_for_repo_config(
    repo: RepoConfig,
    github_type: GithubType = GithubType.GithubEnterprise,
) -> str:
    git_url = get_clone_url_for_repo_config(repo, github_type)
    token = get_token_for_repo_config(repo_config=repo, github_type=github_type)
    return add_access_token_to_url(git_url, token)


def add_access_token_to_url(url: str, token: str | None) -> str:
    parsed_url = urlparse(url)
    scheme = parsed_url.scheme or "https"
    token_prefix = f"x-access-token:{token}@" if token else ""
    return f"{scheme}://{token_prefix}{parsed_url.netloc}{parsed_url.path}"
