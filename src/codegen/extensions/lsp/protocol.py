import os

from lsprotocol.types import INITIALIZE, InitializeParams, InitializeResult
from pygls.protocol import LanguageServerProtocol, lsp_method

from codegen.extensions.lsp.io import LSPIO
from codegen.sdk.codebase.config import CodebaseConfig, GSFeatureFlags
from codegen.sdk.core.codebase import Codebase


class CodegenLanguageServerProtocol(LanguageServerProtocol):
    @lsp_method(INITIALIZE)
    def lsp_initialize(self, params: InitializeParams) -> InitializeResult:
        root = params.root_path or os.getcwd()
        config = CodebaseConfig(feature_flags=GSFeatureFlags(full_range_index=True))
        ret = super().lsp_initialize(params)
        io = LSPIO(self.workspace)
        self._server.codebase = Codebase(repo_path=root, config=config, io=io)
        self._server.io = io
        return ret
