import logging

from lsprotocol import types

import codegen
from codegen.extensions.lsp.protocol import CodegenLanguageServerProtocol
from codegen.extensions.lsp.server import CodegenLanguageServer

version = getattr(codegen, "__version__", "v0.1")
server = CodegenLanguageServer("codegen", version, protocol_cls=CodegenLanguageServerProtocol)
logger = logging.getLogger(__name__)


@server.feature(
    types.TEXT_DOCUMENT_RENAME,
)
def rename(server: CodegenLanguageServer, params: types.RenameParams):
    symbol = server.get_symbol(params.text_document.uri, params.position)
    if symbol is None:
        logger.warning(f"No symbol found at {params.text_document.uri}:{params.position}")
        return
    logger.info(f"Renaming symbol {symbol.name} to {params.new_name}")
    symbol.rename(params.new_name)
    server.codebase.commit()


# @server.feature(
#     types.TEXT_DOCUMENT_RENAME,
# )
# def completions(params: types.CompletionParams):
#     document = server.workspace.get_document(params.text_document.uri)
#     current_line = document.lines[params.position.line].strip()

#     if not current_line.endswith("hello."):
#         return []

#     return [
#         types.CompletionItem(label="world"),
#         types.CompletionItem(label="friend"),
#     ]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    server.start_io()
