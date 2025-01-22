from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar, override

from tree_sitter import Node as TSNode

from graph_sitter.core.dataclasses.usage import UsageKind
from graph_sitter.core.expressions import Expression
from graph_sitter.core.interfaces.has_name import HasName
from graph_sitter.core.node_id_factory import NodeId
from graph_sitter.extensions.autocommit import commiter
from graph_sitter.writer_decorators import apidoc, noapidoc

if TYPE_CHECKING:
    from graph_sitter.codebase.codebase_graph import CodebaseGraph


Parent = TypeVar("Parent", bound="Expression")
TExpression = TypeVar("TExpression", bound="Expression")


@apidoc
class MultiExpression(Expression[Parent], Generic[Parent, TExpression]):
    """Represents an group of Expressions, such as List, Dict, Binary Expression, String."""

    expressions: list[TExpression]

    def __init__(self, ts_node: TSNode, file_node_id: NodeId, G: CodebaseGraph, parent: Parent, expressions: list[TExpression]) -> None:
        super().__init__(ts_node, file_node_id, G, parent)
        self.expressions = expressions

    @noapidoc
    @commiter
    @override
    def _compute_dependencies(self, usage_type: UsageKind | None = None, dest: HasName | None = None) -> None:
        for exp in self.expressions:
            exp._compute_dependencies(usage_type, dest)
