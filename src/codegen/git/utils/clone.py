import logging
import os
import subprocess

from codegen.shared.performance.stopwatch_utils import subprocess_with_stopwatch

logger = logging.getLogger(__name__)


# TODO: update to use GitPython instead + move into LocalRepoOperator
def clone_repo(
    repo_path: str,
    clone_url: str,
    shallow: bool = True,
):
    """TODO: re-use this code in clone_or_pull_repo. create separate pull_repo util"""
    if os.path.exists(repo_path) and os.listdir(repo_path):
        # NOTE: if someone calls the current working directory is the repo directory then we need to move up one level
        if os.getcwd() == os.path.realpath(repo_path):
            repo_parent_dir = os.path.dirname(repo_path)
            os.chdir(repo_parent_dir)
        delete_command = f"rm -rf {repo_path}"
        logger.info(f"Deleting existing clone with command: {delete_command}")
        subprocess.run(delete_command, shell=True, capture_output=True)

    if shallow:
        clone_command = f"""git clone --depth 1 {clone_url} {repo_path}"""
    else:
        clone_command = f"""git clone {clone_url} {repo_path}"""
    logger.info(f"Cloning with command: {clone_command} ...")
    subprocess_with_stopwatch(clone_command, shell=True, capture_output=True)
    # TODO: if an error raise or return None rather than silently failing
    return repo_path


# TODO: update to use GitPython instead + move into LocalRepoOperator
def clone_or_pull_repo(
    repo_path: str,
    clone_url: str,
    shallow: bool = True,
):
    if os.path.exists(repo_path) and os.listdir(repo_path):
        logger.info(f"{repo_path} directory already exists. Pulling instead of cloning ...")
        pull_repo(clone_url=clone_url, repo_path=repo_path)
    else:
        logger.info(f"{repo_path} directory does not exist running git clone ...")
        if shallow:
            clone_command = f"""git clone --depth 1 {clone_url} {repo_path}"""
        else:
            clone_command = f"""git clone {clone_url} {repo_path}"""
        logger.info(f"Cloning with command: {clone_command} ...")
        subprocess_with_stopwatch(command=clone_command, command_desc=f"clone {repo_path}", shell=True, capture_output=True)
    return repo_path


# TODO: update to use GitPython instead + move into LocalRepoOperators
def pull_repo(
    repo_path: str,
    clone_url: str,
) -> None:
    if not os.path.exists(repo_path):
        logger.info(f"{repo_path} directory does not exist. Unable to git pull.")
        return

    logger.info(f"Refreshing token for repo at {repo_path} ...")
    subprocess.run(f"git -C {repo_path} remote set-url origin {clone_url}", shell=True, capture_output=True)

    pull_command = f"git -C {repo_path} pull {clone_url}"
    logger.info(f"Pulling with command: {pull_command} ...")
    subprocess_with_stopwatch(command=pull_command, command_desc=f"pull {repo_path}", shell=True, capture_output=True)
