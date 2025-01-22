from collections.abc import Generator
from typing import TYPE_CHECKING, Generic, Self, TypeVar, override

from graph_sitter.codebase.resolution_stack import ResolutionStack
from graph_sitter.core.autocommit import reader
from graph_sitter.core.dataclasses.usage import UsageKind
from graph_sitter.core.expressions.type import Type
from graph_sitter.core.interfaces.importable import Importable
from graph_sitter.core.node_id_factory import NodeId
from graph_sitter.writer_decorators import noapidoc, ts_apidoc
from tree_sitter import Node as TSNode

if TYPE_CHECKING:
    from graph_sitter.codebase.codebase_graph import CodebaseGraph
    from graph_sitter.typescript.expressions.type import TSType


Parent = TypeVar("Parent")


@ts_apidoc
class TSConditionalType(Type[Parent], Generic[Parent]):
    """Conditional Type

    Examples:
    typeof s
    """

    left: "TSType[Self]"
    right: "TSType[Self]"
    consequence: "TSType[Self]"
    alternative: "TSType[Self]"

    def __init__(self, ts_node: TSNode, file_node_id: NodeId, G: "CodebaseGraph", parent: Parent):
        super().__init__(ts_node, file_node_id, G, parent)
        self.left = self.child_by_field_name("left")
        self.right = self.child_by_field_name("right")
        self.consequence = self.child_by_field_name("consequence")
        self.alternative = self.child_by_field_name("alternative")

    def _compute_dependencies(self, usage_type: UsageKind, dest: Importable):
        self.left._compute_dependencies(usage_type, dest)
        self.right._compute_dependencies(usage_type, dest)
        self.consequence._compute_dependencies(usage_type, dest)
        self.alternative._compute_dependencies(usage_type, dest)

    @reader
    @noapidoc
    @override
    def _resolved_types(self) -> Generator[ResolutionStack[Self], None, None]:
        yield from self.with_resolution_frame(self.consequence)
        yield from self.with_resolution_frame(self.alternative)
