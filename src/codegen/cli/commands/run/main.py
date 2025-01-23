import json
import webbrowser

import rich
import rich_click as click
from rich.panel import Panel

from codegen.cli.api.client import RestAPI
from codegen.cli.auth.decorators import requires_auth
from codegen.cli.auth.session import CodegenSession
from codegen.cli.errors import ServerError
from codegen.cli.git.patch import apply_patch
from codegen.cli.rich.codeblocks import format_command
from codegen.cli.rich.spinners import create_spinner
from codegen.cli.utils.codemod_manager import CodemodManager
from codegen.cli.utils.json_schema import validate_json
from codegen.cli.utils.url import generate_webapp_url
from codegen.cli.workspace.decorators import requires_init


def run_function(session: CodegenSession, function, web: bool = False, apply_local: bool = False, diff_preview: int | None = None):
    """Run a function and handle its output."""
    with create_spinner(f"Running {function.name}...") as status:
        try:
            run_output = RestAPI(session.token).run(
                function=function,
            )

            status.stop()
            rich.print(f"✅ Ran {function.name} successfully")
            if run_output.web_link:
                # Extract the run ID from the web link
                run_id = run_output.web_link.split("/run/")[1].split("/")[0]
                function_id = run_output.web_link.split("/codemod/")[1].split("/")[0]

                rich.print("   [dim]Web viewer:[/dim] [blue underline]" + run_output.web_link + "[/blue underline]")
                run_details_url = generate_webapp_url(f"functions/{function_id}/run/{run_id}")
                rich.print(f"   [dim]Run details:[/dim] [blue underline]{run_details_url}[/blue underline]")

            if run_output.logs:
                rich.print("")
                panel = Panel(run_output.logs, title="[bold]Logs[/bold]", border_style="blue", padding=(1, 2), expand=False)
                rich.print(panel)

            if run_output.error:
                rich.print("")
                panel = Panel(run_output.error, title="[bold]Error[/bold]", border_style="red", padding=(1, 2), expand=False)
                rich.print(panel)

            if run_output.observation:
                # Only show diff preview if requested
                if diff_preview:
                    rich.print("")  # Add some spacing

                    # Split and limit diff to requested number of lines
                    diff_lines = run_output.observation.splitlines()
                    truncated = len(diff_lines) > diff_preview
                    limited_diff = "\n".join(diff_lines[:diff_preview])

                    if truncated:
                        if apply_local:
                            limited_diff += "\n\n...\n\n[yellow]diff truncated to {diff_preview} lines, view the full change set in your local file system[/yellow]"
                        else:
                            limited_diff += (
                                "\n\n...\n\n[yellow]diff truncated to {diff_preview} lines, view the full change set on your local file system after using run with `--apply-local`[/yellow]"
                            )

                    panel = Panel(limited_diff, title="[bold]Diff Preview[/bold]", border_style="blue", padding=(1, 2), expand=False)
                    rich.print(panel)

                if not apply_local:
                    rich.print("")
                    rich.print("Apply changes locally:")
                    rich.print(format_command(f"codegen run {function.name} --apply-local"))
                    rich.print("Create a PR:")
                    rich.print(format_command(f"codegen run {function.name} --create-pr"))
            else:
                rich.print("")
                rich.print("[yellow] No changes were produced by this codemod[/yellow]")

            if web and run_output.web_link:
                webbrowser.open_new(run_output.web_link)

            if apply_local and run_output.observation:
                try:
                    apply_patch(session.git_repo, f"\n{run_output.observation}\n")
                    rich.print("")
                    rich.print("[green]✓ Changes have been applied to your local filesystem[/green]")
                    rich.print("[yellow]→ Don't forget to commit your changes:[/yellow]")
                    rich.print(format_command("git add ."))
                    rich.print(format_command("git commit -m 'Applied codemod changes'"))
                except Exception as e:
                    rich.print("")
                    rich.print("[red]✗ Failed to apply changes locally[/red]")
                    rich.print("\n[yellow]This usually happens when you have uncommitted changes.[/yellow]")
                    rich.print("\nOption 1 - Save your changes:")
                    rich.print("  1. [blue]git status[/blue]        (check your working directory)")
                    rich.print("  2. [blue]git add .[/blue]         (stage your changes)")
                    rich.print("  3. [blue]git commit -m 'msg'[/blue]  (commit your changes)")
                    rich.print("  4. Run this command again")
                    rich.print("\nOption 2 - Discard your changes:")
                    rich.print("  1. [red]git reset --hard HEAD[/red]     (⚠️ discards all uncommitted changes)")
                    rich.print("  2. [red]git clean -fd[/red]            (⚠️ removes all untracked files)")
                    rich.print("  3. Run this command again\n")
                    raise click.ClickException("Failed to apply patch to local filesystem")

        except ServerError as e:
            status.stop()
            raise click.ClickException(str(e))


@click.command(name="run")
@requires_auth
@requires_init
@click.argument("label", required=True)
@click.option("--web", is_flag=True, help="Automatically open the diff in the web app")
@click.option("--apply-local", is_flag=True, help="Applies the generated diff to the repository")
@click.option("--diff-preview", type=int, help="Show a preview of the first N lines of the diff")
@click.option("--arguments", type=str, help="Arguments as a json string to pass as the function's 'arguments' parameter")
def run_command(session: CodegenSession, label: str, web: bool = False, apply_local: bool = False, diff_preview: int | None = None, arguments: str | None = None):
    """Run a codegen function by its label."""
    # First try to find it as a stored codemod
    codemod = CodemodManager.get(label)
    if codemod:
        if codemod.arguments_type_schema and not arguments:
            raise click.ClickException(f"This function requires the --arguments parameter. Expected schema: {codemod.arguments_type_schema}")

        if codemod.arguments_type_schema and arguments:
            arguments_json = json.loads(arguments)
            is_valid = validate_json(codemod.arguments_type_schema, arguments_json)
            print(f"is_valid: {is_valid}")

        run_function(session, codemod, web, apply_local, diff_preview)
        return

    # If not found as a stored codemod, look for decorated functions
    functions = CodemodManager.get_decorated()
    print("found some functions", functions)
    matching = [f for f in functions if f.name == label]

    if not matching:
        raise click.ClickException(f"No function found with label '{label}'")

    if len(matching) > 1:
        # If multiple matches, show their locations
        rich.print(f"[yellow]Multiple functions found with label '{label}':[/yellow]")
        for func in matching:
            rich.print(f"  • {func.filepath}")
        raise click.ClickException("Please specify the exact file with codegen run <path>")

    run_function(session, matching[0], web, apply_local, diff_preview)
