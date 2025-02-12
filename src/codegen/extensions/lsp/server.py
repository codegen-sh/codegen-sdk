import logging
from typing import Any, Optional

from lsprotocol.types import Position, Range
from pygls.lsp.server import LanguageServer

from codegen.extensions.lsp.io import LSPIO
from codegen.extensions.lsp.range import get_tree_sitter_range
from codegen.extensions.lsp.utils import get_path
from codegen.sdk.codebase.flagging.code_flag import Symbol
from codegen.sdk.core.codebase import Codebase
from codegen.sdk.core.file import File, SourceFile
from codegen.sdk.core.interfaces.editable import Editable

logger = logging.getLogger(__name__)


class CodegenLanguageServer(LanguageServer):
    codebase: Optional[Codebase]
    io: Optional[LSPIO]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def get_file(self, uri: str) -> SourceFile | File:
        path = get_path(uri)
        return self.codebase.get_file(str(path))

    def get_symbol(self, uri: str, position: Position) -> Symbol | None:
        node = self.get_node_under_cursor(uri, position)
        if node is None:
            return None
        return node.parent_symbol

    def get_node_under_cursor(self, uri: str, position: Position) -> Editable | None:
        file = self.get_file(uri)
        resolved_uri = file.path.absolute().as_uri()
        logger.info(f"Getting node under cursor for {resolved_uri} at {position}")
        document = self.workspace.get_text_document(resolved_uri)
        candidates = []
        target_byte = document.offset_at_position(position)
        for node in file._range_index.nodes:
            if node.start_byte <= target_byte and node.end_byte >= target_byte:
                candidates.append(node)
        if not candidates:
            return None
        return min(candidates, key=lambda node: abs(node.end_byte - node.start_byte))

    def get_node_for_range(self, uri: str, range: Range) -> Editable | None:
        file = self.get_file(uri)
        document = self.workspace.get_text_document(uri)
        ts_range = get_tree_sitter_range(range, document)
        for node in file._range_index.get_all_for_range(ts_range):
            return node
        return None
