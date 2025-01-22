from typing import TYPE_CHECKING

from tree_sitter import Node as TSNode

from codegen_sdk.core.node_id_factory import NodeId
from codegen_sdk.core.statements.switch_case import SwitchCase
from codegen_sdk.typescript.detached_symbols.code_block import TSCodeBlock
from codegen_sdk.typescript.statements.block_statement import TSBlockStatement
from codegen_sdk.writer_decorators import ts_apidoc

if TYPE_CHECKING:
    from codegen_sdk.codebase.codebase_graph import CodebaseGraph


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
