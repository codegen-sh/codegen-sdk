from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar, override

from tree_sitter import Node as TSNode

from codegen_sdk.core.dataclasses.usage import UsageKind
from codegen_sdk.core.expressions import Expression
from codegen_sdk.core.interfaces.has_name import HasName
from codegen_sdk.core.node_id_factory import NodeId
from codegen_sdk.extensions.autocommit import commiter
from codegen_sdk.writer_decorators import apidoc, noapidoc

if TYPE_CHECKING:
    from codegen_sdk.codebase.codebase_graph import CodebaseGraph


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
