import logging
from typing import TYPE_CHECKING, Generic, Self, TypeVar, Union

from tree_sitter import Node as TSNode

from codegen.sdk.core.autocommit import reader
from codegen.sdk.core.dataclasses.usage import UsageType
from codegen.sdk.core.expressions.expression import Expression
from codegen.sdk.core.interfaces.has_name import HasName
from codegen.sdk.core.node_id_factory import NodeId
from codegen.sdk.enums import EdgeType
from codegen.sdk.extensions.autocommit import commiter
from codegen.sdk.extensions.sort import sort_editables
from codegen.shared.decorators.docs import apidoc, noapidoc

if TYPE_CHECKING:
    from codegen.sdk.codebase.codebase_graph import CodebaseGraph
    from codegen.sdk.core.import_resolution import Import
    from codegen.sdk.core.interfaces.editable import Editable
    from codegen.sdk.core.symbol import Symbol

Parent = TypeVar("Parent", bound="Editable")

logger = logging.getLogger(__name__)


@apidoc
class Importable(Expression[Parent], HasName, Generic[Parent]):
    """An interface for any node object that can import (or reference) an exportable symbol eg. All nodes that are on the graph must inherit from here

    Class, function, imports, exports, etc.
    """

    node_id: int

    def __init__(self, ts_node: TSNode, file_node_id: NodeId, G: "CodebaseGraph", parent: Parent) -> None:
        if not hasattr(self, "node_id"):
            self.node_id = G.add_node(self)
        super().__init__(ts_node, file_node_id, G, parent)
        if self.file:
            self.file._nodes.append(self)

    @property
    @reader(cache=False)
    def dependencies(self) -> list[Union["Symbol", "Import"]]:
        """Returns a list of symbols that this symbol depends on.

        Returns a list of symbols (including imports) that this symbol directly depends on.
        The returned list is sorted by file location for consistent ordering.

        Returns:
            list[Union[Symbol, Import]]: A list of symbols and imports that this symbol directly depends on,
                sorted by file location.
        """
        return self.get_dependencies(UsageType.DIRECT)

    @reader(cache=False)
    @noapidoc
    def get_dependencies(self, usage_types: UsageType) -> list[Union["Symbol", "Import"]]:
        """Returns Symbols and Importsthat this symbol depends on.

        Opposite of `usages`
        """
        avoid = set(self.descendant_symbols)
        deps = []
        for symbol in self.descendant_symbols:
            deps += filter(lambda x: x not in avoid, symbol._get_dependencies(usage_types))
        return sort_editables(deps, by_file=True)

    @reader(cache=False)
    @noapidoc
    def _get_dependencies(self, usage_types: UsageType) -> list[Union["Symbol", "Import"]]:
        """Symbols that this symbol depends on.

        Opposite of `usages`
        """
        # TODO: sort out attribute usages in dependencies
        edges = [x for x in self.G.out_edges(self.node_id) if x[2].type == EdgeType.SYMBOL_USAGE]
        unique_dependencies = []
        for edge in edges:
            if edge[2].usage.usage_type is None or edge[2].usage.usage_type in usage_types:
                dependency = self.G.get_node(edge[1])
                unique_dependencies.append(dependency)
        return sort_editables(unique_dependencies, by_file=True)

    @commiter
    @noapidoc
    def recompute(self, incremental: bool = False) -> list["Importable"]:
        """Recompute the dependencies of this symbol.

        Returns:
            A list of importables that need to be updated now this importable has been updated.
        """
        if incremental:
            self._remove_internal_edges(EdgeType.SYMBOL_USAGE)
        try:
            self._compute_dependencies()
        except Exception as e:
            logger.exception(f"Error in file {self.file.path} while computing dependencies for symbol {self.name}")
            raise e
        if incremental:
            return self.descendant_symbols + self.file.get_nodes(sort=False)
        return []

    @commiter
    @noapidoc
    def _remove_internal_edges(self, edge_type: EdgeType | None = None) -> None:
        """Removes edges from itself to its children from the codebase graph.

        Returns a list of node ids for edges that were removed.
        """
        # Must store edges to remove in a static read-only view before removing to avoid concurrent dict modification
        for v in self.G.successors(self.node_id, edge_type=edge_type):
            self.G.remove_edge(self.node_id, v.node_id, edge_type=edge_type)

    @property
    @noapidoc
    def descendant_symbols(self) -> list[Self]:
        return [self]
