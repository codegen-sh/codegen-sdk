import base64
import logging

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class BaseRepoConfig(BaseModel):
    """Base version of RepoConfig that does not depend on the db."""

    name: str = ""
    respect_gitignore: bool = True


class RepoConfig(BaseModel):
    """All the information about the repo needed to build a codebase"""

    id: int
    name: str
    full_name: str

    # Org fields
    organization_id: int
    organization_name: str

    # Codebase fields
    base_dir: str = "/tmp"
    base_path: str | None = None
    language: str | None = "PYTHON"
    subdirectories: list[str] | None = None
    respect_gitignore: bool = True

    def encoded_json(self):
        return base64.b64encode(self.model_dump_json().encode("utf-8")).decode("utf-8")

    @staticmethod
    def from_encoded_json(encoded_json: str) -> "RepoConfig":
        decoded = base64.b64decode(encoded_json).decode("utf-8")
        return RepoConfig.model_validate_json(decoded)
