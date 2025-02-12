from dataclasses import dataclass
from pathlib import Path

from codegen.cli.api.client import RestAPI
from codegen.cli.auth.session import CodegenSession
from codegen.cli.auth.token_manager import get_current_token
from codegen.cli.errors import AuthError, NoTokenError


@dataclass
class User:
    full_name: str
    email: str
    github_username: str


@dataclass
class Identity:
    token: str
    expires_at: str
    status: str
    user: "User"


class CodegenAuthenticatedSession(CodegenSession):
    """Represents an authenticated codegen session with user and repository context"""

    # =====[ Instance attributes ]=====
    _token: str | None = None

    # =====[ Lazy instance attributes ]=====
    _identity: Identity | None = None

    def __init__(self, token: str | None = None, repo_path: Path | None = None):
        # TODO: fix jank.
        # super().__init__(repo_path)
        self._token = token

    @property
    def token(self) -> str | None:
        """Get the current authentication token"""
        if self._token:
            return self._token
        return get_current_token()

    @property
    def identity(self) -> Identity | None:
        """Get the identity of the user, if a token has been provided"""
        if self._identity:
            return self._identity
        if not self.token:
            msg = "No authentication token found"
            raise NoTokenError(msg)

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
