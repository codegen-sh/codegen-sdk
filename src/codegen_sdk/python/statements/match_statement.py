from __future__ import annotations

from typing import TYPE_CHECKING

from graph_sitter.core.node_id_factory import NodeId
from graph_sitter.core.statements.switch_statement import SwitchStatement
from graph_sitter.python.detached_symbols.code_block import PyCodeBlock
from graph_sitter.python.statements.match_case import PyMatchCase
from graph_sitter.writer_decorators import py_apidoc
from tree_sitter import Node as PyNode

if TYPE_CHECKING:
    from graph_sitter.codebase.codebase_graph import CodebaseGraph


@py_apidoc
class PyMatchStatement(SwitchStatement["PyCodeBlock", "PyCodeBlock", PyMatchCase]):
    """Abstract representation of the match block"""

    def __init__(self, ts_node: PyNode, file_node_id: NodeId, G: CodebaseGraph, parent: PyCodeBlock, pos: int | None = None) -> None:
        super().__init__(ts_node, file_node_id, G, parent, pos)
        self.value = self.child_by_field_name("subject")
        code_block = self.ts_node.child_by_field_name("body")
        self.cases = []
        for node in code_block.children_by_field_name("alternative"):
            self.cases.append(PyMatchCase(node, file_node_id, G, self.parent, self.index))
