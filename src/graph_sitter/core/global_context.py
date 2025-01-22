from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from graph_sitter.codebase.config import DefaultConfig, GraphSitterConfig
from graph_sitter.codebase.multigraph import MultiGraph
from graph_sitter.core.plugins import PLUGINS

if TYPE_CHECKING:
    from graph_sitter.core.codebase import Codebase
    from graph_sitter.core.function import Function


@dataclass
class GlobalContext[TFunction: Function]:
    multigraph: MultiGraph[TFunction] = field(default_factory=MultiGraph)
    config: GraphSitterConfig = DefaultConfig

    def execute_plugins(self, codebase: "Codebase"):
        for plugin in PLUGINS:
            plugin.execute(codebase)
