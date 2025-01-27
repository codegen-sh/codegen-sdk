import logging
import os
from functools import cached_property
from typing import override

from codeowners import CodeOwners as CodeOwnersParser
from git import GitCommandError, Remote
from git.remote import PushInfoList

from codegen.git.clients.git_repo_client import GitRepoClient
from codegen.git.repo_operator.repo_operator import RepoOperator
from codegen.git.schemas.enums import CheckoutResult, FetchResult, SetupOption
from codegen.git.schemas.github import GithubScope, GithubType
from codegen.git.schemas.repo_config import RepoConfig
from codegen.git.utils.clone import clone_or_pull_repo, clone_repo, pull_repo
from codegen.git.utils.clone_url import get_clone_url_for_repo_config, url_to_github
from codegen.git.utils.codeowner_utils import create_codeowners_parser_for_repo
from codegen.git.utils.remote_progress import CustomRemoteProgress
from codegen.shared.performance.stopwatch_utils import stopwatch

logger = logging.getLogger(__name__)


class RemoteRepoOperator(RepoOperator):
    """A wrapper around GitPython to make it easier to interact with a cloned lowside repo."""

    # __init__ attributes
    repo_config: RepoConfig
    base_dir: str
    github_type: GithubType

    # lazy attributes
    _remote_git_repo: GitRepoClient | None = None
    _codeowners_parser: CodeOwnersParser | None = None
    _default_branch: str | None = None

    # TODO: allow setting the access scope level of the lowside repo (currently it's always WRITE)
    def __init__(
        self,
        repo_config: RepoConfig,
        base_dir: str = "/tmp",
        setup_option: SetupOption = SetupOption.PULL_OR_CLONE,
        shallow: bool = True,
        github_type: GithubType = GithubType.GithubEnterprise,
        bot_commit: bool = True,
    ) -> None:
        super().__init__(repo_config=repo_config, base_dir=base_dir, bot_commit=bot_commit)
        self.github_type = github_type
        self.setup_repo_dir(setup_option=setup_option, shallow=shallow)

    ####################################################################################################################
    # PROPERTIES
    ####################################################################################################################

    @property
    def remote_git_repo(self) -> GitRepoClient:
        if not self._remote_git_repo:
            self._remote_git_repo = GitRepoClient(self.repo_config, github_type=self.github_type, access_scope=GithubScope.WRITE)
        return self._remote_git_repo

    @property
    def default_branch(self) -> str:
        if self._default_branch is None:
            self._default_branch = self.remote_git_repo.default_branch
        return self._default_branch

    @property
    def codeowners_parser(self) -> CodeOwnersParser | None:
        if not self._codeowners_parser:
            self._codeowners_parser = create_codeowners_parser_for_repo(self.remote_git_repo)
        return self._codeowners_parser

    ####################################################################################################################
    # SET UP
    ####################################################################################################################

    @override
    def pull_repo(self) -> None:
        """Pull the latest commit down to an existing local repo"""
        pull_repo(repo=self.repo_config, path=self.base_dir, github_type=self.github_type)

    def clone_repo(self, shallow: bool = True) -> None:
        clone_repo(repo=self.repo_config, path=self.base_dir, shallow=shallow, github_type=self.github_type)

    def clone_or_pull_repo(self, shallow: bool = True) -> None:
        """If repo exists, pulls changes. otherwise, clones the repo."""
        # TODO(CG-7804): if repo is not valid we should delete it and re-clone. maybe we can create a pull_repo util + use the existing clone_repo util
        if self.repo_exists():
            self.clean_repo()
        clone_or_pull_repo(self.repo_config, path=self.base_dir, shallow=shallow, github_type=self.github_type)

    def setup_repo_dir(self, setup_option: SetupOption = SetupOption.PULL_OR_CLONE, shallow: bool = True) -> None:
        os.makedirs(self.base_dir, exist_ok=True)
        os.chdir(self.base_dir)
        if setup_option is SetupOption.CLONE:
            # if repo exists delete, then clone, else clone
            clone_repo(shallow=shallow)
        elif setup_option is SetupOption.PULL_OR_CLONE:
            # if repo exists, pull changes, else clone
            self.clone_or_pull_repo(shallow=shallow)
        elif setup_option is SetupOption.SKIP:
            if not self.repo_exists():
                logger.warning(f"Valid git repo does not exist at {self.repo_path}. Cannot skip setup with SetupOption.SKIP.")
        os.chdir(self.repo_path)

    ####################################################################################################################
    # CHECKOUT, BRANCHES & COMMITS
    ####################################################################################################################

    def fetch_remote(self, remote_name: str = "origin", refspec: str | None = None, force: bool = True) -> FetchResult:
        """Fetches and updates a ref from a remote repository.

        Args:
            remote_name (str): Name of the remote to fetch from. Defaults to "origin".
            refspec (str | None): The refspec to fetch. If None, fetches all refs. Defaults to None.
            force (bool): If True, forces the fetch operation. Defaults to True.

        Returns:
            FetchResult: An enum indicating the result of the fetch operation.
                - SUCCESS: Fetch was successful.
                - REFSPEC_NOT_FOUND: The specified refspec doesn't exist in the remote.

        Raises:
            GitCommandError: If the fetch operation fails for reasons other than a missing refspec.

        Note:
            This force fetches by default b/c by default we prefer the remote branch over our local branch.
        """
        logger.info(f"Fetching {remote_name} with refspec {refspec}")
        progress = CustomRemoteProgress()

        try:
            self.git_cli.remotes[remote_name].fetch(refspec=refspec, force=force, progress=progress, no_tags=True)
            return FetchResult.SUCCESS
        except GitCommandError as e:
            if progress.fetch_result == FetchResult.REFSPEC_NOT_FOUND:
                return FetchResult.REFSPEC_NOT_FOUND
            else:
                raise e

    @stopwatch
    def checkout_remote_branch(self, branch_name: str | None = None, remote_name: str = "origin") -> CheckoutResult:
        """Checks out a branch from a Remote + tracks the Remote.
        If the branch_name is already checked out, does nothing
        """
        return self.checkout_branch(branch_name, remote_name=remote_name, remote=True, create_if_missing=False)

    @stopwatch
    def push_changes(self, remote: Remote | None = None, refspec: str | None = None, force: bool = False) -> PushInfoList:
        """Push the changes to the given refspec of the remote.

        Args:
            refspec (str | None): refspec to push. If None, the current active branch is used.
            remote (Remote | None): Remote to push too. Defaults to 'origin'.
            force (bool): If True, force push the changes. Defaults to False.
        """
        # Use default remote if not provided
        if not remote:
            remote = self.git_cli.remote(name="origin")

        # Use the current active branch if no branch is specified
        if not refspec:
            # TODO: doesn't work with detached HEAD state
            refspec = self.git_cli.active_branch.name

        res = remote.push(refspec=refspec, force=force, progress=CustomRemoteProgress())
        for push_info in res:
            if push_info.flags & push_info.ERROR:
                # Handle the error case
                logger.warning(f"Error pushing {refspec}: {push_info.summary}")
            elif push_info.flags & push_info.FAST_FORWARD:
                # Successful fast-forward push
                logger.info(f"{refspec} pushed successfully (fast-forward).")
            elif push_info.flags & push_info.NEW_HEAD:
                # Successful push of a new branch
                logger.info(f"{refspec} pushed successfully as a new branch.")
            elif push_info.flags & push_info.NEW_TAG:
                # Successful push of a new tag (if relevant)
                logger.info("New tag pushed successfully.")
            else:
                # Successful push, general case
                logger.info(f"{refspec} pushed successfully.")
        return res

    @cached_property
    def base_url(self) -> str | None:
        repo_config = self.repo_config
        clone_url = get_clone_url_for_repo_config(repo_config, github_type=GithubType.Github)
        branch = self.get_active_branch_or_commit()
        return url_to_github(clone_url, branch)
