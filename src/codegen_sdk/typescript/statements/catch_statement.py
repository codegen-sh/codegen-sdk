from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

from tree_sitter import Node as TSNode

from codegen_sdk.core.node_id_factory import NodeId
from codegen_sdk.core.statements.catch_statement import CatchStatement
from codegen_sdk.typescript.detached_symbols.code_block import TSCodeBlock
from codegen_sdk.typescript.statements.block_statement import TSBlockStatement
from codegen_sdk.writer_decorators import apidoc

if TYPE_CHECKING:
    from codegen_sdk.codebase.codebase_graph import CodebaseGraph


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
