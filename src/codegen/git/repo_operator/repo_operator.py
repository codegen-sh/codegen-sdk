import fnmatch
import glob
import logging
import os
from abc import ABC, abstractmethod
from collections.abc import Generator
from datetime import UTC, datetime
from functools import cached_property
from time import perf_counter

from codeowners import CodeOwners as CodeOwnersParser
from git import Commit as GitCommit
from git import Diff, GitCommandError, InvalidGitRepositoryError, Remote
from git import Repo as GitCLI
from git.remote import PushInfoList

from codegen.git.clients.git_repo_client import GitRepoClient
from codegen.git.configs.constants import CODEGEN_BOT_EMAIL, CODEGEN_BOT_NAME
from codegen.git.schemas.enums import CheckoutResult, FetchResult
from codegen.git.schemas.repo_config import RepoConfig
from codegen.git.utils.remote_progress import CustomRemoteProgress
from codegen.shared.configs.session_configs import config
from codegen.shared.performance.stopwatch_utils import stopwatch
from codegen.shared.performance.time_utils import humanize_duration

logger = logging.getLogger(__name__)


class RepoOperator(ABC):
    """A wrapper around GitPython to make it easier to interact with a repo."""

    repo_config: RepoConfig
    base_dir: str
    bot_commit: bool = True
    access_token: str | None = None

    # lazy attributes
    _codeowners_parser: CodeOwnersParser | None = None
    _default_branch: str | None = None
    _remote_git_repo: GitRepoClient | None = None

    def __init__(
        self,
        repo_config: RepoConfig,
        access_token: str | None = None,
        bot_commit: bool = True,
    ) -> None:
        assert repo_config is not None
        self.repo_config = repo_config
        self.access_token = access_token or config.secrets.github_token
        self.base_dir = repo_config.base_dir
        self.bot_commit = bot_commit

    ####################################################################################################################
    # PROPERTIES
    ####################################################################################################################

    @property
    def repo_name(self) -> str:
        return self.repo_config.name

    @property
    def repo_path(self) -> str:
        return os.path.join(self.base_dir, self.repo_name)

    @property
    def remote_git_repo(self) -> GitRepoClient:
        if not self._remote_git_repo:
            self._remote_git_repo = GitRepoClient(self.repo_config, access_token=self.access_token)
        return self._remote_git_repo

    @property
    def clone_url(self) -> str:
        return f"https://github.com/{self.repo_config.full_name}.git"

    @property
    def viz_path(self) -> str:
        return os.path.join(self.base_dir, "codegen-graphviz")

    @property
    def viz_file_path(self) -> str:
        return os.path.join(self.viz_path, "graph.json")

    def _set_bot_email(self, git_cli: GitCLI) -> None:
        with git_cli.config_writer("repository") as writer:
            if not writer.has_section("user"):
                writer.add_section("user")
            writer.set("user", "email", CODEGEN_BOT_EMAIL)

    def _set_bot_username(self, git_cli: GitCLI) -> None:
        with git_cli.config_writer("repository") as writer:
            if not writer.has_section("user"):
                writer.add_section("user")
            writer.set("user", "name", CODEGEN_BOT_NAME)

    def _unset_bot_email(self, git_cli: GitCLI) -> None:
        with git_cli.config_writer("repository") as writer:
            if writer.has_option("user", "email"):
                writer.remove_option("user", "email")

    def _unset_bot_username(self, git_cli: GitCLI) -> None:
        with git_cli.config_writer("repository") as writer:
            if writer.has_option("user", "name"):
                writer.remove_option("user", "name")

    @cached_property
    def git_cli(self) -> GitCLI:
        git_cli = GitCLI(self.repo_path)
        username = None
        user_level = None
        email = None
        email_level = None
        levels = ["system", "global", "user", "repository"]
        for level in levels:
            with git_cli.config_reader(level) as reader:
                if reader.has_option("user", "name") and not username:
                    username = reader.get("user", "name")
                    user_level = level
                if reader.has_option("user", "email") and not email:
                    email = reader.get("user", "email")
                    email_level = level
        if self.bot_commit:
            self._set_bot_email(git_cli)
            self._set_bot_username(git_cli)
        else:
            # we need a username and email to commit, so if they're not set, set them to the bot's
            # Case 1: username is not set: set it to the bot's
            if not username:
                self._set_bot_username(git_cli)
            # Case 2: username is set to the bot's at the repo level, but something else is set at the user level: unset it
            elif username != CODEGEN_BOT_NAME and user_level != "repository":
                self._unset_bot_username(git_cli)
            # Case 3: username is only set at the repo level: do nothing
            else:
                pass  # no-op to make the logic clearer
            # Repeat for email
            if not email:
                self._set_bot_email(git_cli)

            elif email != CODEGEN_BOT_EMAIL and email_level != "repository":
                self._unset_bot_email(git_cli)
        return git_cli

    @property
    def head_commit(self) -> GitCommit:
        return self.git_cli.head.commit

    @property
    def git_diff(self) -> str:
        """Get the diff of the repo. Useful for checking if there are any changes."""
        return self.git_cli.git.diff()

    @property
    def default_branch(self) -> str:
        # Priority 1: If default branch has been set
        if self._default_branch:
            return self._default_branch

        # Priority 2: If origin/HEAD ref exists
        origin_prefix = "origin"
        if f"{origin_prefix}/HEAD" in self.git_cli.refs:
            return self.git_cli.refs[f"{origin_prefix}/HEAD"].reference.name.removeprefix(f"{origin_prefix}/")

        # Priority 3: Fallback to the active branch
        return self.git_cli.active_branch.name

    @abstractmethod
    def codeowners_parser(self) -> CodeOwnersParser | None: ...

    ####################################################################################################################
    # SET UP
    ####################################################################################################################

    def repo_exists(self) -> bool:
        if not os.path.exists(self.repo_path):
            return False
        try:
            _ = GitCLI(self.repo_path)
            return True
        except InvalidGitRepositoryError as e:
            return False

    def clean_repo(self) -> None:
        """Cleans the repo by:
        1. Discards any changes (tracked/untracked)
        2. Deletes all branches except the checked out branch
        3. Deletes all remotes except origin
        """
        logger.info(f"Cleaning repo at {self.repo_path} ...")
        self.discard_changes()
        self.clean_branches()
        self.clean_remotes()

    @stopwatch
    def discard_changes(self) -> None:
        """Cleans repo dir by discarding any changes in staging/working directory and removes untracked files/dirs. Use with .is_dirty()."""
        ts1 = perf_counter()
        self.git_cli.head.reset(index=True, working_tree=True)  # discard staged (aka index) + unstaged (aka working tree) changes in tracked files
        ts2 = perf_counter()
        self.git_cli.git.clean("-fdxq")  # removes untracked changes and ignored files
        ts3 = perf_counter()
        self.git_cli.git.gc("--auto")  # garbage collect
        ts4 = perf_counter()
        logger.info(f"discard_changes took {humanize_duration(ts2 - ts1)} to reset, {humanize_duration(ts3 - ts2)} to clean, {humanize_duration(ts4 - ts3)} to gc")

    @stopwatch
    def clean_remotes(self) -> None:
        for remote in self.git_cli.remotes:
            if remote.name == "origin":
                continue
            logger.info(f"Deleting remote {remote.name} ...")
            self.git_cli.delete_remote(remote)

    @stopwatch
    def clean_branches(self) -> None:
        for branch in self.git_cli.branches:
            if self.is_branch_checked_out(branch.name):
                continue
            logger.info(f"Deleting branch {branch.name} ...")
            self.git_cli.delete_head(branch.name, force=True)

    @abstractmethod
    def pull_repo(self) -> None:
        """Pull the latest commit down to an existing local repo"""

    ####################################################################################################################
    # CHECKOUT, BRANCHES & COMMITS
    ####################################################################################################################

    def safe_get_commit(self, commit: str) -> GitCommit | None:
        """Gets commit if it exists, else returns None"""
        try:
            return self.git_cli.commit(commit)
        except Exception as e:
            logger.warning(f"Failed to get commit {commit}:\n\t{e}")
            return None

    @abstractmethod
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

    def delete_remote(self, remote_name: str) -> None:
        remote = self.git_cli.remote(remote_name)
        if remote:
            self.git_cli.delete_remote(remote)

    def create_remote(self, remote_name: str, remote_url: str) -> None:
        """Creates a remote. Skips if the remote already exists."""
        if remote_name in self.git_cli.remotes:
            logger.warning(f"Remote with name {remote_name} already exists. Skipping create_remote.")
            return
        self.git_cli.create_remote(remote_name, url=remote_url)

    @stopwatch
    def checkout_commit(self, commit_hash: str | GitCommit, remote_name: str = "origin") -> CheckoutResult:
        """Checks out the relevant commit
        TODO: handle the environment being dirty
        """
        logger.info(f"Checking out commit: {commit_hash}")
        if not self.git_cli.is_valid_object(commit_hash, "commit"):
            self.fetch_remote(remote_name=remote_name, refspec=commit_hash)
            if not self.git_cli.is_valid_object(commit_hash, "commit"):
                return CheckoutResult.NOT_FOUND

        if self.git_cli.is_dirty():
            logger.info(f"Environment is dirty, discarding changes before checking out commit: {commit_hash}")
            self.discard_changes()

        self.git_cli.git.checkout(commit_hash)
        return CheckoutResult.SUCCESS

    def get_active_branch_or_commit(self) -> str:
        """Returns the current active branch, or commit hexsha if head is detached"""
        if self.git_cli.head.is_detached:
            return self.git_cli.head.commit.hexsha
        return self.git_cli.active_branch.name

    def is_branch_checked_out(self, branch_name: str) -> bool:
        if self.git_cli.head.is_detached:
            return False
        return self.git_cli.active_branch.name == branch_name

    def checkout_branch(self, branch_name: str | None, *, remote: bool = False, remote_name: str = "origin", create_if_missing: bool = True) -> CheckoutResult:
        """Attempts to check out the branch in the following order:
        - Check out the local branch by name
        - Check out the remote branch if it's been fetched
        - Creates a new branch from the current commit (with create=True)

        NOTE: if branch is already checked out this does nothing.
        TIP: Use remote=True if you want to always try to checkout the branch from a remote

        Args:
        ----
            branch_name (str): Name of the branch to checkout.
            create_if_missing: If the branch doesn't exist, create one
            remote: Checks out a branch from a Remote + tracks the Remote
            force (bool): If True, force checkout by resetting the current branch to HEAD.
                          If False, raise an error if the branch is dirty.

        Raises:
        ------
            GitCommandError: If there's an error with Git operations.
            RuntimeError: If the branch is dirty and force is not set.
        """
        if branch_name is None:
            branch_name = self.default_branch

        try:
            if self.is_branch_checked_out(branch_name):
                if remote:
                    # If the branch is already checked out and we want to fetch it from the remote, reset --hard to the remote branch
                    logger.info(f"Branch {branch_name} is already checked out locally. Resetting to remote branch: {remote_name}/{branch_name}")
                    # TODO: would have to fetch the the remote branch first to retrieve latest changes
                    self.git_cli.git.reset("--hard", f"{remote_name}/{branch_name}")
                    return CheckoutResult.SUCCESS
                else:
                    logger.info(f"Branch {branch_name} is already checked out! Skipping checkout_branch.")
                    return CheckoutResult.SUCCESS

            if self.git_cli.is_dirty():
                logger.info(f"Environment is dirty, discarding changes before checking out branch: {branch_name}.")
                self.discard_changes()

            # If remote=True, create a local branch tracking the remote branch and checkout onto it
            if remote:
                res = self.fetch_remote(remote_name, refspec=f"{branch_name}:{branch_name}")
                if res is FetchResult.SUCCESS:
                    self.git_cli.git.checkout(branch_name)
                    return CheckoutResult.SUCCESS
                if res is FetchResult.REFSPEC_NOT_FOUND:
                    logger.warning(f"Branch {branch_name} not found in remote {remote_name}. Unable to checkout remote branch.")
                    return CheckoutResult.NOT_FOUND

            # If the branch already exists, checkout onto it
            if branch_name in self.git_cli.heads:
                self.git_cli.heads[branch_name].checkout()
                return CheckoutResult.SUCCESS

            # If the branch does not exist and create_if_missing=True, create and checkout a new branch from the current commit
            elif create_if_missing:
                logger.info(f"Creating new branch {branch_name} from current commit: {self.git_cli.head.commit.hexsha}")
                new_branch = self.git_cli.create_head(branch_name)
                new_branch.checkout()
                return CheckoutResult.SUCCESS
            else:
                return CheckoutResult.NOT_FOUND

        except GitCommandError as e:
            if "fatal: ambiguous argument" in e.stderr:
                logger.warning(f"Branch {branch_name} was not found in remote {remote_name}. Unable to checkout.")
                return CheckoutResult.NOT_FOUND
            else:
                logger.exception(f"Error with Git operations: {e}")
                raise

    def get_diffs(self, ref: str | GitCommit, reverse: bool = True) -> list[Diff]:
        """Gets all staged diffs"""
        self.git_cli.git.add(A=True)
        return [diff for diff in self.git_cli.index.diff(ref, R=reverse)]

    @stopwatch
    def stage_and_commit_all_changes(self, message: str, verify: bool = False) -> bool:
        """TODO: rename to stage_and_commit_changes
        Stage all changes and commit them with the given message.
        Returns True if a commit was made and False otherwise.
        """
        self.git_cli.git.add(A=True)
        return self.commit_changes(message, verify)

    def commit_changes(self, message: str, verify: bool = False) -> bool:
        """Returns True if a commit was made and False otherwise."""
        staged_changes = self.git_cli.git.diff("--staged")
        if staged_changes:
            commit_args = ["-m", message]
            if not verify:
                commit_args.append("--no-verify")
            self.git_cli.git.commit(*commit_args)
            return True
        else:
            logger.info("No changes to commit. Do nothing.")
            return False

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

    def relpath(self, abspath) -> str:
        # TODO: check if the path is an abspath (i.e. contains self.repo_path)
        return os.path.relpath(abspath, self.repo_path)

    def abspath(self, relpath) -> str:
        return os.path.join(self.repo_path, relpath)

    # TODO: should rename to path exists so this can be used for dirs as well
    def file_exists(self, path: str) -> bool:
        return os.path.exists(self.abspath(path))

    def folder_exists(self, path: str) -> bool:
        return os.path.exists(self.abspath(path)) and os.path.isdir(self.abspath(path))

    def mkdir(self, path: str) -> None:
        os.makedirs(self.abspath(path), exist_ok=True)

    def emptydir(self, path: str) -> None:
        """Removes all files within the specified directory."""
        if self.folder_exists(self.abspath(path)):
            for filename in os.listdir(self.abspath(path)):
                file_path = os.path.join(self.abspath(path), filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)

    def get_file(self, path: str) -> str:
        """Returns the contents of a file"""
        file_path = self.abspath(path)
        try:
            with open(file_path, encoding="utf-8-sig") as file:
                content = file.read()
                return content
        except UnicodeDecodeError:
            try:
                with open(file_path, encoding="latin1") as file:
                    content = file.read()
                    return content
            except UnicodeDecodeError:
                print(f"Warning: Unable to decode file {file_path}. Skipping.")
                return None

    def write_file(self, relpath: str, content: str) -> None:
        """Writes file content to disk"""
        with open(self.abspath(relpath), "w") as f:
            f.write(content)

    def delete_file(self, path: str) -> None:
        """Deletes a file from the repo"""
        os.remove(self.abspath(path))
        if os.listdir(self.abspath(os.path.dirname(path))) == []:
            os.rmdir(self.abspath(os.path.dirname(path)))

    def get_filepaths_for_repo(self, ignore_list):
        # Get list of files to iterate over based on gitignore setting
        if self.repo_config.respect_gitignore:
            filepaths = self.git_cli.git.ls_files().split("\n")
        else:
            filepaths = glob.glob("**", root_dir=self.repo_path, recursive=True, include_hidden=True)
            # Filter filepaths by ignore list.
        if ignore_list:
            filepaths = [f for f in filepaths if not any(fnmatch.fnmatch(f, pattern) or f.startswith(pattern) for pattern in ignore_list)]

        return filepaths

    # TODO: unify param naming i.e. subdirectories vs subdirs probably use subdirectories since that's in the DB
    def iter_files(
        self,
        subdirs: list[str] | None = None,
        extensions: list[str] | None = None,
        ignore_list: list[str] | None = None,
    ) -> Generator[tuple[str, str]]:
        """Iterates over all files in the codebase, yielding the filepath and its content.

        Args:
        ----
            subdirs (list[str], optional): List of subdirectories to include. Defaults to None. Can include full filenames.
            codeowners (list[str], optional): List of codeowners to iter files for. Defaults to None. Ex: if codeowners=["@group"], only files owned by @group will be included.
            extensions (list[str], optional): List of file extensions to include. Defaults to None.

        Yields:
        ------
            tuple: A tuple containing the relative filepath and the content of the file.

        """
        filepaths = self.get_filepaths_for_repo(ignore_list)
        # Iterate through files and yield contents
        for rel_filepath in filepaths:
            rel_filepath: str
            filepath = os.path.join(self.repo_path, rel_filepath)

            # Filter by subdirectory (includes full filenames)
            if subdirs and not any(rel_filepath.startswith(subdir) for subdir in subdirs):
                continue

            if extensions is None or any(filepath.endswith(e) for e in extensions):
                try:
                    content = self.get_file(filepath)
                    yield rel_filepath, content
                except Exception as e:
                    print(f"Error reading file {filepath}: {e}")

    def list_files(self, subdirs: list[str] | None = None, extensions: list[str] | None = None) -> list[str]:
        """List files matching subdirs + extensions in a repo.

        Args:
        ----
            subdirs (list[str], optional): List of subdirectories to include. Defaults to None.
            codeowners (list[str], optional): List of codeowners to iter files for. Defaults to None. Ex: if codeowners=["@group"], only files owned by @group will be included.
            extensions (list[str], optional): List of file extensions to include. Defaults to None.

        Yields:
        ------
            str: filepath

        """
        list_files = []

        for rel_filepath in self.git_cli.git.ls_files().split("\n"):
            rel_filepath: str
            if subdirs and not any(d in rel_filepath for d in subdirs):
                continue
            if extensions is None or any(rel_filepath.endswith(e) for e in extensions):
                list_files.append(rel_filepath)
        return list_files

    def get_commits_in_last_n_days(self, days: int = 1) -> list[str]:
        """Returns a list of commits in the last n days"""
        repo = self.git_cli
        ret = []
        default_branch = self.default_branch
        for commit in repo.iter_commits(default_branch, all=True, reverse=False):
            current_dt = datetime.now(tz=UTC)
            current_dt = current_dt.replace(tzinfo=None)
            commit_dt = commit.committed_datetime
            commit_dt = commit_dt.replace(tzinfo=None)
            if int((current_dt - commit_dt).total_seconds()) > 60 * 60 * 24 * days:
                break
            ret.append(commit.hexsha)
        return ret

    def get_modified_files_in_last_n_days(self, days: int = 1) -> tuple[list[str], list[str]]:
        """Returns a list of files modified and deleted in the last n days"""
        modified_files = []
        deleted_files = []
        allowed_extensions = [".py"]

        repo = self.git_cli
        commits = self.get_commits_in_last_n_days(days)

        for commit_sha in commits:
            commit = repo.commit(commit_sha)
            files_changed = commit.stats.files
            for file, stats in files_changed.items():
                if stats["deletions"] == stats["lines"]:
                    deleted_files.append(file)
                    if file in modified_files:
                        modified_files.remove(file)
                else:
                    if file not in modified_files and file[-3:] in allowed_extensions:
                        modified_files.append(file)
        return modified_files, deleted_files

    @abstractmethod
    def base_url(self) -> str | None: ...

    def stash_push(self) -> None:
        self.git_cli.git.stash("push")

    def stash_pop(self) -> None:
        self.git_cli.git.stash("pop")

    ####################################################################################################################
    # PR UTILITIES
    ####################################################################################################################

    def get_pr_data(self, pr_number: int) -> dict:
        """Returns the data associated with a PR"""
        return self.remote_git_repo.get_pr_data(pr_number)

    def create_pr_comment(self, pr_number: int, body: str) -> None:
        """Create a general comment on a pull request.

        Args:
            pr_number (int): The PR number to comment on
            body (str): The comment text
        """
        pr = self.remote_git_repo.get_pull_safe(pr_number)
        if pr:
            self.remote_git_repo.create_issue_comment(pr, body)

    def create_pr_review_comment(
        self,
        pr_number: int,
        body: str,
        commit_sha: str,
        path: str,
        line: int | None = None,
        side: str | None = None,
        start_line: int | None = None,
    ) -> None:
        """Create an inline review comment on a specific line in a pull request.

        Args:
            pr_number (int): The PR number to comment on
            body (str): The comment text
            commit_sha (str): The commit SHA to attach the comment to
            path (str): The file path to comment on
            line (int | None, optional): The line number to comment on. Defaults to None.
            side (str | None, optional): Which version of the file to comment on ('LEFT' or 'RIGHT'). Defaults to None.
            start_line (int | None, optional): For multi-line comments, the starting line. Defaults to None.
        """
        pr = self.remote_git_repo.get_pull_safe(pr_number)
        if pr:
            commit = self.remote_git_repo.get_commit_safe(commit_sha)
            if commit:
                self.remote_git_repo.create_review_comment(
                    pull=pr,
                    body=body,
                    commit=commit,
                    path=path,
                    line=line,
                    side=side,
                    start_line=start_line,
                )
