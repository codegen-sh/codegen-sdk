import os

from lsprotocol.types import INITIALIZE, InitializeParams, InitializeResult
from pygls.protocol import LanguageServerProtocol, lsp_method

from codegen.sdk.core.codebase import Codebase


class CodegenLanguageServerProtocol(LanguageServerProtocol):
    @lsp_method(INITIALIZE)
    def lsp_initialize(self, params: InitializeParams) -> InitializeResult:
        root = params.root_path or os.getcwd()
        self._server.codebase = Codebase(repo_path=root)
        return super().lsp_initialize(params)
