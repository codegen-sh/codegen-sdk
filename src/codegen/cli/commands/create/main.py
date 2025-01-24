from pathlib import Path

import rich
import rich_click as click

from codegen.cli.api.client import RestAPI
from codegen.cli.auth.constants import PROMPTS_DIR
from codegen.cli.auth.decorators import requires_auth
from codegen.cli.auth.session import CodegenSession
from codegen.cli.codemod.convert import convert_to_cli
from codegen.cli.errors import ServerError
from codegen.cli.rich.codeblocks import format_command, format_path
from codegen.cli.rich.pretty_print import pretty_print_error
from codegen.cli.rich.spinners import create_spinner
from codegen.cli.utils.constants import ProgrammingLanguage
from codegen.cli.workspace.decorators import requires_init


def get_prompts_dir() -> Path:
    """Get the directory for storing prompts, creating it if needed."""
    PROMPTS_DIR.mkdir(parents=True, exist_ok=True)

    # Ensure .gitignore exists and contains the prompts directory
    gitignore = Path.cwd() / ".gitignore"
    if not gitignore.exists() or "codegen-sh/prompts" not in gitignore.read_text():
        with open(gitignore, "a") as f:
            f.write("\n# Codegen prompts\ncodegen-sh/prompts/\n")

    return PROMPTS_DIR


def get_target_path(name: str, path: Path) -> Path:
    """Get the target path for the new function file."""
    # Convert name to snake case for filename
    name_snake = name.lower().replace("-", "_").replace(" ", "_")

    if path.suffix == ".py":
        # If path is a file, use it directly
        return path
    else:
        # If path is a directory, create name_snake.py in it
        return path / f"{name_snake}.py"


def make_relative(path: Path) -> str:
    """Convert a path to a relative path from cwd, handling non-existent paths."""
    # If it's just a filename in the current directory, return it directly
    if str(path.parent) == ".":
        return f"./{path.name}"

    try:
        return f"./{path.relative_to(Path.cwd())}"
    except ValueError:
        # For paths in subdirectories, try to make the parent relative
        try:
            parent_rel = path.parent.relative_to(Path.cwd())
            return f"./{parent_rel}/{path.name}"
        except ValueError:
            # If all else fails, just return the filename
            return f"./{path.name}"


@click.command(name="create")
@requires_auth
@requires_init
@click.argument("name", type=str)
@click.argument("path", type=click.Path(path_type=Path), default=Path.cwd())
@click.option("--description", "-d", default=None, help="Description of what this codemod does.")
@click.option("--overwrite", is_flag=True, help="Overwrites function if it already exists.")
def create_command(session: CodegenSession, name: str, path: Path, description: str | None = None, overwrite: bool = False):
    """Create a new codegen function.

    NAME is the name/label for the function
    PATH is where to create the function (default: current directory)
    """
    # Get the target path for the function
    target_path = get_target_path(name, path)

    # Check if file exists
    if target_path.exists() and not overwrite:
        rel_path = make_relative(target_path)
        pretty_print_error(f"File already exists at {format_path(rel_path)}\n\nTo overwrite the file:\n{format_command(f'codegen create {name} {rel_path} --overwrite')}")
        return

    if description:
        status_message = "Generating function (using LLM, this will take ~30s)"
    else:
        status_message = "Setting up function"

    rich.print("")  # Add a newline before the spinner
    with create_spinner(status_message) as status:
        try:
            # Get code from API
            response = RestAPI(session.token).create(name=name, query=description if description else None)

            # Convert the code to include the decorator
            code = convert_to_cli(response.code, session.config.programming_language or ProgrammingLanguage.PYTHON, name)

            # Create the target directory if needed
            target_path.parent.mkdir(parents=True, exist_ok=True)

            # Write the function code
            target_path.write_text(code)

            # Write the system prompt to the prompts directory
            if response.context:
                prompt_path = get_prompts_dir() / f"{name.lower().replace(' ', '-')}-system-prompt.md"
                prompt_path.write_text(response.context)

        except ServerError as e:
            status.stop()
            raise click.ClickException(str(e))
        except ValueError as e:
            status.stop()
            raise click.ClickException(str(e))

    # Success message
    rich.print(f"\n✅ {'Overwrote' if overwrite and target_path.exists() else 'Created'} function '{name}'")
    rich.print("")
    rich.print("📁 Files Created:")
    rich.print(f"   [dim]Function:[/dim]  {make_relative(target_path)}")
    if response.context:
        rich.print(f"   [dim]Prompt:[/dim]    {make_relative(get_prompts_dir() / f'{name.lower().replace(" ", "-")}-system-prompt.md')}")

    # Next steps
    rich.print("\n[bold]What's next?[/bold]\n")
    rich.print("1. Review and edit the function to customize its behavior")
    rich.print(f"2. Run it with: \n{format_command(f'codegen run {name}')}")
