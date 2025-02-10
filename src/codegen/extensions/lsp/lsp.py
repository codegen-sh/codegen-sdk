import logging

from lsprotocol import types

import codegen
from codegen.extensions.lsp.document_symbol import get_document_symbol
from codegen.extensions.lsp.protocol import CodegenLanguageServerProtocol
from codegen.extensions.lsp.range import get_range
from codegen.extensions.lsp.server import CodegenLanguageServer
from codegen.sdk.core.assignment import Assignment
from codegen.sdk.core.detached_symbols.function_call import FunctionCall
from codegen.sdk.core.expressions.chained_attribute import ChainedAttribute
from codegen.sdk.core.expressions.expression import Expression
from codegen.sdk.core.expressions.name import Name
from codegen.sdk.core.interfaces.has_name import HasName

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
    node = server.get_node_under_cursor(params.text_document.uri, params.position)
    if node is None or not isinstance(node, (Expression)):
        logger.warning(f"No node found at {params.text_document.uri}:{params.position}")
        return None
    if isinstance(node, Name) and isinstance(node.parent, ChainedAttribute) and node.parent.attribute == node:
        node = node.parent
    if isinstance(node.parent, FunctionCall) and node.parent.get_name() == node:
        node = node.parent
    logger.info(f"Resolving definition for {node}")
    if isinstance(node, FunctionCall):
        resolved = node.function_definition
    else:
        resolved = node.resolved_value
    if resolved is None:
        logger.warning(f"No resolved value found for {node.name} at {params.text_document.uri}:{params.position}")
        return None
    if isinstance(resolved, (HasName,)):
        resolved = resolved.get_name()
    if isinstance(resolved.parent, Assignment) and resolved.parent.value == resolved:
        resolved = resolved.parent.get_name()
    return types.Location(
        uri=resolved.file.path.as_uri(),
        range=get_range(resolved),
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    server.start_io()
