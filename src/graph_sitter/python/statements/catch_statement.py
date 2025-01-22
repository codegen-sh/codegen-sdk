from __future__ import annotations

from typing import TYPE_CHECKING

from tree_sitter import Node as PyNode

from graph_sitter.core.node_id_factory import NodeId
from graph_sitter.core.statements.catch_statement import CatchStatement
from graph_sitter.python.detached_symbols.code_block import PyCodeBlock
from graph_sitter.python.statements.block_statement import PyBlockStatement
from graph_sitter.writer_decorators import py_apidoc

if TYPE_CHECKING:
    from graph_sitter.codebase.codebase_graph import CodebaseGraph


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
