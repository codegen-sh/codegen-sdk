from collections.abc import Generator
from typing import TYPE_CHECKING, Generic, Self, TypeVar, override

from graph_sitter.codebase.resolution_stack import ResolutionStack
from graph_sitter.core.dataclasses.usage import UsageKind
from graph_sitter.core.expressions.type import Type
from graph_sitter.core.interfaces.editable import Editable
from graph_sitter.core.interfaces.importable import Importable
from graph_sitter.extensions.autocommit import reader
from graph_sitter.writer_decorators import apidoc, noapidoc

if TYPE_CHECKING:
    pass


Parent = TypeVar("Parent", bound="Editable")


@apidoc
class NoneType(Type[Parent], Generic[Parent]):
    """Represents a None or Null object."""

    @noapidoc
    def _compute_dependencies(self, usage_type: UsageKind, dest: Importable):
        pass

    @reader
    @noapidoc
    @override
    def _resolved_types(self) -> Generator[ResolutionStack[Self], None, None]:
        yield from []
