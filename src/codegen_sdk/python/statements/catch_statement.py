from __future__ import annotations

from typing import TYPE_CHECKING

from tree_sitter import Node as PyNode

from codegen_sdk.core.node_id_factory import NodeId
from codegen_sdk.core.statements.catch_statement import CatchStatement
from codegen_sdk.python.detached_symbols.code_block import PyCodeBlock
from codegen_sdk.python.statements.block_statement import PyBlockStatement
from codegen_sdk.writer_decorators import py_apidoc

if TYPE_CHECKING:
    from codegen_sdk.codebase.codebase_graph import CodebaseGraph


@py_apidoc
class PyCatchStatement(CatchStatement[PyCodeBlock], PyBlockStatement):
    """Python catch clause.

    Attributes:
        code_block: The code block that may trigger an exception
        condition: The condition which triggers this clause
    """

    def __init__(self, ts_node: PyNode, file_node_id: NodeId, G: CodebaseGraph, parent: PyCodeBlock, pos: int | None = None) -> None:
        super().__init__(ts_node, file_node_id, G, parent, pos)
        self.condition = self.children[0]
