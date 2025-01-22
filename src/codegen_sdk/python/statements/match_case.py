from typing import TYPE_CHECKING

from graph_sitter.core.node_id_factory import NodeId
from graph_sitter.core.statements.switch_case import SwitchCase
from graph_sitter.python.detached_symbols.code_block import PyCodeBlock
from graph_sitter.python.statements.block_statement import PyBlockStatement
from graph_sitter.writer_decorators import py_apidoc
from tree_sitter import Node as PyNode

if TYPE_CHECKING:
    from graph_sitter.codebase.codebase_graph import CodebaseGraph


@py_apidoc
class PyMatchCase(SwitchCase[PyCodeBlock["PyMatchStatement"]], PyBlockStatement):
    """Python match case."""

    def __init__(self, ts_node: PyNode, file_node_id: NodeId, G: "CodebaseGraph", parent: PyCodeBlock, pos: int | None = None) -> None:
        super().__init__(ts_node, file_node_id, G, parent, pos)
        self.condition = self.child_by_field_name("alternative")
