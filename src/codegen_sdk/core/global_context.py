from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from codegen_sdk.codebase.config import DefaultConfig, GraphSitterConfig
from codegen_sdk.codebase.multigraph import MultiGraph
from codegen_sdk.core.plugins import PLUGINS

if TYPE_CHECKING:
    from codegen_sdk.core.codebase import Codebase
    from codegen_sdk.core.function import Function


@dataclass
class GlobalContext[TFunction: Function]:
    multigraph: MultiGraph[TFunction] = field(default_factory=MultiGraph)
    config: GraphSitterConfig = DefaultConfig

    def execute_plugins(self, codebase: "Codebase"):
        for plugin in PLUGINS:
            plugin.execute(codebase)
