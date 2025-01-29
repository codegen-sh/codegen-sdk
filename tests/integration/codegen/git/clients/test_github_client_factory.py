from codegen.git.clients.github_client_factory import GithubClientFactory
from codegen.git.schemas.github import GithubType


def test_github_client_factory_create_from_token_no_token():
    github_client = GithubClientFactory.create_from_token(github_type=GithubType.Github)
    assert github_client.base_url == "https://api.github.com"
    repo = github_client.read_client.get_repo("python-lsp/python-lsp-server")
    assert repo.full_name == "python-lsp/python-lsp-server"
    assert repo.name == "python-lsp-server"


def test_github_client_factory_create_from_repo(repo_config):
    github_client = GithubClientFactory.create_from_repo(repo_config=repo_config, github_type=GithubType.Github)
    repo = github_client.read_client.get_repo("codegen-sh/Kevin-s-Adventure-Game")
    assert repo.full_name == "codegen-sh/Kevin-s-Adventure-Game"
    assert repo.name == "Kevin-s-Adventure-Game"
