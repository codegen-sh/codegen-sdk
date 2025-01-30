import webbrowser

import rich
import rich_click as click

from codegen.cli.api.webapp_routes import USER_SECRETS_ROUTE
from codegen.cli.auth.session import CodegenSession
from codegen.cli.auth.token_manager import TokenManager
from codegen.cli.env.global_env import global_env
from codegen.cli.errors import AuthError


def login_routine(token: str | None = None) -> CodegenSession:
    """Guide user through login flow and return authenticated session.

    Args:
        console: Optional console for output. Creates new one if not provided.

    Returns:
        CodegenSession: Authenticated session

    Raises:
        click.ClickException: If login fails

    """
    # Try environment variable first

    _token = token or global_env.CODEGEN_USER_ACCESS_TOKEN

    # If no token provided, guide user through browser flow
    if not _token:
        rich.print(f"Opening {USER_SECRETS_ROUTE} to get your authentication token...")
        webbrowser.open_new(USER_SECRETS_ROUTE)
        _token = click.prompt("Please enter your authentication token from the browser", hide_input=False)

    if not _token:
        msg = "Token must be provided via CODEGEN_USER_ACCESS_TOKEN environment variable or manual input"
        raise click.ClickException(msg)

    # Validate and store token
    token_manager = TokenManager()
    session = CodegenSession(_token)

    try:
        session.assert_authenticated()
        token_manager.save_token(_token)
        rich.print(f"[green]✓ Stored token to:[/green] {token_manager.token_file}")
        return session
    except AuthError as e:
        msg = f"Error: {e!s}"
        raise click.ClickException(msg)
