from typing import TYPE_CHECKING

from tree_sitter import Node as PyNode

from codegen_sdk.core.node_id_factory import NodeId
from codegen_sdk.core.statements.switch_case import SwitchCase
from codegen_sdk.python.detached_symbols.code_block import PyCodeBlock
from codegen_sdk.python.statements.block_statement import PyBlockStatement
from codegen_sdk.writer_decorators import py_apidoc

if TYPE_CHECKING:
    from codegen_sdk.codebase.codebase_graph import CodebaseGraph


@py_apidoc
class PyMatchCase(SwitchCase[PyCodeBlock["PyMatchStatement"]], PyBlockStatement):
    """Python match case."""

    def __init__(self, ts_node: PyNode, file_node_id: NodeId, G: "CodebaseGraph", parent: PyCodeBlock, pos: int | None = None) -> None:
        super().__init__(ts_node, file_node_id, G, parent, pos)
        self.condition = self.child_by_field_name("alternative")
