import functools
from collections.abc import Callable

import click
import rich
from rich.status import Status

from codegen.cli.auth.session import CodegenSession
from codegen.cli.rich.pretty_print import pretty_print_error
from codegen.cli.workspace.initialize_workspace import initialize_codegen


def requires_init(f: Callable) -> Callable:
    """Decorator that ensures codegen has been initialized."""

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        # Create a session if one wasn't provided
        session = kwargs.get("session") or CodegenSession.from_active_session()
        if session is None:
            rich.print("Codegen not initialized. Running init command first...")
            with Status("[bold]Initializing Codegen...", spinner="dots", spinner_style="purple") as status:
                session = initialize_codegen(status)

        # Check for valid session
        if not session.is_valid():
            pretty_print_error(f"The session at path {session.repo_path} is missing or corrupt.\nPlease run 'codegen init' to re-initialize the project.")
            raise click.Abort()

        kwargs["session"] = session
        return f(*args, **kwargs)

    return wrapper
