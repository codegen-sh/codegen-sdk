import os
from pathlib import Path

import click
from pygit2.enums import FileStatus, ResetMode
from pygit2.repository import Repository

from codegen.cli.auth.constants import CODEGEN_DIR
from codegen.cli.git.repo import get_git_repo


def is_codegen_file(filepath: str) -> bool:
    """Check if a file is in the .codegen directory."""
    return filepath.startswith(str(CODEGEN_DIR) + "/")


def backup_codegen_files(repo: Repository) -> dict[str, tuple[bytes, bool]]:
    """Backup .codegen files and track if they were staged.

    Returns:
        Dict mapping filepath to (content, was_staged) tuple
    """
    codegen_changes = {}
    for filepath, status in repo.status().items():
        if not is_codegen_file(filepath):
            continue

        was_staged = bool(status & (FileStatus.INDEX_MODIFIED | FileStatus.INDEX_NEW))
        if status & (FileStatus.WT_MODIFIED | FileStatus.WT_NEW | FileStatus.INDEX_MODIFIED | FileStatus.INDEX_NEW):
            with open(os.path.join(repo.workdir, filepath), "rb") as f:
                codegen_changes[filepath] = (f.read(), was_staged)

    return codegen_changes


def restore_codegen_files(repo: Repository, codegen_changes: dict[str, tuple[bytes, bool]]) -> None:
    """Restore backed up .codegen files and their staged status."""
    for filepath, (content, was_staged) in codegen_changes.items():
        file_path = Path(repo.workdir) / filepath
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(content)
        if was_staged:
            repo.index.add(filepath)
    if codegen_changes:
        repo.index.write()


def remove_untracked_files(repo: Repository) -> None:
    """Remove untracked files except those in .codegen directory."""
    for filepath, status in repo.status().items():
        if not is_codegen_file(filepath) and status & FileStatus.WT_NEW:
            file_path = Path(repo.workdir) / filepath
            if file_path.is_file():
                file_path.unlink()
            elif file_path.is_dir():
                file_path.rmdir()


@click.command(name="reset")
def reset_command() -> None:
    """Reset git repository while preserving all files in .codegen directory"""
    repo = get_git_repo()
    if not repo:
        click.echo("Not a git repository", err=True)
        return

    try:
        # Backup .codegen files and their staged status
        codegen_changes = backup_codegen_files(repo)

        # Reset everything
        repo.reset(repo.head.target, ResetMode.HARD)

        # Restore .codegen files and their staged status
        restore_codegen_files(repo, codegen_changes)

        # Remove untracked files except .codegen
        remove_untracked_files(repo)

        click.echo(f"Reset complete. Repository has been restored to HEAD (preserving {CODEGEN_DIR}) and untracked files have been removed (except {CODEGEN_DIR})")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


if __name__ == "__main__":
    reset_command()
