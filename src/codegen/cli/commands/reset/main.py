import shutil
from pathlib import Path

import click


@click.command()
@click.argument("path", type=click.Path(exists=True), default=".")
def reset_command(path: str | Path) -> None:
    """Reset a directory by removing all files and folders except .codegen"""
    path = Path(path)

    for item in path.iterdir():
        if item.name == ".codegen":
            continue

        try:
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
        except Exception as e:
            click.echo(f"Error removing {item}: {e}", err=True)

    click.echo(f"Reset complete. All files except .codegen have been removed from {path}")


if __name__ == "__main__":
    reset_command()
