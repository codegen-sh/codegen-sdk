import logging

import click

from codegen.extensions.lsp.lsp import server


@click.command(name="lsp")
def lsp_command():
    logging.basicConfig(level=logging.INFO)
    server.start_io()
