from collections.abc import Generator
from typing import TYPE_CHECKING, Generic, Self, TypeVar, override

from codegen_sdk.codebase.resolution_stack import ResolutionStack
from codegen_sdk.core.autocommit import commiter
from codegen_sdk.core.dataclasses.usage import UsageKind
from codegen_sdk.core.expressions.type import Type
from codegen_sdk.core.interfaces.editable import Editable
from codegen_sdk.core.interfaces.importable import Importable
from codegen_sdk.extensions.autocommit import reader
from codegen_sdk.writer_decorators import apidoc, noapidoc

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
