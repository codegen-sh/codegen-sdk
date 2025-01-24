import functools
from collections.abc import Callable

import click
import rich

from codegen.cli.auth.login import login_routine
from codegen.cli.auth.session import CodegenSession
from codegen.cli.errors import AuthError, InvalidTokenError, NoTokenError


def requires_auth(f: Callable) -> Callable:
    """Decorator that ensures a user is authenticated and injects a CodegenSession."""

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        session = CodegenSession()

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
