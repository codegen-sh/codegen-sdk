import functools
from collections.abc import Callable

import click
import rich

from codegen.cli.auth.auth_session import CodegenAuthenticatedSession
from codegen.cli.auth.login import login_routine
from codegen.cli.errors import AuthError, InvalidTokenError, NoTokenError
from codegen.cli.rich.pretty_print import pretty_print_error


def requires_auth(f: Callable) -> Callable:
    """Decorator that ensures a user is authenticated and injects a CodegenSession."""

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        session = CodegenAuthenticatedSession.from_active_session()

        # Check for valid session
        if not session.is_valid():
            pretty_print_error(f"The session at path {session.repo_path} is missing or corrupt.\nPlease run 'codegen init' to re-initialize the project.")
            raise click.Abort()

        try:
            if not session.is_authenticated():
                rich.print("[yellow]Not authenticated. Let's get you logged in first![/yellow]\n")
                session = login_routine()
        except (InvalidTokenError, NoTokenError) as e:
            rich.print("[yellow]Authentication token is invalid or expired. Let's get you logged in again![/yellow]\n")
            session = login_routine()
        except AuthError as e:
            raise click.ClickException(str(e))

        return f(*args, session=session, **kwargs)

    return wrapper
