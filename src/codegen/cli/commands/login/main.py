import sys

import rich
import rich_click as click

from codegen.cli.auth.auth_session import CodegenAuthenticatedSession
from codegen.cli.auth.login import login_routine
from codegen.cli.auth.token_manager import TokenManager, get_current_token


@click.command(name="login")
@click.option("--token", required=False, help="API token for authentication")
def login_command(token: str):
    """Store authentication token."""
    # Check if already authenticated
    if get_current_token():
        msg = "Already authenticated. Use 'codegen logout' to clear the token."
        raise click.ClickException(msg)

    if not token:
        login_routine()
        sys.exit(1)

    # Use provided token or go through login flow
    token_manager = TokenManager()
    session = CodegenAuthenticatedSession(token=token)
    try:
        session.assert_authenticated()
        token_manager.save_token(token)
        rich.print(f"[green]✓ Stored token to:[/green] {token_manager.token_file}")
        rich.print("[cyan]📊 Hey![/cyan] We collect anonymous usage data to improve your experience 🔒")
        rich.print("To opt out, set [green]telemetry_enabled = false[/green] in [cyan]~/.config/codegen-sh/analytics.json[/cyan] ✨")
    except ValueError as e:
        msg = f"Error: {e!s}"
        raise click.ClickException(msg)
