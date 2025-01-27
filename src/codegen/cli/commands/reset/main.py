import os
from pathlib import Path

import click
from pygit2.enums import FileStatus, ResetMode

from codegen.cli.auth.constants import CODEGEN_DIR
from codegen.cli.git.repo import get_git_repo


@click.command(name="reset")
def reset_command() -> None:
    """Reset git repository while preserving all files in .codegen directory"""
    repo = get_git_repo()
    if not repo:
        click.echo("Not a git repository", err=True)
        return

    try:
        # Get current state of .codegen files
        codegen_changes = {}
        for filepath, status in repo.status().items():
            if filepath.startswith(str(CODEGEN_DIR) + "/"):
                if status & (FileStatus.WT_MODIFIED | FileStatus.WT_NEW | FileStatus.INDEX_MODIFIED | FileStatus.INDEX_NEW):
                    with open(os.path.join(repo.workdir, filepath), "rb") as f:
                        codegen_changes[filepath] = f.read()

        # Reset everything
        repo.reset(repo.head.target, ResetMode.HARD)

        # Restore .codegen files
        for filepath, content in codegen_changes.items():
            file_path = Path(repo.workdir) / filepath
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "wb") as f:
                f.write(content)

        # Remove untracked files except .codegen
        for filepath, status in repo.status().items():
            if not filepath.startswith(str(CODEGEN_DIR) + "/") and status & FileStatus.WT_NEW:
                file_path = Path(repo.workdir) / filepath
                if file_path.is_file():
                    file_path.unlink()
                elif file_path.is_dir():
                    file_path.rmdir()

        click.echo(f"Reset complete. Repository has been restored to HEAD (preserving {CODEGEN_DIR}) and untracked files have been removed (except {CODEGEN_DIR})")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


if __name__ == "__main__":
    reset_command()
