from abc import abstractmethod
from collections.abc import Generator
from typing import TYPE_CHECKING, Generic, Self, TypeVar, override

from tree_sitter import Node as TSNode

from graph_sitter.core.autocommit import commiter, reader
from graph_sitter.core.dataclasses.usage import UsageKind
from graph_sitter.core.expressions.named_type import NamedType
from graph_sitter.core.expressions.type import Type
from graph_sitter.core.interfaces.editable import Editable
from graph_sitter.core.interfaces.importable import Importable
from graph_sitter.core.node_id_factory import NodeId
from graph_sitter.core.symbol_groups.collection import Collection
from graph_sitter.extensions.resolution import ResolutionStack
from graph_sitter.writer_decorators import apidoc, noapidoc

if TYPE_CHECKING:
    from graph_sitter.codebase.codebase_graph import CodebaseGraph
    from graph_sitter.core.interfaces.importable import Importable

Parent = TypeVar("Parent")


TType = TypeVar("TType", bound="Type")
Parent = TypeVar("Parent", bound="Editable")


@apidoc
class GenericType(NamedType[Parent], Generic[TType, Parent]):
    """Abstract representation of the generic types of the programming language."""

    _parameters: Collection[TType, Self]

    def __init__(self, ts_node: TSNode, file_node_id: NodeId, G: "CodebaseGraph", parent: Parent):
        super().__init__(ts_node, file_node_id, G, parent)
        self._parameters = self._get_parameters()

    @property
    @reader
    def parameters(self) -> Collection[TType, Self]:
        """Retrieves the generic type parameters associated with this type.

        Args:
            None

        Returns:
            Collection[TType, Self]: A collection of generic type parameters associated with this type.
        """
        return self._parameters

    @abstractmethod
    def _get_parameters(self) -> Collection[TType, Self]:
        pass

    @noapidoc
    @commiter
    def _compute_dependencies(self, usage_type: UsageKind, dest: Importable):
        super()._compute_dependencies(usage_type, dest)
        for param in self._parameters:
            param._compute_dependencies(UsageKind.GENERIC, dest)

    @property
    @noapidoc
    def descendant_symbols(self) -> list["Importable"]:
        """Returns the nested symbols of the importable object, including itself."""
        ret = self.get_name().descendant_symbols
        for param in self._parameters:
            ret.extend(param.descendant_symbols)
        return ret

    @reader
    @noapidoc
    @override
    def _resolved_types(self) -> Generator[ResolutionStack[Self], None, None]:
        if name := self.get_name():
            yield from self.with_resolution_frame(name, generic_parameters=self.parameters)
