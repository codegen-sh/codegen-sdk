from collections.abc import Generator
from typing import TYPE_CHECKING, Generic, Self, TypeVar, override

from codegen_sdk.codebase.resolution_stack import ResolutionStack
from codegen_sdk.core.dataclasses.usage import UsageKind
from codegen_sdk.core.expressions.type import Type
from codegen_sdk.core.interfaces.editable import Editable
from codegen_sdk.core.interfaces.importable import Importable
from codegen_sdk.extensions.autocommit import reader
from codegen_sdk.writer_decorators import apidoc, noapidoc

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
