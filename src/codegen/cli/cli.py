import rich_click as click
from rich.traceback import install

from codegen.cli.commands.create.main import create_command
from codegen.cli.commands.deploy.main import deploy_command
from codegen.cli.commands.expert.main import expert_command
from codegen.cli.commands.init.main import init_command
from codegen.cli.commands.list.main import list_command
from codegen.cli.commands.login.main import login_command
from codegen.cli.commands.logout.main import logout_command
from codegen.cli.commands.notebook.main import notebook_command
from codegen.cli.commands.profile.main import profile_command
from codegen.cli.commands.reset.main import reset_command
from codegen.cli.commands.run.main import run_command
from codegen.cli.commands.run_on_pr.main import run_on_pr_command
from codegen.cli.commands.style_debug.main import style_debug_command
from codegen.cli.metrics.wrap_command import metrics_wrapper

click.rich_click.USE_RICH_MARKUP = True
install(show_locals=True)


@click.group()
@click.version_option(prog_name="codegen", message="%(version)s")
def main():
    """Codegen CLI - Transform your code with AI."""


# Wrap commands with error handler
main.add_command(metrics_wrapper(init_command))
main.add_command(metrics_wrapper(logout_command))
main.add_command(metrics_wrapper(login_command))
main.add_command(metrics_wrapper(run_command))
main.add_command(metrics_wrapper(profile_command))
main.add_command(metrics_wrapper(create_command))
main.add_command(metrics_wrapper(expert_command))
main.add_command(metrics_wrapper(list_command))
main.add_command(metrics_wrapper(deploy_command))
main.add_command(metrics_wrapper(style_debug_command))
main.add_command(metrics_wrapper(run_on_pr_command))
main.add_command(metrics_wrapper(notebook_command))
main.add_command(metrics_wrapper(reset_command))


if __name__ == "__main__":
    main()
