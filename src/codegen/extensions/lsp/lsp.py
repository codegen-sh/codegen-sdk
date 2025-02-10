import logging

from lsprotocol import types

import codegen
from codegen.extensions.lsp.document_symbol import get_document_symbol
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


@server.feature(
    types.TEXT_DOCUMENT_DOCUMENT_SYMBOL,
)
def document_symbol(server: CodegenLanguageServer, params: types.DocumentSymbolParams) -> types.DocumentSymbolResult:
    file = server.get_file(params.text_document.uri)
    symbols = []
    for symbol in file.symbols:
        symbols.append(get_document_symbol(symbol))
    return symbols


get_document_symbol


@server.feature(
    types.TEXT_DOCUMENT_HOVER,
)
def hover(server: CodegenLanguageServer, params: types.HoverParams) -> types.HoverResponse:
    pass


@server.feature(
    types.TEXT_DOCUMENT_COMPLETION,
)
def completion(server: CodegenLanguageServer, params: types.CompletionParams):
    pass


@server.feature(
    types.TEXT_DOCUMENT_DEFINITION,
)
def definition(server: CodegenLanguageServer, params: types.DefinitionParams):
    pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    server.start_io()
