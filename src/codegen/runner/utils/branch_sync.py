from git.remote import Remote

from codegen.git.configs.constants import HIGHSIDE_REMOTE_NAME, LOWSIDE_REMOTE_NAME
from codegen.git.repo_operator.remote_repo_operator import RemoteRepoOperator
from codegen.git.schemas.github import GithubType
from codegen.git.utils.clone_url import get_authenticated_clone_url_for_repo_config


def get_remote_for_github_type(op: RemoteRepoOperator, github_type: GithubType = GithubType.GithubEnterprise) -> Remote:
    if op.github_type == github_type:
        return op.git_cli.remote(name="origin")

    remote_name = HIGHSIDE_REMOTE_NAME if github_type == GithubType.Github else LOWSIDE_REMOTE_NAME
    remote_url = get_authenticated_clone_url_for_repo_config(repo=op.repo_config, github_type=github_type)

    if remote_name in op.git_cli.remotes:
        remote = op.git_cli.remote(remote_name)
        remote.set_url(remote_url)
    else:
        remote = op.git_cli.create_remote(remote_name, remote_url)
    return remote
