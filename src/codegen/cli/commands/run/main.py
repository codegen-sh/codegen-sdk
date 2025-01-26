import json

import rich
import rich_click as click

from codegen.cli.auth.session import CodegenSession
from codegen.cli.utils.codemod_manager import CodemodManager
from codegen.cli.utils.json_schema import validate_json
from codegen.cli.workspace.decorators import requires_init


@click.command(name="run")
@requires_init
@click.argument("label", required=True)
@click.option("--web", is_flag=True, help="Run the function on the web service instead of locally")
@click.option("--apply-local", is_flag=True, help="Applies the generated diff to the repository")
@click.option("--diff-preview", type=int, help="Show a preview of the first N lines of the diff")
@click.option("--arguments", type=str, help="Arguments as a json string to pass as the function's 'arguments' parameter")
def run_command(
    session: CodegenSession,
    label: str,
    web: bool = False,
    apply_local: bool = False,
    diff_preview: int | None = None,
    arguments: str | None = None,
):
    """Run a codegen function by its label."""
    # First try to find it as a stored codemod
    codemod = CodemodManager.get(label)
    if codemod:
        if codemod.arguments_type_schema and not arguments:
            raise click.ClickException(f"This function requires the --arguments parameter. Expected schema: {codemod.arguments_type_schema}")

        if codemod.arguments_type_schema and arguments:
            arguments_json = json.loads(arguments)
            is_valid = validate_json(codemod.arguments_type_schema, arguments_json)
            if not is_valid:
                raise click.ClickException(f"Invalid arguments format. Expected schema: {codemod.arguments_type_schema}")

        if web:
            from codegen.cli.commands.run.run_cloud import run_cloud

            run_cloud(session, codemod, apply_local=apply_local, diff_preview=diff_preview)
        else:
            from codegen.cli.commands.run.run_local import run_local

            run_local(session, codemod, apply_local=apply_local, diff_preview=diff_preview)
        return

    # If not found as a stored codemod, look for decorated functions
    functions = CodemodManager.get_decorated()
    matching = [f for f in functions if f.name == label]

    if not matching:
        raise click.ClickException(f"No function found with label '{label}'")

    if len(matching) > 1:
        # If multiple matches, show their locations
        rich.print(f"[yellow]Multiple functions found with label '{label}':[/yellow]")
        for func in matching:
            rich.print(f"  • {func.filepath}")
        raise click.ClickException("Please specify the exact file with codegen run <path>")

    if web:
        from codegen.cli.commands.run.run_cloud import run_cloud

        run_cloud(session, matching[0], apply_local=apply_local, diff_preview=diff_preview)
    else:
        from codegen.cli.commands.run.run_local import run_local

        run_local(session, matching[0], apply_local=apply_local, diff_preview=diff_preview)
