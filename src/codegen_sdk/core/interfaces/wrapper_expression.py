from abc import abstractmethod
from collections.abc import Generator
from typing import TYPE_CHECKING, Self, final, override

from graph_sitter.codebase.resolution_stack import ResolutionStack
from graph_sitter.core.autocommit import reader
from graph_sitter.core.dataclasses.usage import UsageKind
from graph_sitter.core.expressions import Expression
from graph_sitter.core.interfaces.chainable import Chainable
from graph_sitter.core.interfaces.editable import Editable
from graph_sitter.core.interfaces.has_name import HasName
from graph_sitter.extensions.autocommit import commiter
from graph_sitter.writer_decorators import noapidoc

if TYPE_CHECKING:
    from graph_sitter.core.interfaces.importable import Importable


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
