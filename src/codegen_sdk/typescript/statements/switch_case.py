from typing import TYPE_CHECKING

from graph_sitter.core.node_id_factory import NodeId
from graph_sitter.core.statements.switch_case import SwitchCase
from graph_sitter.typescript.detached_symbols.code_block import TSCodeBlock
from graph_sitter.typescript.statements.block_statement import TSBlockStatement
from graph_sitter.writer_decorators import ts_apidoc
from tree_sitter import Node as TSNode

if TYPE_CHECKING:
    from graph_sitter.codebase.codebase_graph import CodebaseGraph


@ts_apidoc
class TSSwitchCase(SwitchCase[TSCodeBlock["TSSwitchStatement"]], TSBlockStatement):
    """Typescript switch case.

    Attributes:
        default: is this a default case?
    """

    default: bool

    def __init__(self, ts_node: TSNode, file_node_id: NodeId, G: "CodebaseGraph", parent: TSCodeBlock, pos: int | None = None) -> None:
        super().__init__(ts_node, file_node_id, G, parent, pos)
        self.condition = self.child_by_field_name("value")
        self.default = self.ts_node.type == "switch_default"
