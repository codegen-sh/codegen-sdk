import logging

import click

logger = logging.getLogger(__name__)


@click.command(name="lsp")
def lsp_command():
    try:
        from codegen.extensions.lsp.lsp import server
    except (ImportError, ModuleNotFoundError):
        logger.exception("LSP is not installed. Please install it with `uv tool install codegen[lsp] --prerelease=allow`")
        return
    logging.basicConfig(level=logging.INFO)
    server.start_io()
