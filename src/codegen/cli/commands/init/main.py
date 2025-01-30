import subprocess
import sys
from pathlib import Path

import rich
import rich_click as click

from codegen.cli.auth.constants import CODEGEN_DIR
from codegen.cli.auth.session import CodegenSession
from codegen.cli.commands.init.render import get_success_message
from codegen.cli.git.url import get_git_organization_and_repo
from codegen.cli.rich.codeblocks import format_command
from codegen.cli.workspace.initialize_workspace import initialize_codegen


@click.command(name="init")
@click.option("--repo-name", type=str, help="The name of the repository")
@click.option("--organization-name", type=str, help="The name of the organization")
@click.option("--fetch-docs", is_flag=True, help="Fetch docs and examples (requires auth)")
def init_command(repo_name: str | None = None, organization_name: str | None = None, fetch_docs: bool = False):
    """Initialize or update the Codegen folder."""
    # Print a message if not in a git repo
    try:
        subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], capture_output=True, check=True, text=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        rich.print("\n[bold red]Error:[/bold red] Not in a git repository")
        rich.print("[white]Please run this command from within a git repository.[/white]")
        rich.print("\n[dim]To initialize a new git repository:[/dim]")
        rich.print(format_command("git init"))
        rich.print(format_command("git remote add origin <your-repo-url>"))
        rich.print(format_command("codegen init"))
        sys.exit(1)

    # Only create session if we need to fetch docs
    session = CodegenSession() if fetch_docs else None
    codegen_dir = Path.cwd() / CODEGEN_DIR if not session else session.codegen_dir
    is_update = codegen_dir.exists()

    # Only update config if we have a session
    if session:
        if organization_name is not None:
            session.config.organization_name = organization_name
        if repo_name is not None:
            session.config.repo_name = repo_name
        if not session.config.organization_name or not session.config.repo_name:
            cwd_org, cwd_repo = get_git_organization_and_repo(session.git_repo)
            session.config.organization_name = session.config.organization_name or cwd_org
            session.config.repo_name = session.config.repo_name or cwd_repo
        session.write_config()

    action = "Updating" if is_update else "Initializing"
    rich.print("")  # Add a newline before the spinner
    codegen_dir, docs_dir, examples_dir = initialize_codegen(action, session=session, fetch_docs=fetch_docs)

    # Print success message
    rich.print(f"✅ {action} complete\n")
    rich.print(get_success_message(codegen_dir, docs_dir, examples_dir))

    # Print next steps
    rich.print("\n[bold]What's next?[/bold]\n")
    rich.print("1. Create a function:")
    rich.print(format_command('codegen create my-function -d "describe what you want to do"'))
    rich.print("2. Run it:")
    rich.print(format_command("codegen run my-function --apply-local"))
