from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

from graph_sitter.core.node_id_factory import NodeId
from graph_sitter.core.statements.catch_statement import CatchStatement
from graph_sitter.typescript.detached_symbols.code_block import TSCodeBlock
from graph_sitter.typescript.statements.block_statement import TSBlockStatement
from graph_sitter.writer_decorators import apidoc
from tree_sitter import Node as TSNode

if TYPE_CHECKING:
    from graph_sitter.codebase.codebase_graph import CodebaseGraph


Parent = TypeVar("Parent", bound="TSCodeBlock")


@apidoc
class TSCatchStatement(CatchStatement[Parent], TSBlockStatement, Generic[Parent]):
    """Typescript catch clause.

    Attributes:
        code_block: The code block that may trigger an exception
        condition: The condition which triggers this clause
    """

    def __init__(self, ts_node: TSNode, file_node_id: NodeId, G: CodebaseGraph, parent: Parent, pos: int | None = None) -> None:
        super().__init__(ts_node, file_node_id, G, parent, pos)
        self.condition = self.child_by_field_name("parameter")
