import os
import subprocess
from pathlib import Path

from codegen.cli.auth.constants import CODEGEN_DIR
from codegen.cli.git.repo import get_git_repo


class VenvManager:
    def __init__(self):
        repo = get_git_repo()
        self.repo_path = Path(repo.workdir)
        self.codegen_dir = self.repo_path / CODEGEN_DIR
        self.venv_dir = self.codegen_dir / ".venv"
        self.python_path = self.venv_dir / "bin" / "python"
        self.pip_path = self.venv_dir / "bin" / "pip"

    def create_venv(self, python_version: str = "3.12") -> None:
        """Create a virtual environment using uv."""
        self.codegen_dir.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["uv", "venv", "--python", python_version, str(self.venv_dir)],
            check=True,
        )

    def install_packages(self, *packages: str) -> None:
        """Install packages into the virtual environment using uv pip."""
        subprocess.run(
            ["uv", "pip", "install", *packages],
            check=True,
            env={**os.environ, "VIRTUAL_ENV": str(self.venv_dir)},
        )

    def get_activate_command(self) -> str:
        """Get the command to activate the virtual environment."""
        return f"source {self.venv_dir}/bin/activate"

    def is_active(self) -> bool:
        """Check if a virtual environment is active."""
        return "VIRTUAL_ENV" in os.environ

    def is_initialized(self) -> bool:
        """Check if the virtual environment exists and is properly set up."""
        return self.venv_dir.exists() and self.python_path.exists()
