from pathlib import Path

import rich
from rich.panel import Panel

from codegen import Codebase
from codegen.cli.auth.session import CodegenSession
from codegen.cli.git.patch import apply_patch
from codegen.cli.rich.codeblocks import format_command
from codegen.cli.rich.spinners import create_spinner
from codegen.cli.utils.function_finder import DecoratedFunction


def run_local(
    session: CodegenSession,
    function: DecoratedFunction,
    apply_local: bool = False,
    diff_preview: int | None = None,
) -> None:
    """Run a function locally against the codebase.

    Args:
        session: The current codegen session
        function: The function to run (either a DecoratedFunction or Codemod)
        apply_local: Whether to apply changes to the local filesystem
        diff_preview: Number of lines of diff to preview (None for all)
    """
    # Initialize codebase from git repo root
    repo_root = Path(session.git_repo.workdir)

    with create_spinner("Parsing codebase...") as status:
        codebase = Codebase(repo_root)

    try:
        # Run the function
        rich.print(f"Running {function.name} locally...")
        result = function.run(codebase)

        if not result:
            rich.print("\n[yellow]No changes were produced by this codemod[/yellow]")
            return

        # Show diff preview if requested
        if diff_preview:
            rich.print("")  # Add spacing
            diff_lines = result.splitlines()
            truncated = len(diff_lines) > diff_preview
            limited_diff = "\n".join(diff_lines[:diff_preview])

            if truncated:
                if apply_local:
                    limited_diff += f"\n\n...\n\n[yellow]diff truncated to {diff_preview} lines, view the full change set in your local file system[/yellow]"
                else:
                    limited_diff += f"\n\n...\n\n[yellow]diff truncated to {diff_preview} lines, view the full change set by running with --apply-local[/yellow]"

            panel = Panel(limited_diff, title="[bold]Diff Preview[/bold]", border_style="blue", padding=(1, 2), expand=False)
            rich.print(panel)

        # Apply changes if requested
        if apply_local:
            try:
                apply_patch(session.git_repo, f"\n{result}\n")
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
                raise RuntimeError("Failed to apply patch to local filesystem") from e
        else:
            rich.print("")
            rich.print("To apply these changes locally:")
            rich.print(format_command(f"codegen run {function.name} --apply-local"))

    except Exception as e:
        rich.print(f"[red]Error running {function.name}:[/red] {e!s}")
        raise
