import logging
from typing import Self

from github import Consts
from github.GithubException import UnknownObjectException
from github.MainClass import Github
from github.Organization import Organization
from github.Repository import Repository

from codegen.git.configs.token import get_token_for_repo_config
from codegen.git.schemas.github import GithubScope, GithubType
from codegen.git.schemas.repo_config import RepoConfig

logger = logging.getLogger(__name__)


class GithubClient:
    """Manages interaction with GitHub"""

    type: GithubType = GithubType.Github
    base_url: str = Consts.DEFAULT_BASE_URL
    read_client: Github
    _write_client: Github

    @classmethod
    def from_repo_config(cls, repo_config: RepoConfig) -> Self:
        gh_wrapper = cls()
        gh_wrapper.read_client = gh_wrapper._create_client_for_repo(repo_config, github_scope=GithubScope.READ)
        gh_wrapper._write_client = gh_wrapper._create_client_for_repo(repo_config, github_scope=GithubScope.WRITE)
        return gh_wrapper

    @classmethod
    def from_token(cls, token: str | None = None) -> Self:
        """Option to create a git client from a token"""
        gh_wrapper = cls()
        gh_wrapper.read_client = Github(token, base_url=cls.base_url)
        gh_wrapper._write_client = Github(token, base_url=cls.base_url)
        return gh_wrapper

    def _create_client_for_repo(self, repo_config: RepoConfig, github_scope: GithubScope = GithubScope.READ) -> Github:
        token = get_token_for_repo_config(repo_config=repo_config, github_type=self.type, github_scope=github_scope)
        return Github(token, base_url=self.base_url)

    def _get_client_for_scope(self, github_scope: GithubScope) -> Github:
        if github_scope is GithubScope.READ:
            return self.read_client
        elif github_scope is GithubScope.WRITE:
            return self._write_client
        msg = f"Invalid github scope: {github_scope}"
        raise ValueError(msg)

    ####################################################################################################################
    # CHECK RUNS
    ####################################################################################################################

    def get_repo_by_full_name(self, full_name: str, github_scope: GithubScope = GithubScope.READ) -> Repository | None:
        try:
            return self._get_client_for_scope(github_scope).get_repo(full_name)
        except UnknownObjectException as e:
            return None
        except Exception as e:
            logger.warning(f"Error getting repo {full_name}:\n\t{e}")
            return None

    def get_organization(self, org_name: str, github_scope: GithubScope = GithubScope.READ) -> Organization | None:
        try:
            return self._get_client_for_scope(github_scope).get_organization(org_name)
        except UnknownObjectException as e:
            return None
        except Exception as e:
            logger.warning(f"Error getting org {org_name}:\n\t{e}")
            return None
