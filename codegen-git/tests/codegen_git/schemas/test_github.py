from codegen_git.schemas.github import GithubType


def test_github_type_base_url():
    assert GithubType.Github.base_url == "https://github.com"
    assert GithubType.GithubEnterprise.base_url == "https://github.codegen.app"
