from pathlib import Path
from typing import Any, Optional

from lsprotocol.types import Position
from pygls.lsp.server import LanguageServer

from codegen.sdk.codebase.flagging.code_flag import Symbol
from codegen.sdk.core.codebase import Codebase
from codegen.sdk.core.file import File, SourceFile


class CodegenLanguageServer(LanguageServer):
    codebase: Optional[Codebase]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def get_file(self, uri: str) -> SourceFile | File:
        path = Path(uri)
        return self.codebase.get_file(path.name)

    def get_symbol(self, uri: str, position: Position) -> Symbol | None:
        file = self.get_file(uri)
        line = position.line
        char = position.character
        for symbol in file.symbols:
            if symbol.start_point.row >= line and symbol.start_point.column >= char:
                return symbol
        return None
