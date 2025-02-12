import os
from pathlib import Path
from typing import TYPE_CHECKING

from lsprotocol.types import INITIALIZE, InitializeParams, InitializeResult, WorkDoneProgressBegin, WorkDoneProgressEnd
from pygls.protocol import LanguageServerProtocol, lsp_method

from codegen.extensions.lsp.io import LSPIO
from codegen.extensions.lsp.utils import get_path
from codegen.sdk.codebase.config import CodebaseConfig
from codegen.sdk.core.codebase import Codebase
from codegen.shared.configs.models.feature_flags import CodebaseFeatureFlags

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
        if params.work_done_token:
            self._server.work_done_progress.end(params.work_done_token, WorkDoneProgressEnd(message="Parsing codebase..."))

    @lsp_method(INITIALIZE)
    def lsp_initialize(self, params: InitializeParams) -> InitializeResult:
        ret = super().lsp_initialize(params)
        if params.work_done_token:
            self._server.work_done_progress.create(params.work_done_token, WorkDoneProgressBegin(title="Parsing codebase..."))
        self._init_codebase(params)
        return ret
