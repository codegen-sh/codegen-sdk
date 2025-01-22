from collections.abc import Generator
from typing import TYPE_CHECKING, Generic, Self, TypeVar, override

from tree_sitter import Node as TSNode

from graph_sitter.codebase.resolution_stack import ResolutionStack
from graph_sitter.core.autocommit import reader
from graph_sitter.core.dataclasses.usage import UsageKind
from graph_sitter.core.expressions.type import Type
from graph_sitter.core.interfaces.importable import Importable
from graph_sitter.core.node_id_factory import NodeId
from graph_sitter.writer_decorators import noapidoc, ts_apidoc

if TYPE_CHECKING:
    from graph_sitter.codebase.codebase_graph import CodebaseGraph
    from graph_sitter.typescript.expressions.type import TSType


Parent = TypeVar("Parent")


@ts_apidoc
class TSQueryType(Type[Parent], Generic[Parent]):
    """Type query

    Examples:
    typeof s
    """

    query: "TSType[Self]"

    def __init__(self, ts_node: TSNode, file_node_id: NodeId, G: "CodebaseGraph", parent: Parent):
        super().__init__(ts_node, file_node_id, G, parent)
        self.query = self._parse_type(ts_node.named_children[0])

    @property
    @reader
    def name(self) -> str | None:
        """Returns the name of the query type.

        A property that retrieves the name of the query type. This property is used to get the name
        associated with TypeScript type queries (e.g., 'typeof s').

        Returns:
            str | None: The name of the query type, or None if no name is available.
        """
        return self.query.name

    def _compute_dependencies(self, usage_type: UsageKind, dest: Importable):
        self.query._compute_dependencies(usage_type, dest)

    @reader
    @noapidoc
    @override
    def _resolved_types(self) -> Generator[ResolutionStack[Self], None, None]:
        yield from self.with_resolution_frame(self.query)
