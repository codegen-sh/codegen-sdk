from codegen.git.clients.github_client import GithubClient
from codegen.git.clients.github_enterprise_client import GithubEnterpriseClient

GithubClientType = GithubClient | GithubEnterpriseClient
