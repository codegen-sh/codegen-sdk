from typing import TYPE_CHECKING

import requests
from github import Repository
from github.PullRequest import PullRequest
from unidiff import PatchSet

from codegen.git.models.pull_request_context import PullRequestContext
from codegen.git.repo_operator.local_repo_operator import LocalRepoOperator
from codegen.git.repo_operator.remote_repo_operator import RemoteRepoOperator

if TYPE_CHECKING:
    from codegen.sdk.core.codebase import Codebase, Editable, File, Symbol


def get_merge_base(git_repo_client: Repository, pull: PullRequest | PullRequestContext) -> str:
    """Gets the merge base of a pull request using a remote GitHub API client.

    Args:
        git_repo_client (GitRepoClient): The GitHub repository client.
        pull (PullRequest): The pull request object.

    Returns:
        str: The SHA of the merge base commit.
    """
    comparison = git_repo_client.compare(pull.base.sha, pull.head.sha)
    return comparison.merge_base_commit.sha


def get_file_to_changed_ranges(pull_patch_set: PatchSet) -> dict[str, list]:
    file_to_changed_ranges = {}
    for patched_file in pull_patch_set:
        # TODO: skip is deleted
        if patched_file.is_removed_file:
            continue
        changed_ranges = []  # list of changed lines for the file
        for hunk in patched_file:
            changed_ranges.append(range(hunk.target_start, hunk.target_start + hunk.target_length))
        file_to_changed_ranges[patched_file.path] = changed_ranges
    return file_to_changed_ranges


def get_pull_patch_set(op: LocalRepoOperator | RemoteRepoOperator, pull: PullRequestContext) -> PatchSet:
    # Get the diff directly from GitHub's API
    if not op.remote_git_repo:
        msg = "GitHub API client is required to get PR diffs"
        raise ValueError(msg)

    # Get the diff directly from the PR
    diff_url = pull.raw_data.get("diff_url")
    if diff_url:
        # Fetch the diff content from the URL
        response = requests.get(diff_url)
        response.raise_for_status()
        diff = response.text
    else:
        # If diff_url not available, get the patch directly
        diff = pull.get_patch()

    # Parse the diff into a PatchSet
    pull_patch_set = PatchSet(diff)
    return pull_patch_set


def to_1_indexed(zero_indexed_range: range) -> range:
    """Converts a n-indexed range to n+1-indexed.
    Primarily to convert 0-indexed ranges to 1 indexed
    """
    return range(zero_indexed_range.start + 1, zero_indexed_range.stop + 1)


def overlaps(range1: range, range2: range) -> bool:
    """Returns True if the two ranges overlap, False otherwise."""
    return max(range1.start, range2.start) < min(range1.stop, range2.stop)


class CodegenPR:
    """Wrapper around PRs - enables codemods to interact with them"""

    _gh_pr: PullRequest
    _codebase: "Codebase"
    _op: LocalRepoOperator | RemoteRepoOperator

    # =====[ Computed ]=====
    _modified_file_ranges: dict[str, list[tuple[int, int]]] = None

    def __init__(self, op: LocalRepoOperator, codebase: "Codebase", pr: PullRequest):
        self._op = op
        self._gh_pr = pr
        self._codebase = codebase

    @property
    def modified_file_ranges(self) -> dict[str, list[tuple[int, int]]]:
        """Files and the ranges within that are modified"""
        if not self._modified_file_ranges:
            pull_patch_set = get_pull_patch_set(op=self._op, pull=self._gh_pr)
            self._modified_file_ranges = get_file_to_changed_ranges(pull_patch_set)
        return self._modified_file_ranges

    @property
    def modified_files(self) -> list["File"]:
        filenames = self.modified_file_ranges.keys()
        return [self._codebase.get_file(f, optional=True) for f in filenames]

    def is_modified(self, editable: "Editable") -> bool:
        """Returns True if the Editable's range contains any modified lines"""
        filepath = editable.filepath
        changed_ranges = self._modified_file_ranges.get(filepath, [])
        symbol_range = to_1_indexed(editable.line_range)
        if any(overlaps(symbol_range, changed_range) for changed_range in changed_ranges):
            return True
        return False

    @property
    def modified_symbols(self) -> list["Symbol"]:
        # Import SourceFile locally to avoid circular dependencies
        from codegen.sdk.core.file import SourceFile

        all_modified = []
        for file in self.modified_files:
            if file is None:
                print("Warning: File is None")
                continue
            if not isinstance(file, SourceFile):
                continue
            for symbol in file.symbols:
                if self.is_modified(symbol):
                    all_modified.append(symbol)
        return all_modified

    def get_pr_diff(self) -> str:
        """Get the full diff of the PR"""
        if not self._op.remote_git_repo:
            msg = "GitHub API client is required to get PR diffs"
            raise ValueError(msg)

        # Get the diff directly from the PR
        diff_url = self._gh_pr.raw_data.get("diff_url")
        if diff_url:
            # Fetch the diff content from the URL
            response = requests.get(diff_url)
            response.raise_for_status()
            return response.text
        else:
            # If diff_url not available, get the patch directly
            return self._gh_pr.get_patch()
