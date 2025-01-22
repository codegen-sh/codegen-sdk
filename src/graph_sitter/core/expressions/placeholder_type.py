from collections.abc import Generator
from typing import TYPE_CHECKING, Generic, Self, TypeVar, override

from graph_sitter.codebase.resolution_stack import ResolutionStack
from graph_sitter.core.autocommit import commiter
from graph_sitter.core.dataclasses.usage import UsageKind
from graph_sitter.core.expressions.type import Type
from graph_sitter.core.interfaces.editable import Editable
from graph_sitter.core.interfaces.importable import Importable
from graph_sitter.extensions.autocommit import reader
from graph_sitter.writer_decorators import apidoc, noapidoc

if TYPE_CHECKING:
    pass


TType = TypeVar("TType", bound="Type")
Parent = TypeVar("Parent", bound="Editable")


@apidoc
class PlaceholderType(Type[Parent], Generic[TType, Parent]):
    """Represents a type that has not been implemented yet."""

    @noapidoc
    @commiter
    def _compute_dependencies(self, usage_type: UsageKind, dest: Importable):
        self._add_all_identifier_usages(usage_type, dest=dest)

    @reader
    @noapidoc
    @override
    def _resolved_types(self) -> Generator[ResolutionStack[Self], None, None]:
        yield from []
