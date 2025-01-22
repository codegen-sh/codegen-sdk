from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

from tree_sitter import Node as TSNode

from codegen_sdk.codebase.codebase_graph import CodebaseGraph
from codegen_sdk.core.node_id_factory import NodeId
from codegen_sdk.core.symbol_groups.collection import Collection

if TYPE_CHECKING:
    from codegen_sdk.core.expressions.type import Type
    from codegen_sdk.core.interfaces.supports_generic import SupportsGenerics


TType = TypeVar("TType", bound="Type")
Parent = TypeVar("Parent", bound="SupportsGenerics")


class TypeParameters(Collection["TType", Parent], Generic[TType, Parent]):
    def __init__(self, ts_node: TSNode, file_node_id: NodeId, G: CodebaseGraph, parent: Parent) -> None:
        super().__init__(ts_node, file_node_id, G, parent)
        self._init_children([self._parse_type(child) for child in ts_node.named_children])
