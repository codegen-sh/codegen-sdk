from abc import abstractmethod
from collections.abc import Generator
from typing import TYPE_CHECKING, Self, final, override

from codegen_sdk.codebase.resolution_stack import ResolutionStack
from codegen_sdk.core.autocommit import reader
from codegen_sdk.core.dataclasses.usage import UsageKind
from codegen_sdk.core.expressions import Expression
from codegen_sdk.core.interfaces.chainable import Chainable
from codegen_sdk.core.interfaces.editable import Editable
from codegen_sdk.core.interfaces.has_name import HasName
from codegen_sdk.extensions.autocommit import commiter
from codegen_sdk.writer_decorators import noapidoc

if TYPE_CHECKING:
    from codegen_sdk.core.interfaces.importable import Importable


class IWrapper(Chainable, Editable):
    """Any expression or statement that contains another expression.

    This is a simple interface to unwrap the nested expression.
    """

    @property
    @abstractmethod
    @reader
    def value(self) -> Expression | None:
        """The value of the object."""

    @reader
    @final
    def resolve(self) -> Expression:
        """Resolves the wrapper expression and returns the first concrete expression."""
        cur_val = self.value
        while cur_val and isinstance(cur_val, IWrapper):
            cur_val = cur_val.value
        return cur_val

    @reader
    @noapidoc
    @override
    def _resolved_types(self) -> Generator[ResolutionStack[Self], None, None]:
        yield from self.with_resolution_frame(self.value)

    @noapidoc
    @commiter
    def _compute_dependencies(self, usage_type: UsageKind = UsageKind.BODY, dest: HasName | None = None) -> None:
        if self._value_node:
            self.resolve()._compute_dependencies(usage_type, dest)

    @property
    @noapidoc
    def descendent_symbols(self) -> list["Importable"]:
        return self.resolve().descendant_symbols
