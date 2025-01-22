import itertools
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

from graph_sitter.core.dataclasses.usage import UsageKind
from graph_sitter.core.expressions.expression import Expression
from graph_sitter.core.interfaces.chainable import Chainable
from graph_sitter.core.interfaces.editable import Editable
from graph_sitter.extensions.autocommit import reader
from graph_sitter.writer_decorators import apidoc, noapidoc
from typing_extensions import deprecated

if TYPE_CHECKING:
    from graph_sitter.core.interfaces.importable import Importable
    from graph_sitter.core.symbol import Symbol


Parent = TypeVar("Parent", bound="Editable")


@apidoc
class Type(Expression[Parent], Chainable, ABC, Generic[Parent]):
    """Abstract representation of a type
    Used to store the types of variables, parameters, or return values in functions, classes, etc.
    """

    @noapidoc
    @abstractmethod
    def _compute_dependencies(self, usage_type: UsageKind, dest: "Importable"): ...

    @property
    @deprecated("Use resolved_types instead for internal uses")
    @noapidoc
    @reader
    def resolved_symbol(self) -> "Symbol | str | None":
        from graph_sitter.core.symbol import Symbol

        for resolved in self.resolved_types:
            if isinstance(resolved, Symbol):
                return resolved
        return None

    @property
    @noapidoc
    def descendant_symbols(self) -> list["Importable"]:
        """Returns the nested symbols of the importable object, including itself."""
        return list(itertools.chain.from_iterable(child.descendant_symbols for child in self.children))
