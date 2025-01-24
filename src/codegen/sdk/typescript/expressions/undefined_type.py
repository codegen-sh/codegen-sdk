from collections.abc import Generator
from typing import TYPE_CHECKING, Generic, Self, TypeVar, override

from codegen.sdk.codebase.resolution_stack import ResolutionStack
from codegen.sdk.core.dataclasses.usage import UsageKind
from codegen.sdk.core.expressions.type import Type
from codegen.sdk.core.interfaces.importable import Importable
from codegen.sdk.extensions.autocommit import reader
from codegen.shared.decorators.docs import noapidoc, ts_apidoc

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
