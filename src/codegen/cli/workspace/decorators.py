import functools
from collections.abc import Callable

import click
import rich
from rich.status import Status

from codegen.cli.auth.constants import CODEGEN_DIR
from codegen.cli.auth.session import CodegenSession
from codegen.cli.rich.pretty_print import pretty_print_error
from codegen.cli.workspace.initialize_workspace import initialize_codegen


def requires_init(f: Callable) -> Callable:
    """Decorator that ensures codegen has been initialized."""

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        # Create a session if one wasn't provided
        session = kwargs.get("session")
        if not session:
            session = CodegenSession()
            kwargs["session"] = session

        if not session.codegen_dir.exists():
            rich.print("Codegen not initialized. Running init command first...")
            with Status("[bold]Initializing Codegen...", spinner="dots", spinner_style="purple") as status:
                initialize_codegen(status)

        # Check for config.toml existence and validity
        config_path = session.codegen_dir / "config.toml"
        if not config_path.exists():
            pretty_print_error(f"{CODEGEN_DIR}/config.toml is missing.\nPlease run 'codegen init' to initialize the project.")
            raise click.Abort()

        try:
            # This will attempt to parse the config
            _ = session.config
        except Exception as e:
            pretty_print_error(f"{CODEGEN_DIR}/config.toml is corrupted or invalid.\nDetails: {e!s}\n\n\nPlease run 'codegen init' to reinitialize the project.")
            raise click.Abort()

        try:
            # Verify git repo exists before proceeding
            _ = session.git_repo
        except ValueError:
            pretty_print_error(
                "This command must be run from within a git repository.\n\nPlease either:\n1. Navigate to a git repository directory\n2. Initialize a new git repository with 'git init'"
            )
            raise click.Abort()

        return f(*args, **kwargs)

    return wrapper
