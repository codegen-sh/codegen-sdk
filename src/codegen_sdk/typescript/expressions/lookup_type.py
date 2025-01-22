from collections.abc import Generator
from typing import TYPE_CHECKING, Generic, Self, TypeVar, override

from graph_sitter.codebase.resolution_stack import ResolutionStack
from graph_sitter.core.autocommit import reader
from graph_sitter.core.dataclasses.usage import UsageKind
from graph_sitter.core.expressions import Expression
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
class TSLookupType(Type[Parent], Generic[Parent]):
    """Type lookup
    Examples:
        a["key"]
    """

    type: "TSType[Self]"
    lookup: Expression

    def __init__(self, ts_node: TSNode, file_node_id: NodeId, G: "CodebaseGraph", parent: Parent):
        super().__init__(ts_node, file_node_id, G, parent)
        self.type = self._parse_type(ts_node.named_children[0])
        if literal_type := self.child_by_field_types("literal_type"):
            self.lookup = self._parse_expression(literal_type.ts_node.named_children[0])

    @property
    @reader
    def name(self) -> str | None:
        """Retrieves the name of the type object.

        Gets the name property of the underlying type object. This property is commonly used to access type names in TypeScript-style type lookups.

        Returns:
            str | None: The name of the type object if it exists, None otherwise.
        """
        return self.type.name

    @reader
    @noapidoc
    @override
    def _resolved_types(self) -> Generator[ResolutionStack[Self], None, None]:
        # TODO: not implemented properly. Needs to look at the actual lookup
        self._log_parse("Cannot resolve lookup type properly")
        yield from self.with_resolution_frame(self.type)

    def _compute_dependencies(self, usage_type: UsageKind, dest: Importable):
        self.type._compute_dependencies(usage_type, dest)
