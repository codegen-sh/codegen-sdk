from pathlib import Path

from codegen.cli.git.repo import get_git_repo
from codegen.git.repo_operator.local_git_repo import LocalGitRepo
from codegen.shared.configs.constants import CODEGEN_DIR_NAME, CONFIG_FILENAME
from codegen.shared.configs.models.session import SessionConfig
from codegen.shared.configs.session_configs import global_config, load_session_config


class CodegenSession:
    """Represents an authenticated codegen session with user and repository context"""

    repo_path: Path
    codegen_dir: Path
    config: SessionConfig
    existing: bool

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.codegen_dir = repo_path / CODEGEN_DIR_NAME
        self.existing = global_config.get_session(repo_path) is not None
        self.config = load_session_config(self.codegen_dir / CONFIG_FILENAME)
        global_config.set_active_session(repo_path)

        if not self.existing:
            self._initialize_repo_config()

    @classmethod
    def from_active_session(cls) -> "CodegenSession | None":
        active_session = global_config.get_active_session()
        if not active_session:
            return None

        return cls(active_session)

    @classmethod
    def from_local_git(cls, git_repo: LocalGitRepo, token: str | None = None) -> "CodegenSession":
        session = cls(git_repo.repo_path)
        session._initialize_repo_config(git_repo, token)
        return session

    def _initialize_repo_config(self, git_repo: LocalGitRepo, token: str | None = None):
        """Initialize the codegen session"""
        self.config.repository.repo_path = str(git_repo.repo_path)
        self.config.repository.repo_name = git_repo.name
        self.config.repository.full_name = git_repo.full_name
        self.config.repository.user_name = git_repo.user_name
        self.config.repository.user_email = git_repo.user_email
        self.config.repository.language = git_repo.get_language(access_token=token)
        self.config.save()

    def is_valid(self) -> bool:
        """Validates that the session configuration is correct"""
        if not self.repo_path.exists():
            return False

        if not self.codegen_dir.exists():
            return False

        if not Path(self.config.file_path).exists():
            return False

        if get_git_repo(self.repo_path) is None:
            return False

    def __str__(self) -> str:
        return f"CodegenSession(user={self.config.repository.user_name}, repo={self.config.repository.repo_name})"
