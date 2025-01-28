import json
from pathlib import Path

DEFAULT_NOTEBOOK_CONTENT = """from codegen import Codebase

# Initialize codebase
codebase = Codebase('../../')

# Print out stats
print("🔍 Codebase Analysis")
print("=" * 50)
print(f"📚 Total Files: {len(codebase.files)}")
print(f"⚡ Total Functions: {len(codebase.functions)}")
print(f"🔄 Total Imports: {len(codebase.imports)}")
""".strip()


def create_notebook(jupyter_dir: Path) -> Path:
    """Create a new Jupyter notebook if it doesn't exist.

    Args:
        jupyter_dir: Directory where the notebook should be created

    Returns:
        Path to the created or existing notebook
    """
    notebook_path = jupyter_dir / "tmp.ipynb"
    if not notebook_path.exists():
        notebook_content = {
            "cells": [
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": DEFAULT_NOTEBOOK_CONTENT,
                }
            ],
            "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}},
            "nbformat": 4,
            "nbformat_minor": 4,
        }
        notebook_path.write_text(json.dumps(notebook_content, indent=2))
    return notebook_path
