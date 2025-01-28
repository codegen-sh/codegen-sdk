import os
import subprocess
from pathlib import Path

import rich_click as click

from codegen.cli.auth.constants import CODEGEN_DIR
from codegen.cli.auth.decorators import requires_auth
from codegen.cli.auth.session import CodegenSession
from codegen.cli.rich.spinners import create_spinner
from codegen.cli.utils.notebooks import create_notebook
from codegen.cli.workspace.decorators import requires_init
from codegen.cli.workspace.venv_manager import VenvManager


def create_jupyter_dir() -> Path:
    """Create and return the jupyter directory."""
    jupyter_dir = Path.cwd() / CODEGEN_DIR / "jupyter"
    jupyter_dir.mkdir(parents=True, exist_ok=True)
    return jupyter_dir


@click.command(name="notebook")
@requires_auth
@requires_init
def notebook_command(session: CodegenSession):
    """Open a Jupyter notebook with the current codebase loaded."""
    with create_spinner("Setting up Jupyter environment...") as status:
        venv = VenvManager()

        status.update("Checking Jupyter installation...")
        venv.ensure_jupyter()

        jupyter_dir = create_jupyter_dir()
        notebook_path = create_notebook(jupyter_dir)

        status.update("Running Jupyter Lab...")

        # Prepare the environment with the virtual environment activated
        env = {**os.environ, "VIRTUAL_ENV": str(venv.venv_dir), "PATH": f"{venv.venv_dir}/bin:{os.environ['PATH']}"}

        # Run Jupyter Lab
        subprocess.run(["jupyter", "lab", str(notebook_path)], env=env, check=True)
