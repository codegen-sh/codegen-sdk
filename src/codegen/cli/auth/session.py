from dataclasses import dataclass
from pathlib import Path

from pygit2.repository import Repository

from codegen.cli.auth.constants import CODEGEN_DIR
from codegen.cli.auth.token_manager import get_current_token
from codegen.cli.errors import AuthError, NoTokenError
from codegen.cli.git.repo import get_git_repo
from codegen.cli.utils.config import Config, get_config, write_config
from codegen.sdk.enums import ProgrammingLanguage


@dataclass
class Identity:
    token: str
    expires_at: str
    status: str
    user: "User"


@dataclass
class User:
    full_name: str
    email: str
    github_username: str


@dataclass
class UserProfile:
    """User profile populated from /identity endpoint"""

    name: str
    email: str
    username: str


class CodegenSession:
    """Represents an authenticated codegen session with user and repository context"""

    # =====[ Instance attributes ]=====
    token: str | None = None

    # =====[ Lazy instance attributes ]=====
    _config: Config | None = None
    _identity: Identity | None = None
    _profile: UserProfile | None = None

    def __init__(self, token: str | None = None):
        self.token = token or get_current_token()

    @property
    def config(self) -> Config:
        """Get the config for the current session"""
        if self._config:
            return self._config
        self._config = get_config(self.codegen_dir)
        return self._config

    @property
    def identity(self) -> Identity | None:
        """Get the identity of the user, if a token has been provided"""
        if self._identity:
            return self._identity
        if not self.token:
            msg = "No authentication token found"
            raise NoTokenError(msg)

        from codegen.cli.api.client import RestAPI

        identity = RestAPI(self.token).identify()
        if not identity:
            return None

        self._identity = Identity(
            token=self.token,
            expires_at=identity.auth_context.expires_at,
            status=identity.auth_context.status,
            user=User(
                full_name=identity.user.full_name,
                email=identity.user.email,
                github_username=identity.user.github_username,
            ),
        )
        return self._identity

    @property
    def profile(self) -> UserProfile | None:
        """Get the user profile information"""
        if self._profile:
            return self._profile
        if not self.identity:
            return None

        self._profile = UserProfile(
            name=self.identity.user.full_name,
            email=self.identity.user.email,
            username=self.identity.user.github_username,
        )
        return self._profile

    @property
    def git_repo(self) -> Repository:
        git_repo = get_git_repo(Path.cwd())
        if not git_repo:
            msg = "No git repository found"
            raise ValueError(msg)
        return git_repo

    @property
    def repo_name(self) -> str:
        """Get the current repository name"""
        return self.config.repo_full_name

    @property
    def language(self) -> ProgrammingLanguage:
        """Get the current language"""
        # TODO(jayhack): This is a temporary solution to get the language.
        # We should eventually get the language on init.
        return self.config.programming_language or ProgrammingLanguage.PYTHON

    @property
    def codegen_dir(self) -> Path:
        """Get the path to the  codegen-sh directory"""
        return Path.cwd() / CODEGEN_DIR

    def __str__(self) -> str:
        return f"CodegenSession(user={self.profile.name}, repo={self.repo_name})"

    def is_authenticated(self) -> bool:
        """Check if the session is fully authenticated, including token expiration"""
        return bool(self.identity and self.identity.status == "active")

    def assert_authenticated(self) -> None:
        """Raise an AuthError if the session is not fully authenticated"""
        if not self.identity:
            msg = "No identity found for session"
            raise AuthError(msg)
        if self.identity.status != "active":
            msg = "Current session is not active. API Token may be invalid or may have expired."
            raise AuthError(msg)

    def write_config(self) -> None:
        """Write the config to the codegen-sh/config.toml file"""
        write_config(self.config, self.codegen_dir)
