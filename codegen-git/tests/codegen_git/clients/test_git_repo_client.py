from unittest.mock import MagicMock, patch

from codegen_git.clients.git_repo_client import GitRepoClient
from codegen_git.schemas.github import GithubScope


@patch("codegen_git.clients.git_repo_client.GithubClientFactory")
def test_delete_branch_default(
    mock_github_client_factory,
):
    git_repo_client = GitRepoClient(repo_config=MagicMock(), access_scope=GithubScope.WRITE)
    git_repo_client.read_client = MagicMock(default_branch="default-branch")
    git_repo_client.delete_branch(branch_name="default-branch")
    # assert write client is never accessed to delete the default branch
    assert git_repo_client._write_client.call_count == 0


@patch("codegen_git.clients.git_repo_client.GithubClientFactory")
def test_delete_branch_non_default_branch(
    mock_github_client_factory,
):
    git_repo_client = GitRepoClient(repo_config=MagicMock(), access_scope=GithubScope.WRITE)
    git_repo_client.read_client = MagicMock(default_branch="default-branch")
    mock_ref = MagicMock()
    git_repo_client._write_client.get_git_ref.return_value = mock_ref
    git_repo_client.delete_branch(branch_name="non-default-branch")
    assert mock_ref.delete.call_count == 1


@patch("codegen_git.clients.git_repo_client.GithubClientFactory")
def test_delete_branch_cannot_write_branch(
    mock_github_client_factory,
):
    git_repo_client = GitRepoClient(repo_config=MagicMock(), access_scope=GithubScope.WRITE)
    git_repo_client.read_client = MagicMock(default_branch="default-branch")
    git_repo_client.delete_branch(branch_name="not-default-branch")
    # assert write client is never accessed to delete the default branch
    assert git_repo_client._write_client.call_count == 0
