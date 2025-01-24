import rich
import rich_click as click
from rich import box
from rich.panel import Panel

from codegen.cli.auth.decorators import requires_auth
from codegen.cli.auth.session import CodegenSession
from codegen.cli.workspace.decorators import requires_init


@click.command(name="profile")
@requires_auth
@requires_init
def profile_command(session: CodegenSession):
    """Display information about the currently authenticated user."""
    rich.print(
        Panel(
            f"[cyan]Name:[/cyan]  {session.profile.name}\n[cyan]Email:[/cyan] {session.profile.email}\n[cyan]Repo:[/cyan]  {session.repo_name}",
            title="🔑 [bold]Current Profile[/bold]",
            border_style="cyan",
            box=box.ROUNDED,
            padding=(1, 2),
        )
    )
