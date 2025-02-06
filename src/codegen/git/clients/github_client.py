import logging
from typing import Self

from github import Consts
from github.GithubException import UnknownObjectException
from github.MainClass import Github
from github.Organization import Organization
from github.Repository import Repository

from codegen.git.configs.config import config

logger = logging.getLogger(__name__)


class GithubClient:
    """Manages interaction with GitHub"""

    base_url: str
    _client: Github

    def __init__(self, base_url: str = Consts.DEFAULT_BASE_URL):
        self.base_url = base_url
        self._client = Github(config.GITHUB_TOKEN, base_url=base_url)

    @classmethod
    def from_token(cls, token: str | None = None) -> Self:
        """Option to create a git client from a token"""
        gh_wrapper = cls()
        gh_wrapper._client = Github(token, base_url=cls.base_url)
        return gh_wrapper

    @property
    def client(self) -> Github:
        return self._client

    ####################################################################################################################
    # CHECK RUNS
    ####################################################################################################################

    def get_repo_by_full_name(self, full_name: str) -> Repository | None:
        try:
            return self._client.get_repo(full_name)
        except UnknownObjectException as e:
            return None
        except Exception as e:
            logger.warning(f"Error getting repo {full_name}:\n\t{e}")
            return None

    def get_organization(self, org_name: str) -> Organization | None:
        try:
            return self._client.get_organization(org_name)
        except UnknownObjectException as e:
            return None
        except Exception as e:
            logger.warning(f"Error getting org {org_name}:\n\t{e}")
            return None
