import logging
from enum import StrEnum

from git.remote import Remote

from codegen.git.configs.constants import HIGHSIDE_REMOTE_NAME
from codegen.git.repo_operator.remote_repo_operator import RemoteRepoOperator
from codegen.git.schemas.enums import FetchResult
from codegen.git.schemas.github import GithubType
from codegen.git.utils.clone_url import get_authenticated_clone_url_for_repo_config
from codegen.shared.performance.stopwatch_utils import stopwatch

logger = logging.getLogger(__name__)


class BranchSyncResult(StrEnum):
    SUCCESS = "SUCCESS"
    BRANCH_NOT_FOUND = "BRANCH_NOT_FOUND"
    SKIP = "SKIP"


def get_highside_origin(op: RemoteRepoOperator) -> Remote:
    remote_url = get_authenticated_clone_url_for_repo_config(op.repo_config, github_type=GithubType.Github)

    if HIGHSIDE_REMOTE_NAME in op.git_cli.remotes:
        highside_origin = op.git_cli.remote(HIGHSIDE_REMOTE_NAME)
        highside_origin.set_url(remote_url)
    else:
        highside_origin = op.git_cli.create_remote(HIGHSIDE_REMOTE_NAME, remote_url)
    return highside_origin


@stopwatch
def fetch_highside_branch(op: RemoteRepoOperator, branch_name: str) -> FetchResult:
    """Checks out a a branch from highside origin"""
    # Step 1: create highside origin
    remote_url = get_authenticated_clone_url_for_repo_config(repo=op.repo_config, github_type=GithubType.Github)
    op.create_remote(HIGHSIDE_REMOTE_NAME, remote_url)

    # Step 2: fetch the branch from highside
    res = op.fetch_remote(HIGHSIDE_REMOTE_NAME, refspec=branch_name)
    if res == FetchResult.REFSPEC_NOT_FOUND:
        logger.warning(f"Branch: {branch_name} not found in highside. Skipping fetch.")
        return FetchResult.REFSPEC_NOT_FOUND

    # Step 3: checkout (or update existing) local branch that tracks highside remote
    if op.is_branch_checked_out(branch_name):
        # update currently checked out branch to match the latest highside branch
        op.git_cli.git.reset("--hard", f"{HIGHSIDE_REMOTE_NAME}/{branch_name}")
    else:
        # create a new local branch that tracks the remote highside branch
        op.git_cli.create_head(branch_name, commit=f"{HIGHSIDE_REMOTE_NAME}/{branch_name}", force=True)
    return FetchResult.SUCCESS
