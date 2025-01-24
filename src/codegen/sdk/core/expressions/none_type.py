from collections.abc import Generator
from typing import Generic, Self, TypeVar, override

from codegen.sdk.codebase.resolution_stack import ResolutionStack
from codegen.sdk.core.dataclasses.usage import UsageKind
from codegen.sdk.core.expressions.type import Type
from codegen.sdk.core.interfaces.editable import Editable
from codegen.sdk.core.interfaces.importable import Importable
from codegen.sdk.extensions.autocommit import reader
from codegen.shared.decorators.docs import apidoc, noapidoc

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
