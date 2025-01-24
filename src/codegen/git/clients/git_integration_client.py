import logging
from functools import cached_property

from github.GithubException import UnknownObjectException
from github.GithubIntegration import GithubIntegration
from github.Installation import Installation
from github.InstallationAuthorization import InstallationAuthorization

from codegen.git.schemas.github import GithubType

logger = logging.getLogger(__name__)


class GitIntegrationClient:
    """Wrapper around PyGithub's GithubIntegration."""

    github_type: GithubType = GithubType.GithubEnterprise
    client: GithubIntegration  # PyGithub's GithubIntegration that this class wraps

    def __init__(
        self,
        github_app_id: str,
        github_app_id_private_key: str,
        base_url: str | None = None,
    ) -> None:
        """Initialize a safe wrapper around PyGithub's GithubIntegration. Used for calling Github's integration APIs. (e.g. GitHub Apps)"""
        if base_url:
            self.client = GithubIntegration(integration_id=github_app_id, private_key=github_app_id_private_key, base_url=base_url)
        else:
            self.client = GithubIntegration(integration_id=github_app_id, private_key=github_app_id_private_key)

    @cached_property
    def name(self) -> str:
        return self.client.get_app().name

    def get_org_installation(self, org_name: str) -> Installation | None:
        try:
            return self.client.get_org_installation(org_name)
        except UnknownObjectException as e:
            return None
        except Exception as e:
            logger.warning(f"Error getting org installation with org_name: {org_name}\n\t{e}")
            return None

    def get_app_installation(self, installation_id: int) -> Installation | None:
        try:
            return self.client.get_app_installation(installation_id)
        except UnknownObjectException as e:
            return None
        except Exception as e:
            logger.warning(f"Error getting app installation with installation_id: {installation_id}\n\t{e}")
            return None

    def get_access_token(self, installation_id: int, permissions: dict[str, str]) -> InstallationAuthorization:
        # TODO: add try/catch error handling around this
        return self.client.get_access_token(installation_id=installation_id, permissions=permissions)
