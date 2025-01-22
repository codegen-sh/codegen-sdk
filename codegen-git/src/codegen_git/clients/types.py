from codegen_git.clients.github_client import GithubClient
from codegen_git.clients.github_enterprise_client import GithubEnterpriseClient

GithubClientType = GithubClient | GithubEnterpriseClient
