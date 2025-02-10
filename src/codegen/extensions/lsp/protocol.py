import os

from lsprotocol.types import INITIALIZE, InitializeParams, InitializeResult
from pygls.protocol import LanguageServerProtocol, lsp_method

from codegen.sdk.codebase.config import CodebaseConfig, GSFeatureFlags
from codegen.sdk.core.codebase import Codebase


class CodegenLanguageServerProtocol(LanguageServerProtocol):
    @lsp_method(INITIALIZE)
    def lsp_initialize(self, params: InitializeParams) -> InitializeResult:
        root = params.root_path or os.getcwd()
        config = CodebaseConfig(feature_flags=GSFeatureFlags(full_range_index=True))
        self._server.codebase = Codebase(repo_path=root, config=config)
        return super().lsp_initialize(params)
