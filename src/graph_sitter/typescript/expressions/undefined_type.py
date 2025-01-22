from collections.abc import Generator
from typing import TYPE_CHECKING, Generic, Self, TypeVar, override

from graph_sitter.codebase.resolution_stack import ResolutionStack
from graph_sitter.core.dataclasses.usage import UsageKind
from graph_sitter.core.expressions.type import Type
from graph_sitter.core.interfaces.importable import Importable
from graph_sitter.extensions.autocommit import reader
from graph_sitter.writer_decorators import noapidoc, ts_apidoc

if TYPE_CHECKING:
    pass


Parent = TypeVar("Parent")


@ts_apidoc
class TSUndefinedType(Type[Parent], Generic[Parent]):
    """Undefined type. Represents the undefined keyword
    Examples:
        undefined
    """

    @noapidoc
    def _compute_dependencies(self, usage_type: UsageKind, dest: Importable):
        pass

    @reader
    @noapidoc
    @override
    def _resolved_types(self) -> Generator[ResolutionStack[Self], None, None]:
        yield from []
