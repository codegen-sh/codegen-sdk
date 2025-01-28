from codegen.git.clients.github_client import GithubClient
from codegen.git.clients.github_enterprise_client import GithubEnterpriseClient
from codegen.git.clients.types import GithubClientType
from codegen.git.schemas.github import GithubType
from codegen.git.schemas.repo_config import RepoConfig


class GithubClientFactory:
    """Factory for creating GithubClients"""

    # TODO: also allow creating from a organization model
    @classmethod
    def create_from_repo(cls, repo_config: RepoConfig, github_type: GithubType = GithubType.GithubEnterprise) -> GithubClientType:
        """Factory method for creating an instance of a subclass of GithubClientType.

        This method creates and returns an instance of either GithubEnterpriseClient or GithubClient, depending on the specified github_type. It is designed to abstract the instantiation process,
        allowing for easy creation of the appropriate GithubClient subclass.

        Defaults to GHE b/c for most cases we should be operating in GHE (i.e. the lowside) and only lowside/highside utils should sync between lowside and highside (i.e. sync between GHE and Github).

        Parameters
        ----------
        - repo (RepoModel): The repository model instance which contains necessary data for the GitHub wrapper.
        - github_type (GithubType, optional): An enum value specifying the type of GitHub instance.
          Defaults to GithubType.GithubEnterprise.

        Returns:
        -------
        - GithubClientType: An instance of either GithubEnterpriseClient or GithubClient, depending on the github_type.

        Raises:
        ------
        - Exception: If an unknown github_type is provided, the method raises an exception with a message indicating the invalid type.

        """
        if github_type == GithubType.GithubEnterprise:
            return GithubEnterpriseClient.from_repo_config(repo_config=repo_config)
        elif github_type == GithubType.Github:
            return GithubClient.from_repo_config(repo_config=repo_config)
        else:
            msg = f"Unknown GithubType: {github_type}"
            raise Exception(msg)

    @classmethod
    def create_from_token(cls, token: str | None = None, github_type: GithubType = GithubType.GithubEnterprise) -> GithubClientType:
        if github_type == GithubType.GithubEnterprise:
            return GithubEnterpriseClient.from_token(token=token)
        elif github_type == GithubType.Github:
            return GithubClient.from_token(token=token)
        else:
            msg = f"Unknown GithubType: {github_type}"
            raise Exception(msg)
