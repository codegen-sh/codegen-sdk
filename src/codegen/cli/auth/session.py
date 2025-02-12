from pathlib import Path

from pygit2.repository import Repository

from codegen.cli.git.repo import get_git_repo
from codegen.shared.configs.config import load
from codegen.shared.configs.constants import CODEGEN_DIR_NAME, CONFIG_FILENAME
from codegen.shared.configs.global_config import config as global_config
from codegen.shared.configs.models import Config


class CodegenSession:
    """Represents an authenticated codegen session with user and repository context"""

    repo_path: Path  # TODO: rename to root_path
    codegen_dir: Path
    config: Config
    existing: bool

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.codegen_dir = repo_path / CODEGEN_DIR_NAME
        self.existing = global_config.get_session(repo_path) is not None
        self.config = load(self.codegen_dir / CONFIG_FILENAME)
        global_config.set_active_session(repo_path)

    @classmethod
    def from_active_session(cls) -> "CodegenSession | None":
        active_session = global_config.get_active_session()
        if not active_session:
            return None

        return cls(active_session)

    def is_valid(self) -> bool:
        """Validates that the session configuration is correct"""
        # TODO: also make sure all the expected prompt, jupyter, codemods are present
        # TODO: make sure there is still a git instance here.
        return self.repo_path.exists() and self.codegen_dir.exists() and Path(self.config.file_path).exists()

    @property
    def git_repo(self) -> Repository:
        git_repo = get_git_repo(Path.cwd())
        if not git_repo:
            msg = "No git repository found"
            raise ValueError(msg)
        return git_repo

    def __str__(self) -> str:
        return f"CodegenSession(user={self.config.repository.user_name}, repo={self.config.repository.repo_name})"
