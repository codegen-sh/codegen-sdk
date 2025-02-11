import os
import subprocess
import sys
from pathlib import Path

import rich
import rich_click as click

from codegen.cli.auth.session import CodegenSession
from codegen.cli.commands.init.render import get_success_message
from codegen.cli.rich.codeblocks import format_command
from codegen.cli.workspace.initialize_workspace import initialize_codegen
from codegen.git.repo_operator.local_git_repo import LocalGitRepo
from codegen.shared.configs.config import config
from codegen.shared.configs.constants import CODEGEN_DIR_NAME
from codegen.shared.enums.programming_language import ProgrammingLanguage


@click.command(name="init")
@click.option("--path", type=str, help="Path within a git repository. Defaults to the current directory.")
@click.option("--token", type=str, help="Access token for the git repository. Required for full functionality.")
@click.option("--language", type=click.Choice(["python", "typescript"], case_sensitive=False), help="Override automatic language detection")
@click.option("--fetch-docs", is_flag=True, help="Fetch docs and examples (requires auth)")
def init_command(path: str | None = None, token: str | None = None, language: str | None = None, fetch_docs: bool = False):
    """Initialize or update the Codegen folder."""
    # Print a message if not in a git repo
    path = str(Path.cwd()) if path is None else path
    try:
        os.chdir(path)
        output = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, check=True, text=True)
        local_git = LocalGitRepo(repo_path=output.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        rich.print(f"\n[bold red]Error:[/bold red] Path={path} is not in a git repository")
        rich.print("[white]Please run this command from within a git repository.[/white]")
        rich.print("\n[dim]To initialize a new git repository:[/dim]")
        rich.print(format_command("git init"))
        rich.print(format_command("git remote add origin <your-repo-url>"))
        rich.print(format_command("codegen init"))
        sys.exit(1)

    if token is None:
        token = config.secrets.github_token
    else:
        config.secrets.github_token = token

    if not token:
        rich.print("\n[bold yellow]Warning:[/bold yellow] GitHub token not found")
        rich.print("To enable full functionality, please set your GitHub token:")
        rich.print(format_command("export CODEGEN_SECRETS__GITHUB_TOKEN=<your-token>"))
        rich.print("Or pass in as a parameter:")
        rich.print(format_command("codegen init --token <your-token>"))

    # Save repo config
    config.repository.repo_path = local_git.repo_path
    config.repository.repo_name = local_git.name
    config.repository.full_name = local_git.full_name
    config.repository.user_name = local_git.user_name
    config.repository.user_email = local_git.user_email
    config.repository.language = ProgrammingLanguage(language or local_git.get_language(access_token=token).upper())
    config.save()

    session = CodegenSession()
    action = "Updating" if CODEGEN_DIR_NAME.exists() else "Initializing"
    rich.print("")
    codegen_dir, docs_dir, examples_dir = initialize_codegen(action, session=session, fetch_docs=fetch_docs, programming_language=config.repository.language)

    # Print success message
    rich.print(f"✅ {action} complete\n")
    rich.print(get_success_message(codegen_dir, docs_dir, examples_dir))

    # Print next steps
    rich.print("\n[bold]What's next?[/bold]\n")
    rich.print("1. Create a function:")
    rich.print(format_command('codegen create my-function -d "describe what you want to do"'))
    rich.print("2. Run it:")
    rich.print(format_command("codegen run my-function --apply-local"))
