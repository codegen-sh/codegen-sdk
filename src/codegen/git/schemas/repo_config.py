import base64
import logging
import os.path

from pydantic import BaseModel

from codegen.git.schemas.enums import RepoVisibility

logger = logging.getLogger(__name__)


class RepoConfig(BaseModel):
    """All the information about the repo needed to build a codebase"""

    name: str
    full_name: str | None = None
    organization_name: str | None = None
    visibility: RepoVisibility | None = None

    # Codebase fields
    base_dir: str = "/tmp"  # parent directory of the git repo
    base_path: str | None = None  # root directory of the codebase within the repo
    language: str | None = "PYTHON"
    subdirectories: list[str] | None = None
    respect_gitignore: bool = True

    @property
    def repo_path(self) -> str:
        return f"{self.base_dir}/{self.name}"

    @classmethod
    def from_repo_path(cls, repo_path: str, **kwargs) -> "RepoConfig":
        name = os.path.basename(repo_path)
        base_dir = os.path.dirname(repo_path)
        return cls(name=name, base_dir=base_dir, **kwargs)

    # TODO: remove
    def encoded_json(self):
        return base64.b64encode(self.model_dump_json().encode("utf-8")).decode("utf-8")

    # TODO: remove, read from shared config instead
    @staticmethod
    def from_encoded_json(encoded_json: str) -> "RepoConfig":
        decoded = base64.b64decode(encoded_json).decode("utf-8")
        return RepoConfig.model_validate_json(decoded)
