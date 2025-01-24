import logging
import os
import subprocess

from codegen.git.schemas.github import GithubType
from codegen.git.schemas.repo_config import RepoConfig
from codegen.git.utils.clone_url import get_authenticated_clone_url_for_repo_config
from codegen.shared.performance.stopwatch_utils import subprocess_with_stopwatch

logger = logging.getLogger(__name__)


def _get_path_to_repo(
    repo: RepoConfig,
    path: str,
    github_type: GithubType = GithubType.GithubEnterprise,
) -> tuple[str, str]:
    authenticated_git_url = get_authenticated_clone_url_for_repo_config(repo=repo, github_type=github_type)
    repo_name = repo.name
    return os.path.join(path, repo_name), authenticated_git_url


# TODO: update to use GitPython instead + move into LocalRepoOperator
def clone_repo(
    repo: RepoConfig,
    path: str,
    shallow: bool = True,
    github_type: GithubType = GithubType.GithubEnterprise,
):
    """TODO: re-use this code in clone_or_pull_repo. create separate pull_repo util"""
    path_to_repo, authenticated_git_url = _get_path_to_repo(repo=repo, path=path, github_type=github_type)

    if os.path.exists(path_to_repo) and os.listdir(path_to_repo):
        # NOTE: if someone calls the current working directory is the repo directory then we need to move up one level
        if os.getcwd() == os.path.realpath(path_to_repo):
            repo_parent_dir = os.path.dirname(path_to_repo)
            os.chdir(repo_parent_dir)
        delete_command = f"rm -rf {path_to_repo}"
        logger.info(f"Deleting existing clone with command: {delete_command}")
        subprocess.run(delete_command, shell=True, capture_output=True)

    if shallow:
        clone_command = f"""git clone --depth 1 {authenticated_git_url} {path_to_repo}"""
    else:
        clone_command = f"""git clone {authenticated_git_url} {path_to_repo}"""
    logger.info(f"Cloning with command: {clone_command} ...")
    subprocess_with_stopwatch(clone_command, shell=True, capture_output=True)
    # TODO: if an error raise or return None rather than silently failing
    return path_to_repo


# TODO: update to use GitPython instead + move into LocalRepoOperator
def clone_or_pull_repo(
    repo: RepoConfig,
    path: str,
    shallow: bool = True,
    github_type: GithubType = GithubType.GithubEnterprise,
):
    path_to_repo, authenticated_git_url = _get_path_to_repo(repo=repo, path=path, github_type=github_type)

    if os.path.exists(path_to_repo) and os.listdir(path_to_repo):
        logger.info(f"{path_to_repo} directory already exists. Pulling instead of cloning ...")
        pull_repo(repo=repo, path=path, github_type=github_type)
    else:
        logger.info(f"{path_to_repo} directory does not exist running git clone ...")
        if shallow:
            clone_command = f"""git clone --depth 1 {authenticated_git_url} {path_to_repo}"""
        else:
            clone_command = f"""git clone {authenticated_git_url} {path_to_repo}"""
        logger.info(f"Cloning with command: {clone_command} ...")
        subprocess_with_stopwatch(command=clone_command, command_desc=f"clone {repo.name}", shell=True, capture_output=True)
    return path_to_repo


# TODO: update to use GitPython instead + move into LocalRepoOperators
def pull_repo(
    repo: RepoConfig,
    path: str,
    github_type: GithubType = GithubType.GithubEnterprise,
) -> None:
    path_to_repo, authenticated_git_url = _get_path_to_repo(repo=repo, path=path, github_type=github_type)
    if not os.path.exists(path_to_repo):
        logger.info(f"{path_to_repo} directory does not exist. Unable to git pull.")
        return

    logger.info(f"Refreshing token for repo: {repo.full_name} ...")
    subprocess.run(f"git -C {path_to_repo} remote set-url origin {authenticated_git_url}", shell=True, capture_output=True)

    pull_command = f"git -C {path_to_repo} pull {authenticated_git_url}"
    logger.info(f"Pulling with command: {pull_command} ...")
    subprocess_with_stopwatch(command=pull_command, command_desc=f"pull {repo.name}", shell=True, capture_output=True)
