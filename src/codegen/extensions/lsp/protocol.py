import os
import threading
from pathlib import Path
from typing import TYPE_CHECKING

from lsprotocol.types import INITIALIZE, INITIALIZED, InitializedParams, InitializeParams, InitializeResult
from pygls.protocol import LanguageServerProtocol, lsp_method

from codegen.extensions.lsp.io import LSPIO
from codegen.extensions.lsp.utils import get_path
from codegen.sdk.codebase.config import CodebaseConfig
from codegen.sdk.core.codebase import Codebase
from codegen.shared.configs.models import CodebaseFeatureFlags

if TYPE_CHECKING:
    from codegen.extensions.lsp.server import CodegenLanguageServer


class CodegenLanguageServerProtocol(LanguageServerProtocol):
    _server: "CodegenLanguageServer"

    def _init_codebase(self, params: InitializeParams) -> None:
        if params.root_path:
            root = Path(params.root_path)
        elif params.root_uri:
            root = get_path(params.root_uri)
        else:
            root = os.getcwd()
        config = CodebaseConfig(feature_flags=CodebaseFeatureFlags(full_range_index=True))
        io = LSPIO(self.workspace)
        self._server.codebase = Codebase(repo_path=str(root), config=config, io=io)
        self._server.io = io

    @lsp_method(INITIALIZE)
    def lsp_initialize(self, params: InitializeParams) -> InitializeResult:
        if params.root_path:
            root = Path(params.root_path)
        elif params.root_uri:
            root = get_path(params.root_uri)
        else:
            root = os.getcwd()
        config = CodebaseConfig(feature_flags=CodebaseFeatureFlags(full_range_index=True))
        ret = super().lsp_initialize(params)

        self._worker = threading.Thread(target=self._init_codebase, args=(params,))
        self._worker.start()
        return ret

    @lsp_method(INITIALIZED)
    def lsp_initialized(self, params: InitializedParams) -> None:
        self._worker.join()
        super().lsp_initialized(params)
