import logging
import os
from functools import cached_property
from typing import Self, override

from codeowners import CodeOwners as CodeOwnersParser
from git import Remote
from git import Repo as GitCLI
from git.remote import PushInfoList
from github import Github
from github.PullRequest import PullRequest

from codegen.git.clients.git_repo_client import GitRepoClient
from codegen.git.repo_operator.repo_operator import RepoOperator
from codegen.git.schemas.enums import FetchResult
from codegen.git.schemas.github import GithubType
from codegen.git.schemas.repo_config import BaseRepoConfig
from codegen.git.utils.clone_url import url_to_github
from codegen.git.utils.file_utils import create_files

logger = logging.getLogger(__name__)

class OperatorIsLocal(Exception):
    """Error raised while trying to do a remote operation on a local operator"""


class LocalRepoOperator(RepoOperator):
    """RepoOperator that does not depend on remote Github.
    It is useful for:
    - Testing codemods locally with a repo already cloned from Github on disk.
    - Creating "fake" repos from a dictionary of files contents
    """

    _repo_path: str
    _repo_name: str
    _git_cli: GitCLI
    repo_config: BaseRepoConfig
    _github_api_key: str | None
    _remote_git_repo: GitRepoClient | None = None

    def __init__(
        self,
        repo_path: str,  # full path to the repo
        github_api_key: str | None = None,
        repo_config: BaseRepoConfig | None = None,
        bot_commit: bool = False,
    ) -> None:
        self._repo_path = repo_path
        self._repo_name = os.path.basename(repo_path)
        self._github_api_key = github_api_key
        self.github_type = GithubType.Github
        self._remote_git_repo = None
        os.makedirs(self.repo_path, exist_ok=True)
        GitCLI.init(self.repo_path)
        repo_config = repo_config or BaseRepoConfig()
        super().__init__(repo_config, self.repo_path, bot_commit)
    ####################################################################################################################
    # PROPERTIES
    ####################################################################################################################

    @property
    def remote_git_repo(self) -> GitRepoClient:
        if self._remote_git_repo is None:
            if not self._github_api_key:
                return None

            if not (base_url := self.base_url):
                msg = "Could not determine GitHub URL from remotes"
                raise ValueError(msg)

            # Extract owner and repo from the base URL
            # Format: https://github.com/owner/repo
            parts = base_url.split('/')
            if len(parts) < 2:
                msg = f"Invalid GitHub URL format: {base_url}"
                raise ValueError(msg)

            owner = parts[-4]
            repo = parts[-3]

            github = Github(self._github_api_key)
            self._remote_git_repo = github.get_repo(f"{owner}/{repo}")
        return self._remote_git_repo

    ####################################################################################################################
    # CLASS METHODS
    ####################################################################################################################
    @classmethod
    def create_from_files(cls, repo_path: str, files: dict[str, str], bot_commit: bool = True, repo_config: BaseRepoConfig = BaseRepoConfig()) -> "LocalRepoOperator":
        """Used when you want to create a directory from a set of files and then create a LocalRepoOperator that points to that directory.
        Use cases:
        - Unit testing
        - Playground
        - Codebase eval

        Args:
            repo_path (str): The path to the directory to create.
            files (dict[str, str]): A dictionary of file names and contents to create in the directory.
            repo_config (BaseRepoConfig): The configuration of the repo.
        """
        # Step 1: Create dir (if not exists) + files
        os.makedirs(repo_path, exist_ok=True)
        create_files(base_dir=repo_path, files=files)

        # Step 2: Init git repo
        op = cls(repo_path=repo_path, bot_commit=bot_commit, repo_config=repo_config)
        if op.stage_and_commit_all_changes("[Codegen] initial commit"):
            op.checkout_branch(None, create_if_missing=True)
        return op

    @classmethod
    def create_from_commit(cls, repo_path: str, commit: str, url: str, github_api_key: str | None = None) -> Self:
        """Do a shallow checkout of a particular commit to get a repository from a given remote URL.

        Args:
            repo_path (str): Path where the repo should be cloned
            commit (str): The commit hash to checkout
            url (str): Git URL of the repository
            github_api_key (str | None): Optional GitHub API key for operations that need GitHub access
        """
        op = cls(repo_path=repo_path, bot_commit=False, github_api_key=github_api_key)
        op.discard_changes()
        if op.get_active_branch_or_commit() != commit:
            op.create_remote("origin", url)
            op.git_cli.remotes["origin"].fetch(commit, depth=1)
            op.checkout_commit(commit)
        return op

    @classmethod
    def create_from_repo(cls, repo_path: str, url: str, github_api_key: str | None = None) -> Self:
        """Create a fresh clone of a repository or use existing one if up to date.

        Args:
            repo_path (str): Path where the repo should be cloned
            url (str): Git URL of the repository
            github_api_key (str | None): Optional GitHub API key for operations that need GitHub access
        """
        # Check if repo already exists
        if os.path.exists(repo_path):
            try:
                # Try to initialize git repo from existing path
                git_cli = GitCLI(repo_path)
                # Check if it has our remote URL
                if any(remote.url == url for remote in git_cli.remotes):
                    # Fetch to check for updates
                    git_cli.remotes.origin.fetch()
                    # Get current and remote HEADs
                    local_head = git_cli.head.commit
                    remote_head = git_cli.remotes.origin.refs[git_cli.active_branch.name].commit
                    # If up to date, use existing repo
                    if local_head.hexsha == remote_head.hexsha:
                        return cls(repo_path=repo_path, bot_commit=False, github_api_key=github_api_key)
            except Exception:
                # If any git operations fail, fallback to fresh clone
                pass

            # If we get here, repo exists but is not up to date or valid
            # Remove the existing directory to do a fresh clone
            import shutil

            shutil.rmtree(repo_path)

        # Clone the repository
        GitCLI.clone_from(url=url, to_path=repo_path, depth=1)

        # Initialize with the cloned repo
        git_cli = GitCLI(repo_path)

        return cls(repo_path=repo_path, bot_commit=False, github_api_key=github_api_key)

    ####################################################################################################################
    # PROPERTIES
    ####################################################################################################################

    @property
    def repo_name(self) -> str:
        return self._repo_name

    @property
    def repo_path(self) -> str:
        return self._repo_path

    @property
    def codeowners_parser(self) -> CodeOwnersParser | None:
        return None

    @cached_property
    def base_url(self) -> str | None:
        if remote := next(iter(self.git_cli.remotes), None):
            return url_to_github(remote.url, self.get_active_branch_or_commit())

    @override
    def push_changes(self, remote: Remote | None = None, refspec: str | None = None, force: bool = False) -> PushInfoList:
        raise OperatorIsLocal()

    @override
    def pull_repo(self) -> None:
        """Pull the latest commit down to an existing local repo"""
        raise OperatorIsLocal()

    def fetch_remote(self, remote_name: str = "origin", refspec: str | None = None, force: bool = True) -> FetchResult:
        raise OperatorIsLocal()


    def get_pull_request(self, pr_number: int) -> PullRequest | None:
        """Get a GitHub Pull Request object for the given PR number.

        Args:
            pr_number (int): The PR number to fetch

        Returns:
            PullRequest | None: The PyGitHub PullRequest object if found, None otherwise

        Note:
            This requires a GitHub API key to be set when creating the LocalRepoOperator
        """
        try:
            # Create GitHub client and get the PR
            repo = self.remote_git_repo
            if repo is None:
                logger.warning("GitHub API key is required to fetch pull requests")
                return None
            return repo.get_pull(pr_number)
        except Exception as e:
            logger.warning(f"Failed to get PR {pr_number}: {e!s}")
            return None
