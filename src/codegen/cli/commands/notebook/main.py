import os
import subprocess
from pathlib import Path

import rich_click as click

from codegen.cli.auth.constants import CODEGEN_DIR
from codegen.cli.auth.decorators import requires_auth
from codegen.cli.auth.session import CodegenSession
from codegen.cli.rich.spinners import create_spinner
from codegen.cli.workspace.decorators import requires_init
from codegen.cli.workspace.venv_manager import VenvManager


def create_jupyter_dir() -> Path:
    """Create and return the jupyter directory."""
    jupyter_dir = Path.cwd() / CODEGEN_DIR / "jupyter"
    jupyter_dir.mkdir(parents=True, exist_ok=True)
    return jupyter_dir


def create_notebook(jupyter_dir: Path) -> Path:
    """Create a new Jupyter notebook if it doesn't exist."""
    notebook_path = jupyter_dir / "tmp.ipynb"
    if not notebook_path.exists():
        notebook_content = {
            "cells": [
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": ["from codegen import Codebase\n", "\n", "# Initialize codebase\n", "codebase = Codebase.from_directory('.')\n"],
                }
            ],
            "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}},
            "nbformat": 4,
            "nbformat_minor": 4,
        }
        import json

        notebook_path.write_text(json.dumps(notebook_content, indent=2))
    return notebook_path


@click.command(name="notebook")
@requires_auth
@requires_init
def notebook_command(session: CodegenSession):
    """Open a Jupyter notebook with the current codebase loaded."""
    with create_spinner("Setting up Jupyter environment...") as status:
        venv = VenvManager()

        if not venv.is_initialized():
            status.update("Creating virtual environment...")
            venv.create_venv()

        status.update("Installing required packages...")
        venv.install_packages("codegen", "jupyterlab")

        jupyter_dir = create_jupyter_dir()
        notebook_path = create_notebook(jupyter_dir)

        status.update("Starting Jupyter Lab...")

        # Prepare the environment with the virtual environment activated
        env = {**os.environ, "VIRTUAL_ENV": str(venv.venv_dir), "PATH": f"{venv.venv_dir}/bin:{os.environ['PATH']}"}

        # Start Jupyter Lab
        subprocess.Popen(["jupyter", "lab", str(notebook_path)], env=env, start_new_session=True)
